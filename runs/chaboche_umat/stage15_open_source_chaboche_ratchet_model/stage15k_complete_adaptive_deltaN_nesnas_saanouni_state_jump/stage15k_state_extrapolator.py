#!/usr/bin/env python3
"""Shared Stage 15K real-NEML state-jump utilities."""

from __future__ import print_function

import csv
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
import neml
from neml import drivers, elasticity, hardening, models, ri_flow, surfaces


CASE_NAME = "B1_stress_m150_to_250"
STRESS_MIN = -150.0
STRESS_MAX = 250.0
POINTS_PER_CYCLE = 40
TEMPERATURE = 293.15
STRESS_RATE = 1.0e-4
BASELINE = Path("../stage15g_real_neml_long_b1_validation_baseline/case_outputs/B1_long_cycle_summary.csv")

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

DERIVATIVE_METHODS = ["last_2", "last_5", "last_10", "least_squares_last_20", "least_squares_last_50"]
SUMMARY_FIELDS = [
    "case_name", "route_type", "base_cycle", "requested_target_cycle", "jump_target_cycle",
    "deltaN_requested", "deltaN_used", "derivative_method", "limiting_variable",
    "comparison_cycle", "reference_cycle", "reference_exact", "continuation_cycles",
    "strain_mean", "reference_strain_mean", "mean_strain_norm_error",
    "ratcheting_strain", "reference_ratcheting_strain", "ratcheting_norm_error",
    "accumulated_inelastic_strain", "reference_accumulated_inelastic_strain", "accumulated_inelastic_norm_error",
    "backstress_norm", "reference_backstress_norm", "backstress_norm_error",
    "drift_direction_correct", "strict_accepted", "relaxed_2pct_accepted", "relaxed_5pct_accepted",
    "real_neml_backend", "full_state_reinjected", "nan_or_inf", "status",
]


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


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


def new_driver():
    model = build_model()
    return model, internal_names(model), drivers.Driver_sd(model, T_init=TEMPERATURE)


def float_or_nan(value):
    try:
        return float(value)
    except Exception:
        return float("nan")


def trapz(xs, ys):
    area = 0.0
    for i in range(1, len(xs)):
        area += 0.5 * (ys[i] + ys[i - 1]) * (xs[i] - xs[i - 1])
    return area


def history_metrics(history, names):
    values = {name: float(history[i]) for i, name in enumerate(names) if i < len(history)}
    alpha = values.get("alpha", float("nan"))
    backstress = [value for key, value in values.items() if key.startswith("backstress_")]
    norm = math.sqrt(sum(value * value for value in backstress)) if backstress else float("nan")
    return alpha, norm


def state_vector_from_snapshot(snapshot):
    values = []
    names = []
    for key in ["stress", "strain", "history"]:
        arr = snapshot[key]
        for i, value in enumerate(arr):
            names.append("%s_%d" % (key, i))
            values.append(float(value))
    for key in ["time", "temperature", "energy_u", "plastic_work_p"]:
        names.append(key)
        values.append(float(snapshot[key]))
    return names, np.array(values, dtype=float)


def snapshot_from_vector(template, vector):
    vector = np.array(vector, dtype=float)
    n_stress = len(template["stress"])
    n_strain = len(template["strain"])
    n_hist = len(template["history"])
    pos = 0
    out = dict(template)
    out["stress"] = vector[pos:pos + n_stress].tolist()
    pos += n_stress
    out["strain"] = vector[pos:pos + n_strain].tolist()
    pos += n_strain
    out["history"] = vector[pos:pos + n_hist].tolist()
    pos += n_hist
    out["time"] = float(vector[pos])
    pos += 1
    out["temperature"] = float(vector[pos])
    pos += 1
    out["energy_u"] = float(vector[pos])
    pos += 1
    out["plastic_work_p"] = float(vector[pos])
    return out


