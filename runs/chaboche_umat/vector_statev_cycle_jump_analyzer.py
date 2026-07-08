import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HISTORY_CSV = ROOT / "chaboche_v1_full_statev_cycle_history.csv"
STABILITY_CSV = ROOT / "chaboche_v1_full_statev_cycle_stability.csv"

PREDICTIONS_CSV = ROOT / "chaboche_v1_vector_statev_cycle_jump_predictions.csv"
ERRORS_CSV = ROOT / "chaboche_v1_vector_statev_cycle_jump_errors.csv"
CONTROL_CSV = ROOT / "chaboche_v1_vector_statev_adaptive_jump_control.csv"
REPORT = ROOT / "CHABOCHE_V1_VECTOR_STATEV_CYCLE_JUMP_REPORT.md"

REFERENCE_START = 2
REFERENCE_END = 10
JUMP_BASE_CYCLE = 10
FIXED_TARGET_CYCLE = 20
SCALAR_ADAPTIVE_TARGET_CYCLE = 19
ETA = 1.0
JUMPMIN = 1
JUMPMAX = 60
CURVATURE_TOL = 0.01
SMALL = 1.0e-14

ACTIVE_COMPONENTS = [1, 2, 3, 4, 8, 9, 10]
NEAR_ZERO_COMPONENTS = [5, 6, 7, 11, 12, 13]
RECOMPUTABLE_COMPONENTS = [14]
DIAGNOSTIC_COMPONENTS = [15]


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return "%.12g" % value


def mean(values):
    return sum(values) / len(values) if values else 0.0


def sample_std(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_history():
    rows = []
    for raw in read_csv(HISTORY_CSV):
        row = {
            "cycle": int(raw["cycle"]),
            "time": float(raw["time"]),
            "target_time": float(raw["target_time"]),
            "time_error": float(raw["time_error"]),
        }
        for i in range(1, 16):
            row["STATEV%d_end" % i] = float(raw["STATEV%d_end" % i])
            row["Delta_STATEV%d" % i] = float(raw["Delta_STATEV%d" % i])
        rows.append(row)
    return rows


def read_stability():
    out = {}
    for raw in read_csv(STABILITY_CSV):
        idx = int(raw["statev_index"])
        out[idx] = raw
    return out


def component_role(index):
    if index in ACTIVE_COMPONENTS:
        return "active_vector_component"
    if index in NEAR_ZERO_COMPONENTS:
        return "near_zero_report_only"
    if index in RECOMPUTABLE_COMPONENTS:
        return "recomputable_report_only"
    if index in DIAGNOSTIC_COMPONENTS:
        return "diagnostic_report_only"
    return "unclassified"


def derivatives(history, index):
    rows_by_cycle = {r["cycle"]: r for r in history}
    ref = [rows_by_cycle[c] for c in range(REFERENCE_START, REFERENCE_END + 1)]
    deltas = [r["Delta_STATEV%d" % index] for r in ref]
    curvatures = []
    for cycle in range(max(REFERENCE_START + 1, 3), REFERENCE_END + 1):
        current_delta = rows_by_cycle[cycle]["Delta_STATEV%d" % index]
        previous_delta = rows_by_cycle[cycle - 1]["Delta_STATEV%d" % index]
        curvatures.append(current_delta - previous_delta)
    delta_mean = mean(deltas)
    delta_range = max(deltas) - min(deltas)
    rel_range = None if abs(delta_mean) < SMALL else delta_range / abs(delta_mean)
    return {
        "mean_dSTATEV_dN": delta_mean,
        "std_dSTATEV_dN": sample_std(deltas),
        "relative_range_dSTATEV_dN": rel_range,
        "mean_d2STATEV_dN2": mean(curvatures),
        "std_d2STATEV_dN2": sample_std(curvatures),
    }


def first_order(base, dn, slope):
    return base + dn * slope


def second_order(base, dn, slope, curvature):
    return base + dn * slope + 0.5 * dn * dn * curvature


def relative_error(actual, predicted):
    if actual is None or abs(actual) < SMALL:
        return None
    return abs(actual - predicted) / abs(actual) * 100.0


def adaptive_candidate(base, slope, curvature):
    scale = max(abs(base), abs(slope), SMALL)
    if abs(slope) < SMALL:
        raw = JUMPMAX
    else:
        raw = int(math.floor(ETA * scale / abs(slope)))
    candidate = max(JUMPMIN, min(raw, JUMPMAX))
    while candidate > JUMPMIN:
        p1 = first_order(base, candidate, slope)
        p2 = second_order(base, candidate, slope, curvature)
        denom = max(abs(p1), scale, SMALL)
        rel_diff = abs(p2 - p1) / denom
        if rel_diff <= CURVATURE_TOL:
            break
        candidate -= 1
    p1 = first_order(base, candidate, slope)
    p2 = second_order(base, candidate, slope, curvature)
    rel_diff = abs(p2 - p1) / max(abs(p1), scale, SMALL)
    return raw, candidate, rel_diff


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: fmt(row.get(field)) for field in fields})


