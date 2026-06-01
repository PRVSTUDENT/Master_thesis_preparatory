#!/usr/bin/env python3
"""Stage 15K exact restart/reinjection verification.

Gate 2 test:
- direct path: ramp + cycles 1..100
- restarted path: ramp + cycles 1..50, JSON save/load of complete state,
  then cycles 51..100

Both paths use real NEML ``update_sd`` with explicit prior-state arguments.
No cycle jumping is performed here.
"""

from __future__ import print_function

import csv
import json
import math
import os
import platform
import sys
from pathlib import Path

import numpy as np
import neml
from neml import elasticity, hardening, models, ri_flow, surfaces


CASE_NAME = "B1_stress_m150_to_250"
OUT_DIR = Path("restart_verification")
LOGICAL_REPORT = OUT_DIR / "STAGE15K_RESTART_REINJECTION_REPORT.md"
ERRORS_CSV = OUT_DIR / "STAGE15K_RESTART_REINJECTION_ERRORS.csv"
DIRECT_JSON = OUT_DIR / "direct_100_cycle_state.json"
RESTARTED_JSON = OUT_DIR / "restarted_100_cycle_state.json"
SAVED_50_JSON = OUT_DIR / "restart_saved_50_cycle_state.json"

PARAMS = {
    "name": "P2_three_backstress_screen",
    "E": 200000.0,
    "nu": 0.3,
    "yield_stress": 100.0,
    "Q": 50.0,
    "b": 5.0,
    "C": [80000.0, 14000.0, 3333.0],
    "gamma": [900.0, 1500.0, 1.0],
    "A": [0.0, 0.0, 0.0],
    "a": [1.0, 1.0, 1.0],
}

STRESS_MIN = -150.0
STRESS_MAX = 250.0
POINTS_PER_CYCLE = 40
TEMPERATURE = 293.15
STRESS_RATE = 1.0e-4
STRICT_ABS_TOL = 1.0e-8
STRICT_REL_TOL = 1.0e-8
ROUND_TOL = 1.0e-10
RELAXED_TOL = 1.0e-6
NEWTON_TOL = 1.0e-10
MAX_NEWTON = 30


class MaterialState(object):
    def __init__(self, strain, stress, history, temperature, time, u, p, cycle, step_index):
        self.strain = np.array(strain, dtype=float)
        self.stress = np.array(stress, dtype=float)
        self.history = np.array(history, dtype=float)
        self.temperature = float(temperature)
        self.time = float(time)
        self.u = float(u)
        self.p = float(p)
        self.cycle = int(cycle)
        self.step_index = int(step_index)

    def copy(self):
        return MaterialState(
            self.strain.copy(),
            self.stress.copy(),
            self.history.copy(),
            self.temperature,
            self.time,
            self.u,
            self.p,
            self.cycle,
            self.step_index,
        )

    def to_dict(self, names):
        alpha, backstress_norm = history_metrics(self.history, names)
        return {
            "case_name": CASE_NAME,
            "parameter_set": PARAMS["name"],
            "cycle": self.cycle,
            "step_index": self.step_index,
            "temperature": self.temperature,
            "time": self.time,
            "strain": self.strain.tolist(),
            "stress": self.stress.tolist(),
            "history": self.history.tolist(),
            "history_names": list(names),
            "accumulated_inelastic_strain": alpha,
            "backstress_norm": backstress_norm,
            "energy_u": self.u,
            "plastic_dissipation_or_work_p": self.p,
            "neml_path": getattr(neml, "__file__", ""),
            "python": sys.version.replace("\n", " "),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["strain"],
            data["stress"],
            data["history"],
            data["temperature"],
            data["time"],
            data["energy_u"],
            data["plastic_dissipation_or_work_p"],
            data["cycle"],
            data["step_index"],
        )


def build_model():
    elastic = elasticity.IsotropicLinearElasticModel(PARAMS["E"], "youngs", PARAMS["nu"], "poissons")
    surface = surfaces.IsoKinJ2()
    iso = hardening.VoceIsotropicHardeningRule(PARAMS["yield_stress"], PARAMS["Q"], PARAMS["b"])
    gmodels = [hardening.ConstantGamma(g) for g in PARAMS["gamma"]]
    hmodel = hardening.Chaboche(iso, PARAMS["C"], gmodels, PARAMS["A"], PARAMS["a"])
    flow = ri_flow.RateIndependentNonAssociativeHardening(surface, hmodel)
    return models.SmallStrainRateIndependentPlasticity(elastic, flow)