def driver_snapshot(driver, names, cycle, first_mean=None, last_metrics=None):
    history = np.array(driver.stored_int[-1], dtype=float)
    alpha, backstress_norm = history_metrics(history, names)
    metrics = last_metrics or {}
    return {
        "cycle": int(cycle),
        "stress": np.array(driver.stress_int[-1], dtype=float).tolist(),
        "strain": np.array(driver.strain_int[-1], dtype=float).tolist(),
        "history": history.tolist(),
        "temperature": float(driver.T_int[-1]) if hasattr(driver, "T_int") else TEMPERATURE,
        "time": float(driver.t_int[-1]) if hasattr(driver, "t_int") else float(cycle),
        "energy_u": float(driver.u_int[-1]) if hasattr(driver, "u_int") else 0.0,
        "plastic_work_p": float(driver.p_int[-1]) if hasattr(driver, "p_int") else 0.0,
        "accumulated_inelastic_strain": alpha,
        "backstress_norm": backstress_norm,
        "strain_mean": float_or_nan(metrics.get("strain_mean")),
        "ratcheting_strain": float_or_nan(metrics.get("ratcheting_strain")),
        "strain_min": float_or_nan(metrics.get("strain_min")),
        "strain_max": float_or_nan(metrics.get("strain_max")),
        "first_mean": first_mean,
        "neml_path": getattr(neml, "__file__", ""),
    }


def restore_driver(driver, snapshot):
    mapping = [
        ("stress_int", "stress"),
        ("strain_int", "strain"),
        ("stored_int", "history"),
        ("mechanical_strain_int", "strain"),
    ]
    for attr, key in mapping:
        if hasattr(driver, attr):
            setattr(driver, attr, [np.array(snapshot[key], dtype=float)])
    scalar_mapping = [
        ("t_int", "time"),
        ("T_int", "temperature"),
        ("u_int", "energy_u"),
        ("p_int", "plastic_work_p"),
    ]
    for attr, key in scalar_mapping:
        if hasattr(driver, attr):
            setattr(driver, attr, [float(snapshot[key])])

    # Keep ndarray mirrors coherent for NEML driver routines that read them.
    mirror_arrays = [
        ("stress", "stress"),
        ("strain", "strain"),
        ("stored", "history"),
        ("history", "history"),
        ("mechanical_strain", "strain"),
    ]
    for attr, key in mirror_arrays:
        if hasattr(driver, attr):
            try:
                setattr(driver, attr, np.array([snapshot[key]], dtype=float))
            except AttributeError:
                pass
    for attr, key in [("t", "time"), ("T", "temperature"), ("u", "energy_u"), ("p", "plastic_work_p")]:
        if hasattr(driver, attr):
            try:
                setattr(driver, attr, np.array([float(snapshot[key])], dtype=float))
            except AttributeError:
                pass


def has_nonfinite_snapshot(snapshot):
    for key in ["stress", "strain", "history"]:
        if not np.all(np.isfinite(np.array(snapshot[key], dtype=float))):
            return True
    for key in ["time", "temperature", "energy_u", "plastic_work_p"]:
        if not math.isfinite(float(snapshot[key])):
            return True
    return False