def build_analysis(history, stability):
    by_cycle = {r["cycle"]: r for r in history}
    base = by_cycle[JUMP_BASE_CYCLE]
    max_abs_time_error = max(abs(r["time_error"]) for r in history)

    component_stats = {}
    control_rows = []
    for index in range(1, 16):
        stats = derivatives(history, index)
        component_stats[index] = stats
        base_value = base["STATEV%d_end" % index]
        raw, candidate, curvature_diff = adaptive_candidate(
            base_value, stats["mean_dSTATEV_dN"], stats["mean_d2STATEV_dN2"]
        )
        row = {
            "statev_index": index,
            "symbol_or_name": stability[index]["symbol_or_name"],
            "role": component_role(index),
            "used_for_jump_control": "yes" if index in ACTIVE_COMPONENTS else "no",
            "base_value_cycle_10": base_value,
            "mean_dSTATEV_dN_cycles_2_10": stats["mean_dSTATEV_dN"],
            "mean_d2STATEV_dN2_cycles_2_10": stats["mean_d2STATEV_dN2"],
            "relative_range_dSTATEV_dN_cycles_2_10": stats["relative_range_dSTATEV_dN"],
            "raw_candidate_DeltaN": raw,
            "candidate_DeltaN_after_curvature_check": candidate,
            "first_second_order_relative_difference": curvature_diff,
            "prior_stability_classification": stability[index]["classification"],
        }
        control_rows.append(row)

    active_control_rows = [r for r in control_rows if r["used_for_jump_control"] == "yes"]
    global_control = min(active_control_rows, key=lambda r: int(r["candidate_DeltaN_after_curvature_check"]))
    global_delta_n = int(global_control["candidate_DeltaN_after_curvature_check"])
    adaptive_target = JUMP_BASE_CYCLE + global_delta_n
    targets = [
        ("vector_global_adaptive_target", adaptive_target),
        ("scalar_sdv1_adaptive_target", SCALAR_ADAPTIVE_TARGET_CYCLE),
        ("fixed_validation_target", FIXED_TARGET_CYCLE),
    ]

    prediction_rows = []
    error_rows = []
    for target_type, target_cycle in targets:
        dn = target_cycle - JUMP_BASE_CYCLE
        actual_row = by_cycle.get(target_cycle)
        for index in range(1, 16):
            stats = component_stats[index]
            base_value = base["STATEV%d_end" % index]
            p1 = first_order(base_value, dn, stats["mean_dSTATEV_dN"])
            p2 = second_order(base_value, dn, stats["mean_dSTATEV_dN"], stats["mean_d2STATEV_dN2"])
            actual = None if actual_row is None else actual_row["STATEV%d_end" % index]
            common = {
                "target_type": target_type,
                "target_cycle": target_cycle,
                "jump_base_cycle": JUMP_BASE_CYCLE,
                "cycles_skipped": dn,
                "statev_index": index,
                "symbol_or_name": stability[index]["symbol_or_name"],
                "role": component_role(index),
                "used_for_jump_control": "yes" if index in ACTIVE_COMPONENTS else "no",
                "base_value_cycle_10": base_value,
                "mean_dSTATEV_dN_used": stats["mean_dSTATEV_dN"],
                "mean_d2STATEV_dN2_used": stats["mean_d2STATEV_dN2"],
                "first_order_prediction": p1,
                "second_order_prediction": p2,
                "explicit_reference": actual,
            }
            prediction_rows.append(common)
            error_rows.append({
                **common,
                "first_order_abs_error": None if actual is None else actual - p1,
                "first_order_rel_error_percent": relative_error(actual, p1),
                "second_order_abs_error": None if actual is None else actual - p2,
                "second_order_rel_error_percent": relative_error(actual, p2),
            })

    return {
        "prediction_rows": prediction_rows,
        "error_rows": error_rows,
        "control_rows": control_rows,
        "global_control": global_control,
        "global_delta_n": global_delta_n,
        "adaptive_target": adaptive_target,
        "max_abs_time_error": max_abs_time_error,
    }