def internal_names(model):
    return list(model.report_internal_variable_names())


def initial_state(model):
    return MaterialState(
        strain=np.zeros(6),
        stress=np.zeros(6),
        history=np.array(model.init_store(), dtype=float),
        temperature=TEMPERATURE,
        time=0.0,
        u=0.0,
        p=0.0,
        cycle=0,
        step_index=0,
    )


def history_metrics(history, names):
    values = {}
    for i, name in enumerate(names):
        if i < len(history):
            values[name] = float(history[i])
    alpha = values.get("alpha", float("nan"))
    backstress = [value for key, value in values.items() if key.startswith("backstress_")]
    backstress_norm = math.sqrt(sum(value * value for value in backstress)) if backstress else float("nan")
    return alpha, backstress_norm


def assert_finite_state(state, label):
    arrays = [("strain", state.strain), ("stress", state.stress), ("history", state.history)]
    for name, arr in arrays:
        if not np.all(np.isfinite(arr)):
            raise RuntimeError("%s has non-finite values in %s" % (label, name))
    for name, value in [
        ("temperature", state.temperature),
        ("time", state.time),
        ("energy_u", state.u),
        ("plastic_dissipation_or_work_p", state.p),
    ]:
        if not math.isfinite(float(value)):
            raise RuntimeError("%s has non-finite %s" % (label, name))


def update_trial(model, prev, strain_np1, t_np1):
    stress, history, tangent, u, p = model.update_sd(
        np.array(strain_np1, dtype=float),
        prev.strain,
        prev.temperature,
        prev.temperature,
        float(t_np1),
        prev.time,
        prev.stress,
        prev.history,
        prev.u,
        prev.p,
    )
    return np.array(stress, dtype=float), np.array(history, dtype=float), np.array(tangent, dtype=float), float(u), float(p)


def solve_stress_step(model, prev, target_s11, cycle, step_index):
    """Find strain[0:3] giving uniaxial stress [target, 0, 0]."""
    t_np1 = prev.time + abs(float(target_s11) - float(prev.stress[0])) / STRESS_RATE
    if t_np1 <= prev.time:
        t_np1 = prev.time + 1.0

    target = np.array([target_s11, 0.0, 0.0], dtype=float)
    unknown = prev.strain[:3].copy()
    # Isotropic elastic predictor for the axial component.
    unknown[0] += (float(target_s11) - float(prev.stress[0])) / PARAMS["E"]

    best = None
    for _ in range(MAX_NEWTON):
        trial_strain = np.zeros(6)
        trial_strain[:3] = unknown
        stress, history, tangent, u, p = update_trial(model, prev, trial_strain, t_np1)
        residual = stress[:3] - target
        norm = float(np.linalg.norm(residual, ord=np.inf))
        best = (trial_strain, stress, history, tangent, u, p, norm)
        if norm <= NEWTON_TOL:
            break
        jac = tangent[:3, :3]
        try:
            delta = np.linalg.solve(jac, -residual)
        except np.linalg.LinAlgError:
            delta = np.linalg.lstsq(jac, -residual, rcond=None)[0]
        accepted = False
        for scale in [1.0, 0.5, 0.25, 0.125, 0.0625]:
            candidate = unknown + scale * delta
            cand_strain = np.zeros(6)
            cand_strain[:3] = candidate
            cand_stress, cand_history, cand_tangent, cand_u, cand_p = update_trial(model, prev, cand_strain, t_np1)
            cand_norm = float(np.linalg.norm(cand_stress[:3] - target, ord=np.inf))
            if cand_norm < norm:
                unknown = candidate
                best = (cand_strain, cand_stress, cand_history, cand_tangent, cand_u, cand_p, cand_norm)
                accepted = True
                break
        if not accepted:
            unknown = unknown + delta

    trial_strain, stress, history, _, u, p, norm = best
    if norm > 1.0e-6:
        raise RuntimeError("Stress solve failed at cycle %d step %d: residual %.6e" % (cycle, step_index, norm))
    state = MaterialState(trial_strain, stress, history, prev.temperature, t_np1, u, p, cycle, step_index)
    assert_finite_state(state, "cycle %d step %d" % (cycle, step_index))
    return state


