#!/usr/bin/env python3
"""Stage 15K NEML state-access introspection.

This script intentionally performs only API introspection and a minimal direct
model-update probe. It does not do cycle jumping and it does not submit PBS.
"""

from __future__ import print_function

import inspect
import os
import platform
import sys
import traceback


REPORT = "STAGE15K_NEML_STATE_INTROSPECTION_REPORT.md"


P2 = {
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


def public_methods(obj):
    names = []
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            value = getattr(obj, name)
        except Exception:
            continue
        if callable(value):
            names.append(name)
    return sorted(names)


def signature_for(obj, name):
    try:
        return str(inspect.signature(getattr(obj, name)))
    except Exception as exc:
        return "signature unavailable: %s: %s" % (type(exc).__name__, exc)


def public_data_attrs(obj):
    attrs = []
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            value = getattr(obj, name)
        except Exception:
            continue
        if not callable(value):
            attrs.append((name, type(value).__name__, value))
    return attrs


def short_value(value, max_len=140):
    text = repr(value)
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


def len_or_none(value):
    try:
        return len(value)
    except Exception:
        return None


def build_model(elasticity, hardening, models, ri_flow, surfaces):
    elastic = elasticity.IsotropicLinearElasticModel(P2["E"], "youngs", P2["nu"], "poissons")
    surface = surfaces.IsoKinJ2()
    iso = hardening.VoceIsotropicHardeningRule(P2["yield_stress"], P2["Q"], P2["b"])
    gmodels = [hardening.ConstantGamma(g) for g in P2["gamma"]]
    hmodel = hardening.Chaboche(iso, P2["C"], gmodels, P2["A"], P2["a"])
    flow = ri_flow.RateIndependentNonAssociativeHardening(surface, hmodel)
    return models.SmallStrainRateIndependentPlasticity(elastic, flow)


def markdown_list(items):
    if not items:
        return "- None found"
    return "\n".join("- `%s`" % item for item in items)


def inspect_update_access(model):
    candidates = []
    for name in public_methods(model):
        low = name.lower()
        if "update" in low or "store" in low or "hist" in low or "internal" in low:
            candidates.append((name, signature_for(model, name)))
    return candidates


def make_state_snapshot(driver):
    fields = ["t_int", "stress_int", "strain_int", "stored_int", "u_int", "p_int"]
    snapshot = {}
    for field in fields:
        if hasattr(driver, field):
            value = getattr(driver, field)
            snapshot[field] = {
                "type": type(value).__name__,
                "len": len_or_none(value),
                "preview": short_value(value),
            }
    return snapshot


def copy_array(np, value):
    return np.array(value, dtype=float, copy=True)


def direct_update_probe(np, model):
    """Probe whether lower-level update_sd exposes explicit state arguments.

    The return value is diagnostic only. The Stage 15K restart script must still
    perform an exact restart/reinjection verification before any jumping.
    """
    result = {
        "attempted": False,
        "passed": False,
        "message": "",
        "state_fields": [],
        "max_abs_repeat_difference": None,
    }
    if not hasattr(model, "update_sd"):
        result["message"] = "model.update_sd is not available"
        return result
    if not hasattr(model, "init_store"):
        result["message"] = "model.init_store is not available"
        return result

    result["attempted"] = True
    try:
        strain_n = np.zeros(6)
        strain_np1 = np.array([0.0015, 0.0, 0.0, 0.0, 0.0, 0.0])
        stress_n = np.zeros(6)
        history_n = copy_array(np, model.init_store())
        u_n = 0.0
        p_n = 0.0
        out_a = model.update_sd(strain_np1, strain_n, 293.15, 293.15, 1.0, 0.0, stress_n, history_n, u_n, p_n)
        out_b = model.update_sd(
            copy_array(np, strain_np1),
            copy_array(np, strain_n),
            293.15,
            293.15,
            1.0,
            0.0,
            copy_array(np, stress_n),
            copy_array(np, history_n),
            u_n,
            p_n,
        )
        result["state_fields"] = ["strain", "stress", "history", "temperature", "time", "u", "p"]
        diffs = []
        for a, b in zip(out_a, out_b):
            try:
                diffs.append(float(np.max(np.abs(np.asarray(a) - np.asarray(b)))))
            except Exception:
                try:
                    diffs.append(abs(float(a) - float(b)))
                except Exception:
                    pass
        result["max_abs_repeat_difference"] = max(diffs) if diffs else 0.0
        result["passed"] = result["max_abs_repeat_difference"] <= 1.0e-13
        result["message"] = "direct update_sd can be called with explicit prior state"
    except Exception as exc:
        result["message"] = "%s: %s\n%s" % (type(exc).__name__, exc, traceback.format_exc())
    return result


def main():
    lines = []
    exit_code = 1

    lines.append("# Stage 15K NEML State Introspection Report")
    lines.append("")
    lines.append("## Execution Context Note")
    lines.append("- Local Windows/current environment pre-check: **NEML unavailable** (`ModuleNotFoundError: No module named 'neml'`).")
    lines.append("- HPC environment result: see the current run details below.")
    lines.append("")
    lines.append("## Environment")
    lines.append("- Python executable: `%s`" % sys.executable)
    lines.append("- Python version: `%s`" % sys.version.replace("\n", " "))
    lines.append("- Platform: `%s`" % platform.platform())
    lines.append("- Working directory: `%s`" % os.getcwd())
    lines.append("")

    try:
        import numpy as np
        import neml
        from neml import drivers, elasticity, hardening, models, ri_flow, surfaces
    except Exception as exc:
        lines.append("## NEML Import")
        lines.append("- Status: **FAIL**")
        lines.append("- Error: `%s: %s`" % (type(exc).__name__, exc))
        lines.append("")
        lines.append("## Stop/Go Decision")
        lines.append("**STOP.** NEML is not importable in this Python environment, so full state access cannot be verified.")
        with open(REPORT, "w") as handle:
            handle.write("\n".join(lines) + "\n")
        print("Wrote %s" % REPORT)
        print("STOP: NEML import failed; do not continue to restart or jump tests.")
        return exit_code

    lines.append("## NEML Import")
    lines.append("- Status: **PASS**")
    lines.append("- NEML path: `%s`" % getattr(neml, "__file__", "<unknown>"))
    lines.append("- NumPy version: `%s`" % getattr(np, "__version__", "<unknown>"))
    lines.append("")

    try:
        model = build_model(elasticity, hardening, models, ri_flow, surfaces)
    except Exception as exc:
        lines.append("## Model Construction")
        lines.append("- Status: **FAIL**")
        lines.append("- Error: `%s: %s`" % (type(exc).__name__, exc))
        lines.append("")
        lines.append("## Stop/Go Decision")
        lines.append("**STOP.** The Stage 15 P2 Chaboche model could not be constructed.")
        with open(REPORT, "w") as handle:
            handle.write("\n".join(lines) + "\n")
        print("Wrote %s" % REPORT)
        print("STOP: model construction failed.")
        return exit_code

    lines.append("## Model Construction")
    lines.append("- Status: **PASS**")
    lines.append("- Model type: `%s`" % type(model).__name__)
    lines.append("- Model module: `%s`" % type(model).__module__)
    lines.append("")

    model_methods = public_methods(model)
    lines.append("## Available Model Methods")
    lines.append(markdown_list(model_methods))
    lines.append("")
    lines.append("## Model Update/Internal-State Candidate Methods")
    update_candidates = inspect_update_access(model)
    if update_candidates:
        for name, sig in update_candidates:
            lines.append("- `%s`: `%s`" % (name, sig))
    else:
        lines.append("- None found")
    lines.append("")

    lines.append("## Model State Metadata")
    try:
        names = list(model.report_internal_variable_names())
        lines.append("- `report_internal_variable_names()` status: **PASS**")
        lines.append("- Internal variable count: `%d`" % len(names))
        lines.append("- Internal variable names: `%s`" % ", ".join(names))
    except Exception as exc:
        names = []
        lines.append("- `report_internal_variable_names()` status: **FAIL**")
        lines.append("- Error: `%s: %s`" % (type(exc).__name__, exc))
    try:
        store = model.init_store()
        lines.append("- `init_store()` status: **PASS**")
        lines.append("- Initial history type: `%s`" % type(store).__name__)
        lines.append("- Initial history length: `%s`" % len_or_none(store))
        lines.append("- Initial history preview: `%s`" % short_value(store))
    except Exception as exc:
        store = None
        lines.append("- `init_store()` status: **FAIL**")
        lines.append("- Error: `%s: %s`" % (type(exc).__name__, exc))
    lines.append("")

    lines.append("## Available Driver Methods")
    driver_module_methods = public_methods(drivers)
    lines.append("### `neml.drivers` module callables")
    lines.append(markdown_list(driver_module_methods))
    lines.append("")
    driver = None
    try:
        driver = drivers.Driver_sd(model, T_init=293.15)
        lines.append("### `drivers.Driver_sd` instance methods")
        lines.append(markdown_list(public_methods(driver)))
    except Exception as exc:
        lines.append("### `drivers.Driver_sd`")
        lines.append("- Status: **FAIL**")
        lines.append("- Error: `%s: %s`" % (type(exc).__name__, exc))
    lines.append("")

    lines.append("## Driver Data Attributes")
    if driver is None:
        lines.append("- Driver instance unavailable.")
    else:
        for name, typename, value in public_data_attrs(driver):
            lines.append("- `%s`: type `%s`, len `%s`, preview `%s`" % (name, typename, len_or_none(value), short_value(value)))
    lines.append("")

    lines.append("## Stress, Strain, And History Storage")
    if driver is None:
        lines.append("- Driver storage could not be inspected.")
    else:
        try:
            sdir = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            driver.srate_sinc_step(sdir, 1.0e-4, 120.0, 293.15)
            snapshot = make_state_snapshot(driver)
            for field in sorted(snapshot):
                data = snapshot[field]
                lines.append("- `%s`: type `%s`, len `%s`, preview `%s`" % (field, data["type"], data["len"], data["preview"]))
            lines.append("- Interpretation: the public driver stores path history in list-like attributes such as `stress_int`, `strain_int`, `stored_int`, and `t_int` when present.")
        except Exception as exc:
            lines.append("- Driver one-step storage probe status: **FAIL**")
            lines.append("- Error: `%s: %s`" % (type(exc).__name__, exc))
    lines.append("")

    probe = direct_update_probe(np, model)
    lines.append("## Lower-Level Model Update Access")
    lines.append("- `update_sd` available: `%s`" % hasattr(model, "update_sd"))
    lines.append("- `init_store` available: `%s`" % hasattr(model, "init_store"))
    lines.append("- Probe attempted: `%s`" % probe["attempted"])
    lines.append("- Probe passed: `%s`" % probe["passed"])
    lines.append("- Probe message: `%s`" % probe["message"].replace("\n", " "))
    lines.append("- Explicit state fields implied by `update_sd`: `%s`" % ", ".join(probe["state_fields"]))
    lines.append("- Max absolute repeat difference: `%s`" % probe["max_abs_repeat_difference"])
    lines.append("")

    driver_has_state = driver is not None and all(hasattr(driver, name) for name in ["stress_int", "strain_int", "stored_int", "t_int"])
    full_state_access = (
        hasattr(model, "update_sd")
        and hasattr(model, "init_store")
        and probe["passed"]
        and store is not None
    )

    lines.append("## Full State Save/Restore Assessment")
    lines.append("- Driver exposes stress/strain/history/time storage: `%s`" % driver_has_state)
    lines.append("- Lower-level explicit state update is accessible: `%s`" % full_state_access)
    if full_state_access:
        lines.append("- Assessment: **PASS**. Full constitutive state appears representable as strain, stress, history/internal variables, temperature, time, energy `u`, and dissipation/plastic work `p`, and `update_sd` accepts those as explicit prior-state inputs.")
        lines.append("- Required next step: run the Stage 15K restart/reinjection test and require near-roundoff differences before any state jumping.")
        exit_code = 0
    else:
        lines.append("- Assessment: **FAIL**. This environment did not prove exact public access to the full NEML state.")
        missing = []
        if not hasattr(model, "update_sd"):
            missing.append("model.update_sd")
        if not hasattr(model, "init_store"):
            missing.append("model.init_store")
        if not probe["passed"]:
            missing.append("repeatable direct update_sd probe")
        if store is None:
            missing.append("initial history/internal-state vector")
        lines.append("- Missing/failed evidence: `%s`" % ", ".join(missing))
    lines.append("")

    lines.append("## Stop/Go Decision")
    if full_state_access:
        lines.append("**GO TO RESTART TEST ONLY.** Do not proceed to fixed/adaptive jumps until restart/reinjection passes with near-roundoff differences.")
    else:
        lines.append("**STOP.** Document the NEML API limitation and do not continue to jump tests.")

    with open(REPORT, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print("Wrote %s" % REPORT)
    if exit_code == 0:
        print("PASS: full NEML state access appears available; restart/reinjection verification is the next required gate.")
    else:
        print("STOP: full NEML state access was not proven.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