def write_outputs(analysis):
    prediction_fields = [
        "target_type",
        "target_cycle",
        "jump_base_cycle",
        "cycles_skipped",
        "statev_index",
        "symbol_or_name",
        "role",
        "used_for_jump_control",
        "base_value_cycle_10",
        "mean_dSTATEV_dN_used",
        "mean_d2STATEV_dN2_used",
        "first_order_prediction",
        "second_order_prediction",
        "explicit_reference",
    ]
    error_fields = prediction_fields + [
        "first_order_abs_error",
        "first_order_rel_error_percent",
        "second_order_abs_error",
        "second_order_rel_error_percent",
    ]
    control_fields = [
        "statev_index",
        "symbol_or_name",
        "role",
        "used_for_jump_control",
        "base_value_cycle_10",
        "mean_dSTATEV_dN_cycles_2_10",
        "mean_d2STATEV_dN2_cycles_2_10",
        "relative_range_dSTATEV_dN_cycles_2_10",
        "raw_candidate_DeltaN",
        "candidate_DeltaN_after_curvature_check",
        "first_second_order_relative_difference",
        "prior_stability_classification",
    ]
    write_csv(PREDICTIONS_CSV, analysis["prediction_rows"], prediction_fields)
    write_csv(ERRORS_CSV, analysis["error_rows"], error_fields)
    write_csv(CONTROL_CSV, analysis["control_rows"], control_fields)


def row_for(error_rows, target_type, index):
    for row in error_rows:
        if row["target_type"] == target_type and row["statev_index"] == index:
            return row
    raise KeyError((target_type, index))