def ramp_to_stress_max(driver):
    sdir = np.array([1.0, 0, 0, 0, 0, 0])
    half_steps = max(2, POINTS_PER_CYCLE // 2)
    inc = STRESS_MAX / float(half_steps)
    for _ in range(half_steps):
        driver.srate_sinc_step(sdir, STRESS_RATE, inc, TEMPERATURE)


def run_one_cycle(driver, cycle, first_mean):
    sdir = np.array([1.0, 0, 0, 0, 0, 0])
    half_steps = max(2, POINTS_PER_CYCLE // 2)
    strains = []
    stresses = []
    for inc in [(STRESS_MIN - STRESS_MAX) / float(half_steps), (STRESS_MAX - STRESS_MIN) / float(half_steps)]:
        for _ in range(half_steps):
            driver.srate_sinc_step(sdir, STRESS_RATE, inc, TEMPERATURE)
            stresses.append(float(np.dot(driver.stress_int[-1], sdir)))
            strains.append(float(np.dot(driver.strain_int[-1], sdir)))
    strain_min = min(strains)
    strain_max = max(strains)
    strain_mean = 0.5 * (strain_min + strain_max)
    if first_mean is None:
        first_mean = strain_mean
    return first_mean, {
        "case_name": CASE_NAME,
        "cycle": int(cycle),
        "stress_min": min(stresses),
        "stress_max": max(stresses),
        "strain_min": strain_min,
        "strain_max": strain_max,
        "strain_mean": strain_mean,
        "strain_range": strain_max - strain_min,
        "ratcheting_strain": strain_mean - first_mean,
        "hysteresis_area": trapz(strains, stresses),
    }


def run_to_cycle(target_cycle, keep_window=60):
    model, names, driver = new_driver()
    ramp_to_stress_max(driver)
    snapshots = deque(maxlen=max(keep_window, 2))
    first_mean = None
    last_metrics = None
    for cycle in range(1, int(target_cycle) + 1):
        first_mean, last_metrics = run_one_cycle(driver, cycle, first_mean)
        snapshots.append(driver_snapshot(driver, names, cycle, first_mean, last_metrics))
    return model, names, driver, list(snapshots), first_mean, last_metrics


def continue_from_snapshot(snapshot, target_cycle, compare_offsets):
    _, names, driver = new_driver()
    restore_driver(driver, snapshot)
    first_mean = snapshot.get("first_mean")
    current_cycle = int(snapshot["cycle"])
    max_cycle = int(max([target_cycle] + [target_cycle + offset for offset in compare_offsets]))
    wanted = set([int(target_cycle + offset) for offset in compare_offsets] + [int(target_cycle)])
    out = {}
    last_metrics = None
    for cycle in range(current_cycle + 1, max_cycle + 1):
        first_mean, last_metrics = run_one_cycle(driver, cycle, first_mean)
        if cycle in wanted:
            out[cycle] = driver_snapshot(driver, names, cycle, first_mean, last_metrics)
    if int(target_cycle) in wanted and int(target_cycle) not in out:
        out[int(target_cycle)] = snapshot
    return out


def derivative_from_window(snapshots, method):
    if method.startswith("last_"):
        n = int(method.split("_")[1])
        window = snapshots[-n:]
        x0, v0 = state_vector_from_snapshot(window[0])
        _, v1 = state_vector_from_snapshot(window[-1])
        denom = float(window[-1]["cycle"] - window[0]["cycle"])
        return x0, (v1 - v0) / max(denom, 1.0)
    if method.startswith("least_squares_last_"):
        n = int(method.split("_")[-1])
        window = snapshots[-n:]
        cycles = np.array([row["cycle"] for row in window], dtype=float)
        base = cycles - cycles.mean()
        denom = float(np.dot(base, base))
        names, _ = state_vector_from_snapshot(window[-1])
        values = np.array([state_vector_from_snapshot(row)[1] for row in window], dtype=float)
        slope = (base[:, None] * values).sum(axis=0) / max(denom, 1.0)
        return names, slope
    raise ValueError("unknown derivative method %s" % method)


def extrapolate_snapshot(snapshots, target_cycle, method):
    base = snapshots[-1]
    names, base_vec = state_vector_from_snapshot(base)
    deriv_names, slope = derivative_from_window(snapshots, method)
    if deriv_names != names:
        raise RuntimeError("state vector names changed")
    delta = float(target_cycle - base["cycle"])
    pred = snapshot_from_vector(base, base_vec + delta * slope)
    pred["cycle"] = int(target_cycle)
    pred["first_mean"] = base.get("first_mean")
    alpha, norm = history_metrics(np.array(pred["history"], dtype=float), infer_history_names(len(pred["history"])))
    pred["accumulated_inelastic_strain"] = alpha
    pred["backstress_norm"] = norm
    metric_keys = ["strain_mean", "ratcheting_strain", "strain_max", "strain_min"]
    delta = float(target_cycle - base["cycle"])
    for key in metric_keys:
        vals = [(row["cycle"], float_or_nan(row.get(key))) for row in snapshots if math.isfinite(float_or_nan(row.get(key)))]
        if len(vals) < 2:
            continue
        if method.startswith("last_"):
            n = min(int(method.split("_")[1]), len(vals))
            c0, v0 = vals[-n]
            c1, v1 = vals[-1]
            slope_metric = (v1 - v0) / max(float(c1 - c0), 1.0)
        else:
            window_n = min(int(method.split("_")[-1]), len(vals))
            window = vals[-window_n:]
            xs = np.array([item[0] for item in window], dtype=float)
            ys = np.array([item[1] for item in window], dtype=float)
            x = xs - xs.mean()
            slope_metric = float((x * ys).sum() / max(float((x * x).sum()), 1.0))
        pred[key] = float(base.get(key)) + delta * slope_metric
    return pred, names, slope


def infer_history_names(n):
    # P2 NEML names are stable; this fallback avoids needing a model in plotting/report paths.
    base = ["small_stress_%d" % i for i in range(6)] + ["alpha"]
    for branch in range(3):
        for comp in range(6):
            base.append("backstress_%d_%d" % (branch, comp))
    return base[:n]


def baseline_rows(path=BASELINE):
    rows = {}
    with Path(path).open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row = dict(row)
            cycle = int(row["cycle"])
            for key, value in list(row.items()):
                if key not in ["case_name"]:
                    row[key] = float_or_nan(value)
            row["cycle"] = cycle
            rows[cycle] = row
    cycles = sorted(rows)
    return rows, cycles


def nearest_baseline(cycle, rows, cycles):
    if int(cycle) in rows:
        return rows[int(cycle)], int(cycle), True
    nearest = min(cycles, key=lambda c: abs(c - int(cycle)))
    return rows[nearest], nearest, False


def norm_error(value, ref, floor=1.0e-12):
    value = float_or_nan(value)
    ref = float_or_nan(ref)
    if not math.isfinite(value) or not math.isfinite(ref):
        return float("inf")
    return abs(value - ref) / max(abs(ref), floor)


def validate_snapshot(snapshot, route_type, base_cycle, requested_target, jump_target, deltaN_requested, deltaN_used, method, limiting_variable, rows, cycles):
    ref, ref_cycle, exact = nearest_baseline(snapshot["cycle"], rows, cycles)
    mean_err = norm_error(snapshot.get("strain_mean"), ref.get("strain_mean"), 1.0e-6)
    ratchet_err = norm_error(snapshot.get("ratcheting_strain"), ref.get("ratcheting_strain"), 1.0e-6)
    alpha_err = norm_error(snapshot.get("accumulated_inelastic_strain"), ref.get("accumulated_inelastic_strain_end"), 1.0e-8)
    backstress_err = norm_error(snapshot.get("backstress_norm"), ref.get("backstress_norm_end"), 1.0e-8)
    drift_direction = True
    if snapshot.get("ratcheting_strain") is not None and ref.get("ratcheting_strain") is not None:
        drift_direction = (float(snapshot.get("ratcheting_strain")) >= -1.0e-12) == (float(ref.get("ratcheting_strain")) >= -1.0e-12)
    nan = has_nonfinite_snapshot(snapshot) or any(not math.isfinite(x) for x in [mean_err, ratchet_err, alpha_err, backstress_err])
    strict = (not nan) and exact and drift_direction and mean_err <= 0.01 and ratchet_err <= 0.01 and alpha_err <= 0.01 and backstress_err <= 0.01
    relaxed2 = (not nan) and drift_direction and mean_err <= 0.02 and ratchet_err <= 0.02 and alpha_err <= 0.02 and backstress_err <= 0.02
    relaxed5 = (not nan) and drift_direction and mean_err <= 0.05 and ratchet_err <= 0.05 and alpha_err <= 0.05 and backstress_err <= 0.05
    return {
        "case_name": CASE_NAME,
        "route_type": route_type,
        "base_cycle": int(base_cycle),
        "requested_target_cycle": int(requested_target),
        "jump_target_cycle": int(jump_target),
        "deltaN_requested": int(deltaN_requested),
        "deltaN_used": int(deltaN_used),
        "derivative_method": method,
        "limiting_variable": limiting_variable or "",
        "comparison_cycle": int(snapshot["cycle"]),
        "reference_cycle": int(ref_cycle),
        "reference_exact": str(bool(exact)).lower(),
        "continuation_cycles": int(snapshot["cycle"] - jump_target),
        "strain_mean": snapshot.get("strain_mean"),
        "reference_strain_mean": ref.get("strain_mean"),
        "mean_strain_norm_error": mean_err,
        "ratcheting_strain": snapshot.get("ratcheting_strain"),
        "reference_ratcheting_strain": ref.get("ratcheting_strain"),
        "ratcheting_norm_error": ratchet_err,
        "accumulated_inelastic_strain": snapshot.get("accumulated_inelastic_strain"),
        "reference_accumulated_inelastic_strain": ref.get("accumulated_inelastic_strain_end"),
        "accumulated_inelastic_norm_error": alpha_err,
        "backstress_norm": snapshot.get("backstress_norm"),
        "reference_backstress_norm": ref.get("backstress_norm_end"),
        "backstress_norm_error": backstress_err,
        "drift_direction_correct": str(bool(drift_direction)).lower(),
        "strict_accepted": str(bool(strict)).lower(),
        "relaxed_2pct_accepted": str(bool(relaxed2)).lower(),
        "relaxed_5pct_accepted": str(bool(relaxed5)).lower(),
        "real_neml_backend": "true",
        "full_state_reinjected": "true",
        "nan_or_inf": str(bool(nan)).lower(),
        "status": "ok" if not nan else "nonfinite_error",
    }


def write_csv(path, rows, fields=None):
    path = Path(path)
    ensure_dir(path.parent)
    fields = fields or (list(rows[0].keys()) if rows else SUMMARY_FIELDS)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def markdown_table(rows, fields, limit=20):
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def fixed_route(base_cycle, target_cycle, method="least_squares_last_20", compare_offsets=(0, 100, 1000), keep_window=60):
    rows, cycles = baseline_rows()
    _, names, _, snapshots, _, _ = run_to_cycle(base_cycle, keep_window=keep_window)
    base_snapshot = snapshots[-1]
    pred, _, _ = extrapolate_snapshot(snapshots, target_cycle, method)
    if has_nonfinite_snapshot(pred):
        raise RuntimeError("extrapolated state contains NaN/inf for %d -> %d" % (base_cycle, target_cycle))
    continued = continue_from_snapshot(pred, target_cycle, compare_offsets)
    out = []
    for cycle in sorted(continued):
        out.append(validate_snapshot(continued[cycle], "fixed", base_cycle, target_cycle, target_cycle, target_cycle - base_cycle, target_cycle - base_cycle, method, "", rows, cycles))
    return out, base_snapshot, pred


def adaptive_delta(base_snapshot, snapshots, requested_target, method, previous_accepted=100000, epsilon=0.01, delta_min=1, delta_max=100000, growth_factor=5, tiny=1.0e-14):
    names, base_vec = state_vector_from_snapshot(base_snapshot)
    _, slope = derivative_from_window(snapshots, method)
    control = []
    # Include all full-state variables.
    for name, q, dq in zip(names, base_vec, slope):
        scale = max(abs(float(q)), 1.0e-8)
        allowed = math.floor(epsilon * scale / max(abs(float(dq)), tiny))
        control.append((name, allowed, float(dq), scale))
    # Include cycle metric variables when enough rows exist.
    for key in ["strain_mean", "ratcheting_strain", "strain_max", "strain_min", "accumulated_inelastic_strain", "backstress_norm"]:
        ys = np.array([float_or_nan(row.get(key)) for row in snapshots if math.isfinite(float_or_nan(row.get(key)))], dtype=float)
        xs = np.array([row["cycle"] for row in snapshots if math.isfinite(float_or_nan(row.get(key)))], dtype=float)
        if len(ys) >= 2:
            if method.startswith("last_"):
                n = min(int(method.split("_")[1]), len(ys))
                dq = (ys[-1] - ys[-n]) / max(xs[-1] - xs[-n], 1.0)
            else:
                x = xs - xs.mean()
                dq = float((x * ys).sum() / max(float((x * x).sum()), 1.0))
            scale = max(abs(float(ys[-1])), 1.0e-8)
            allowed = math.floor(epsilon * scale / max(abs(float(dq)), tiny))
            control.append((key, allowed, float(dq), scale))
    requested = max(1, int(requested_target - base_snapshot["cycle"]))
    cap = min(requested, int(delta_max), int(growth_factor * max(1, previous_accepted)))
    limiting = min(control, key=lambda item: item[1])
    chosen = max(int(delta_min), min(cap, int(limiting[1])))
    return {
        "deltaN_requested": requested,
        "deltaN_adaptive": chosen,
        "limiting_variable": limiting[0],
        "limiting_raw_deltaN": int(limiting[1]),
        "limiting_slope": limiting[2],
        "limiting_scale": limiting[3],
        "epsilon": epsilon,
        "deltaN_max": delta_max,
        "growth_factor": growth_factor,
        "derivative_method": method,
    }


def adaptive_route(base_cycle, requested_target, method="least_squares_last_20", previous_accepted=100000, compare_offsets=(0, 100, 1000), keep_window=60):
    rows, cycles = baseline_rows()
    _, _, _, snapshots, _, _ = run_to_cycle(base_cycle, keep_window=keep_window)
    base_snapshot = snapshots[-1]
    info = adaptive_delta(base_snapshot, snapshots, requested_target, method, previous_accepted=previous_accepted)
    jump_target = int(base_cycle + info["deltaN_adaptive"])
    pred, _, _ = extrapolate_snapshot(snapshots, jump_target, method)
    if has_nonfinite_snapshot(pred):
        raise RuntimeError("adaptive extrapolated state contains NaN/inf for base %d request %d" % (base_cycle, requested_target))
    continued = continue_from_snapshot(pred, jump_target, compare_offsets)
    out = []
    for cycle in sorted(continued):
        out.append(validate_snapshot(continued[cycle], "adaptive", base_cycle, requested_target, jump_target, info["deltaN_requested"], info["deltaN_adaptive"], method, info["limiting_variable"], rows, cycles))
    return out, info, pred


def summarize_acceptance(rows):
    if not rows:
        return {"strict": 0, "relaxed2": 0, "relaxed5": 0, "total": 0}
    return {
        "strict": sum(1 for row in rows if row.get("strict_accepted") == "true"),
        "relaxed2": sum(1 for row in rows if row.get("relaxed_2pct_accepted") == "true"),
        "relaxed5": sum(1 for row in rows if row.get("relaxed_5pct_accepted") == "true"),
        "total": len(rows),
    }


def write_report(path, title, rows, extra=None, gate_pass=None):
    acc = summarize_acceptance(rows)
    lines = [
        "# %s" % title,
        "",
        "- Real NEML backend: `true`",
        "- NEML path: `%s`" % getattr(neml, "__file__", ""),
        "- Rows: `%d`" % acc["total"],
        "- Strict accepted rows: `%d`" % acc["strict"],
        "- Relaxed 2 pct accepted rows: `%d`" % acc["relaxed2"],
        "- Relaxed 5 pct accepted rows: `%d`" % acc["relaxed5"],
    ]
    if gate_pass is not None:
        lines.append("- Gate pass: `%s`" % str(bool(gate_pass)).lower())
    if extra:
        lines.extend([""] + extra)
    if rows:
        fields = ["base_cycle", "requested_target_cycle", "jump_target_cycle", "derivative_method", "comparison_cycle", "mean_strain_norm_error", "accumulated_inelastic_norm_error", "backstress_norm_error", "relaxed_5pct_accepted"]
        lines.extend(["", "## Error Table", markdown_table(rows, fields, limit=40)])
    Path(path).write_text("\n".join(lines) + "\n")