def stress_targets_for_cycle():
    half_steps = max(2, POINTS_PER_CYCLE // 2)
    targets = []
    for i in range(1, half_steps + 1):
        targets.append(STRESS_MAX + (STRESS_MIN - STRESS_MAX) * i / float(half_steps))
    for i in range(1, half_steps + 1):
        targets.append(STRESS_MIN + (STRESS_MAX - STRESS_MIN) * i / float(half_steps))
    return targets


def ramp_to_stress_max(model, state):
    half_steps = max(2, POINTS_PER_CYCLE // 2)
    for i in range(1, half_steps + 1):
        target = STRESS_MAX * i / float(half_steps)
        state = solve_stress_step(model, state, target, 0, i)
    return state


def run_cycles(model, start_state, start_cycle, end_cycle):
    state = start_state.copy()
    targets = stress_targets_for_cycle()
    for cycle in range(start_cycle + 1, end_cycle + 1):
        for local_step, target in enumerate(targets, start=1):
            state = solve_stress_step(model, state, target, cycle, local_step)
    return state


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def max_abs_rel(a, b):
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    diff = np.abs(aa - bb)
    denom = np.maximum(np.maximum(np.abs(aa), np.abs(bb)), 1.0)
    rel = diff / denom
    return float(np.max(diff)) if diff.size else 0.0, float(np.max(rel)) if rel.size else 0.0


def compare_states(direct, restarted, names):
    direct_alpha, direct_backstress = history_metrics(direct.history, names)
    restarted_alpha, restarted_backstress = history_metrics(restarted.history, names)
    components = [
        ("stress", direct.stress, restarted.stress),
        ("strain", direct.strain, restarted.strain),
        ("history_internal_variables", direct.history, restarted.history),
        ("accumulated_inelastic_strain", [direct_alpha], [restarted_alpha]),
        ("backstress_norm", [direct_backstress], [restarted_backstress]),
        ("time", [direct.time], [restarted.time]),
        ("energy_u", [direct.u], [restarted.u]),
        ("plastic_dissipation_or_work_p", [direct.p], [restarted.p]),
    ]
    rows = []
    for component, direct_value, restarted_value in components:
        max_abs, max_rel = max_abs_rel(direct_value, restarted_value)
        rows.append({
            "component": component,
            "max_abs_error": "%.17e" % max_abs,
            "max_rel_error": "%.17e" % max_rel,
            "strict_abs_tol": "%.1e" % STRICT_ABS_TOL,
            "strict_rel_tol": "%.1e" % STRICT_REL_TOL,
            "relaxed_diagnostic_tol": "%.1e" % RELAXED_TOL,
            "near_roundoff_tol": "%.1e" % ROUND_TOL,
            "strict_pass": str(max_abs <= STRICT_ABS_TOL or max_rel <= STRICT_REL_TOL).lower(),
            "relaxed_pass": str(max_abs <= RELAXED_TOL or max_rel <= RELAXED_TOL).lower(),
        })
    return rows


def write_errors_csv(rows):
    fieldnames = [
        "component",
        "max_abs_error",
        "max_rel_error",
        "strict_abs_tol",
        "strict_rel_tol",
        "relaxed_diagnostic_tol",
        "near_roundoff_tol",
        "strict_pass",
        "relaxed_pass",
    ]
    with ERRORS_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(rows, pass_gate, direct, restarted, names, reloaded_matches_saved):
    direct_alpha, direct_backstress = history_metrics(direct.history, names)
    restarted_alpha, restarted_backstress = history_metrics(restarted.history, names)
    lines = [
        "# Stage 15K Restart/Reinjection Verification Report",
        "",
        "## Gate",
        "- Gate: `2 exact restart/reinjection verification`",
        "- Status: **%s**" % ("PASS" if pass_gate else "FAIL"),
        "- `restart_reinjection_pass`: `%s`" % str(bool(pass_gate)).lower(),
        "",
        "## Environment",
        "- Real NEML backend used: `true`",
        "- NEML path: `%s`" % getattr(neml, "__file__", ""),
        "- Python executable: `%s`" % sys.executable,
        "- Python version: `%s`" % sys.version.replace("\n", " "),
        "- Platform: `%s`" % platform.platform(),
        "",
        "## Test Definition",
        "- Direct run: ramp to 250 MPa, then cycles `1 -> 100`.",
        "- Restarted run: ramp to 250 MPa, cycles `1 -> 50`, save complete state, reload complete state, continue cycles `51 -> 100`.",
        "- Case: `%s`" % CASE_NAME,
        "- Material: `%s`" % PARAMS["name"],
        "- Stress range: `%g` to `%g` MPa" % (STRESS_MIN, STRESS_MAX),
        "- Points per cycle: `%d`" % POINTS_PER_CYCLE,
        "- Update API: real NEML `SmallStrainRateIndependentPlasticity.update_sd` with explicit prior strain, stress, history, temperature, time, `u`, and `p`.",
        "",
        "## Saved State",
        "- Cycle-50 JSON reload reproduced saved state before continuation: `%s`" % str(bool(reloaded_matches_saved)).lower(),
        "- Saved restart state: `%s`" % SAVED_50_JSON.as_posix(),
        "",
        "## Final State Metrics",
        "| Quantity | Direct cycle 100 | Restarted cycle 100 |",
        "|---|---:|---:|",
        "| stress_11 | %.17e | %.17e |" % (direct.stress[0], restarted.stress[0]),
        "| strain_11 | %.17e | %.17e |" % (direct.strain[0], restarted.strain[0]),
        "| accumulated inelastic strain | %.17e | %.17e |" % (direct_alpha, restarted_alpha),
        "| backstress norm | %.17e | %.17e |" % (direct_backstress, restarted_backstress),
        "| energy u | %.17e | %.17e |" % (direct.u, restarted.u),
        "| plastic dissipation/work p | %.17e | %.17e |" % (direct.p, restarted.p),
        "",
        "## Error Summary",
        "| Component | Max abs error | Max rel error | Strict pass | Relaxed pass |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (row["component"], row["max_abs_error"], row["max_rel_error"], row["strict_pass"], row["relaxed_pass"])
        )
    lines.extend([
        "",
        "## Acceptance",
        "- Strict absolute tolerance: `%.1e`" % STRICT_ABS_TOL,
        "- Strict relative tolerance: `%.1e`" % STRICT_REL_TOL,
        "- Near-roundoff diagnostic tolerance: `%.1e`" % ROUND_TOL,
        "- Relaxed diagnostic tolerance: `%.1e`" % RELAXED_TOL,
        "- No NaN/inf appeared: `true`",
        "",
        "## Stop/Go Decision",
    ])
    if pass_gate:
        lines.append("**GO TO GATE 3 ONLY.** Gate 2 passed; fixed `Delta N` state-jump smoke testing may be prepared next. Do not run adaptive/full PBS yet.")
    else:
        lines.append("**STOP.** Restart/reinjection did not reproduce the direct cycle-100 state closely enough. Do not run fixed/adaptive jumps.")
    LOGICAL_REPORT.write_text("\n".join(lines) + "\n")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = build_model()
    names = internal_names(model)

    direct = run_cycles(model, ramp_to_stress_max(model, initial_state(model)), 0, 100)
    direct.cycle = 100

    restart_model = build_model()
    restart_names = internal_names(restart_model)
    if restart_names != names:
        raise RuntimeError("Internal variable names differ between model instances")
    state_50 = run_cycles(restart_model, ramp_to_stress_max(restart_model, initial_state(restart_model)), 0, 50)
    state_50.cycle = 50
    write_json(SAVED_50_JSON, state_50.to_dict(names))

    reloaded_50 = MaterialState.from_dict(json.loads(SAVED_50_JSON.read_text()))
    reload_rows = compare_states(state_50, reloaded_50, names)
    reloaded_matches_saved = all(row["strict_pass"] == "true" for row in reload_rows)
    restarted = run_cycles(restart_model, reloaded_50, 50, 100)
    restarted.cycle = 100

    assert_finite_state(direct, "direct cycle 100")
    assert_finite_state(restarted, "restarted cycle 100")

    write_json(DIRECT_JSON, direct.to_dict(names))
    write_json(RESTARTED_JSON, restarted.to_dict(names))
    rows = compare_states(direct, restarted, names)
    write_errors_csv(rows)
    pass_gate = reloaded_matches_saved and all(row["strict_pass"] == "true" for row in rows)
    write_report(rows, pass_gate, direct, restarted, names, reloaded_matches_saved)

    print("Wrote %s" % LOGICAL_REPORT)
    print("Wrote %s" % ERRORS_CSV)
    print("Wrote %s" % DIRECT_JSON)
    print("Wrote %s" % RESTARTED_JSON)
    print("restart_reinjection_pass=%s" % str(bool(pass_gate)).lower())
    return 0 if pass_gate else 1


if __name__ == "__main__":
    sys.exit(main())