def write_report(analysis):
    control = analysis["global_control"]
    sdv1_vector_adaptive = row_for(analysis["error_rows"], "vector_global_adaptive_target", 1)
    sdv1_scalar_adaptive = row_for(analysis["error_rows"], "scalar_sdv1_adaptive_target", 1)
    sdv1_fixed = row_for(analysis["error_rows"], "fixed_validation_target", 1)
    active_errors = [
        r for r in analysis["error_rows"]
        if r["target_type"] == "vector_global_adaptive_target" and r["statev_index"] in ACTIVE_COMPONENTS
    ]
    worst_active = max(
        active_errors,
        key=lambda r: -1.0 if r["first_order_rel_error_percent"] is None else r["first_order_rel_error_percent"],
    )

    lines = [
        "# Chaboche-v1 Vector STATEV Cycle-Jump Report",
        "",
        "This analyzer extends the validated scalar SDV1 cycle-jump postprocessor to a vector-valued STATEV diagnostic. It remains Level-2 preparation only: no Abaqus rerun, no UMAT edit, no input-file edit, and no STATEV injection.",
        "",
        "## Inputs",
        "",
        f"- `{HISTORY_CSV.name}`",
        f"- `{STABILITY_CSV.name}`",
        "",
        "## Method",
        "",
        f"- Reference window: cycles `{REFERENCE_START}-{REFERENCE_END}`",
        f"- Jump base: cycle `{JUMP_BASE_CYCLE}`",
        f"- Active vector components used for jump control: `STATEV(1), STATEV(2-4), STATEV(8-10)`",
        f"- Near-zero shear components reported only: `STATEV(5-7), STATEV(11-13)`",
        f"- Recomputable/diagnostic components reported only: `STATEV(14-15)`",
        f"- Adaptive settings: `eta={ETA}`, `JUMPMIN={JUMPMIN}`, `JUMPMAX={JUMPMAX}`, curvature tolerance `{CURVATURE_TOL}`",
        "",
        "## Phase Consistency",
        "",
        f"- Maximum absolute cycle-end time error: `{fmt(analysis['max_abs_time_error'])}`",
    ]
    if analysis["max_abs_time_error"] > 1.0e-8:
        lines.append("- Warning: cycle-end frames are nearest available ODB frames, not exactly integer cycle times. This matters especially for backstress and viscoplastic strain components.")
    else:
        lines.append("- Cycle-end frames are effectively exact integer cycle times.")

    lines += [
        "",
        "## Adaptive Vector Jump Control",
        "",
        f"- Conservative global DeltaN: `{analysis['global_delta_n']}`",
        f"- Adaptive target cycle: `{analysis['adaptive_target']}`",
        f"- Controlling component: `STATEV({control['statev_index']})` `{control['symbol_or_name']}`",
        f"- Controlling component prior stability class: `{control['prior_stability_classification']}`",
        "",
        "The global vector jump is the minimum candidate jump over the active components. This is more conservative than the scalar SDV1-only adaptive jump because the normal backstress and viscoplastic strain components are included in the control set.",
        "",
        "## SDV1 Comparison",
        "",
        f"- Vector-global adaptive target cycle: `{sdv1_vector_adaptive['target_cycle']}`",
        f"- Scalar SDV1-only adaptive target cycle retained for comparison: `{sdv1_scalar_adaptive['target_cycle']}`",
        f"- First-order SDV1 relative error at vector-global adaptive target: `{fmt(sdv1_vector_adaptive['first_order_rel_error_percent'])}%`",
        f"- First-order SDV1 relative error at scalar SDV1-only adaptive target: `{fmt(sdv1_scalar_adaptive['first_order_rel_error_percent'])}%`",
        f"- First-order SDV1 relative error at fixed cycle 20 target: `{fmt(sdv1_fixed['first_order_rel_error_percent'])}%`",
        "",
        "## Active Component Error Summary at Adaptive Target",
        "",
        "| STATEV | Symbol | First-order rel. error [%] | Second-order rel. error [%] | Role |",
        "| ---: | --- | ---: | ---: | --- |",
    ]
    for row in active_errors:
        lines.append(
            f"| {row['statev_index']} | `{row['symbol_or_name']}` | "
            f"`{fmt(row['first_order_rel_error_percent'])}` | "
            f"`{fmt(row['second_order_rel_error_percent'])}` | {row['role']} |"
        )

    lines += [
        "",
        "## Worst Active Component at Adaptive Target",
        "",
        f"- `STATEV({worst_active['statev_index']})` `{worst_active['symbol_or_name']}`",
        f"- First-order relative error: `{fmt(worst_active['first_order_rel_error_percent'])}%`",
        "",
        "## Interpretation",
        "",
        "`STATEV(1)` remains the cleanest cycle-jump control variable. The normal backstress components `STATEV(2-4)` and normal viscoplastic strain components `STATEV(8-10)` are physically important for a future restart/injected-state continuation, but their cycle-end increments are less stable and must be handled cautiously.",
        "",
        "For this uniaxial test, the shear components are near zero and should not control the jump. `STATEV(14)` is recomputable from `STATEV(1)` and the material constants in this UMAT, while `STATEV(15)` is diagnostic.",
        "",
        "This result suggests that any Level-2 injection experiment should start conservatively. A scalar-only injected SDV1 test may be useful as a controlled experiment, but a physically consistent restart state will eventually require coordinated treatment of `STATEV(1-4,8-10)` at a consistent cycle phase point.",
        "",
        "## Output Files",
        "",
        f"- `{PREDICTIONS_CSV.name}`",
        f"- `{ERRORS_CSV.name}`",
        f"- `{CONTROL_CSV.name}`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    history = read_history()
    stability = read_stability()
    analysis = build_analysis(history, stability)
    write_outputs(analysis)
    write_report(analysis)
    control = analysis["global_control"]
    sdv1_adaptive = row_for(analysis["error_rows"], "vector_global_adaptive_target", 1)
    print("Vector STATEV cycle-jump analyzer complete")
    print("Global DeltaN:", analysis["global_delta_n"])
    print("Adaptive target cycle:", analysis["adaptive_target"])
    print("Controlling component: STATEV%d %s" % (control["statev_index"], control["symbol_or_name"]))
    print("Max abs time error:", fmt(analysis["max_abs_time_error"]))
    print("SDV1 first-order relative error at adaptive target:", fmt(sdv1_adaptive["first_order_rel_error_percent"]))


if __name__ == "__main__":
    main()
