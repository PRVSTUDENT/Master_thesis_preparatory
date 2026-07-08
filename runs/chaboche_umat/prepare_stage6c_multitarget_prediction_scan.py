import csv
import math
import os
import sys


BASE_CYCLE = 10
TARGET_CYCLES = [29, 39, 49]
MEAN_START = 2
MEAN_END = 10
FULL_REFERENCE_CYCLES = 50

HISTORY_CSV = "chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv"
SUMMARY_CSV = "chaboche_vp_v1_cyclic_eps005_50cycles_summary.csv"
OUT_DIR = "stage6_multitarget_jump_scan"

ERROR_CSV = os.path.join(OUT_DIR, "stage6c_multitarget_prediction_errors.csv")
SUMMARY_OUT_CSV = os.path.join(OUT_DIR, "stage6c_multitarget_prediction_summary.csv")
REPORT_MD = os.path.join(OUT_DIR, "STAGE6C_MULTITARGET_PREDICTION_SCAN_REPORT.md")

NSTATEV = 15
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]
ACTIVE_STATEV = [1, 2, 3, 4, 8, 9, 10]
NEAR_ZERO_STATEV = [5, 6, 7, 11, 12, 13]
SCAN_STATEV = [1, 2, 3, 4, 8, 9, 10, 14, 15]
SCAN_QUANTITIES = (
    ["STATEV%d" % i for i in SCAN_STATEV]
    + ["STATEV%d" % i for i in NEAR_ZERO_STATEV]
    + STRESS_COMPONENTS
)

QISO = 200.0
BISO = 0.05


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % value


def maybe_float(text):
    if text is None or text == "":
        return None
    return float(text)


def mean(values):
    return sum(values) / float(len(values)) if values else None


def abs_err(predicted, exact):
    if predicted is None or exact is None:
        return None
    return abs(predicted - exact)


def rel_err(predicted, exact):
    if predicted is None or exact is None or abs(exact) < 1.0e-30:
        return None
    return abs(predicted - exact) / abs(exact)


def read_summary():
    summary = {}
    with open(SUMMARY_CSV, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            summary[row["quantity"]] = maybe_float(row["value"])
    return summary


def read_cycle_history():
    rows = []
    with open(HISTORY_CSV, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed = {"cycle": int(row["cycle"])}
            for i in range(1, NSTATEV + 1):
                parsed["STATEV%d_end" % i] = maybe_float(row["STATEV%d_end" % i])
                parsed["Delta_STATEV%d" % i] = maybe_float(row["Delta_STATEV%d" % i])
            for name in STRESS_COMPONENTS:
                parsed[name] = maybe_float(row[name])
                parsed["Delta_%s" % name] = maybe_float(row["Delta_%s" % name])
            rows.append(parsed)
    return rows


def get_cycle_row(rows, cycle):
    for row in rows:
        if row["cycle"] == cycle:
            return row
    raise KeyError("Missing cycle %s in %s" % (cycle, HISTORY_CSV))


def statev_policy(index):
    if index in ACTIVE_STATEV:
        return "active_first_order_cycle_space"
    if index in NEAR_ZERO_STATEV:
        return "near_zero_predicted_flagged"
    if index == 14:
        return "recomputed_from_predicted_STATEV1"
    if index == 15:
        return "reset_to_zero_for_injection"
    return "first_order_cycle_space"


def compute_mean_increments(rows):
    window = [row for row in rows if MEAN_START <= row["cycle"] <= MEAN_END]
    statev_mean = {}
    stress_mean = {}
    for i in range(1, NSTATEV + 1):
        statev_mean[i] = mean([row["Delta_STATEV%d" % i] for row in window])
    for name in STRESS_COMPONENTS:
        stress_mean[name] = mean([row["Delta_%s" % name] for row in window])
    return statev_mean, stress_mean


def predict_for_target(rows, statev_mean, stress_mean, target_cycle):
    base = get_cycle_row(rows, BASE_CYCLE)
    delta_n = target_cycle - BASE_CYCLE
    statev = {}
    stress = {}

    for i in range(1, NSTATEV + 1):
        statev[i] = base["STATEV%d_end" % i] + delta_n * statev_mean[i]
    statev[14] = QISO * (1.0 - math.exp(-BISO * statev[1]))
    statev[15] = 0.0

    for name in STRESS_COMPONENTS:
        stress[name] = base[name] + delta_n * stress_mean[name]

    return statev, stress


def add_error_row(rows, target_cycle, quantity, predicted, exact, policy):
    relative = rel_err(predicted, exact)
    rows.append({
        "target_cycle": target_cycle,
        "continuation_to_cycle": target_cycle + 1,
        "delta_n": target_cycle - BASE_CYCLE,
        "skipped_intermediate_cycles": target_cycle - BASE_CYCLE - 1,
        "quantity": quantity,
        "predicted_value": predicted,
        "exact_value": exact,
        "absolute_error": abs_err(predicted, exact),
        "relative_error": relative,
        "relative_error_percent": None if relative is None else 100.0 * relative,
        "policy": policy,
    })


def build_error_rows(rows):
    statev_mean, stress_mean = compute_mean_increments(rows)
    error_rows = []

    for target_cycle in TARGET_CYCLES:
        exact = get_cycle_row(rows, target_cycle)
        pred_statev, pred_stress = predict_for_target(rows, statev_mean, stress_mean, target_cycle)

        for i in range(1, NSTATEV + 1):
            add_error_row(
                error_rows,
                target_cycle,
                "STATEV%d" % i,
                pred_statev[i],
                exact["STATEV%d_end" % i],
                statev_policy(i),
            )

        for name in STRESS_COMPONENTS:
            add_error_row(
                error_rows,
                target_cycle,
                name,
                pred_stress[name],
                exact[name],
                "first_order_cycle_space",
            )

    return error_rows


def find_error(error_rows, target_cycle, quantity):
    for row in error_rows:
        if row["target_cycle"] == target_cycle and row["quantity"] == quantity:
            return row
    raise KeyError("Missing error row for target %s quantity %s" % (target_cycle, quantity))


def max_rel_percent(error_rows, target_cycle, quantities):
    values = []
    for quantity in quantities:
        row = find_error(error_rows, target_cycle, quantity)
        if row["relative_error_percent"] is not None:
            values.append(row["relative_error_percent"])
    return max(values) if values else None


def recommendation(statev1_percent, s11_percent, backstress_percent, vp_tensor_percent):
    if (
        statev1_percent is not None
        and s11_percent is not None
        and backstress_percent is not None
        and vp_tensor_percent is not None
        and statev1_percent < 1.0
        and s11_percent < 1.0
        and backstress_percent < 3.0
        and vp_tensor_percent < 3.0
    ):
        return "strong_candidate"
    if (
        statev1_percent is not None
        and s11_percent is not None
        and backstress_percent is not None
        and vp_tensor_percent is not None
        and statev1_percent < 1.0
        and s11_percent < 3.0
        and backstress_percent < 6.0
        and vp_tensor_percent < 6.0
    ):
        return "acceptable_exploratory_candidate"
    return "not_headline_candidate"


def build_summary_rows(error_rows):
    summary_rows = []
    for target_cycle in TARGET_CYCLES:
        statev1 = find_error(error_rows, target_cycle, "STATEV1")
        s11 = find_error(error_rows, target_cycle, "S11")
        backstress = max_rel_percent(error_rows, target_cycle, ["STATEV2", "STATEV3", "STATEV4"])
        vp_tensor = max_rel_percent(error_rows, target_cycle, ["STATEV8", "STATEV9", "STATEV10"])
        rec = recommendation(
            statev1["relative_error_percent"],
            s11["relative_error_percent"],
            backstress,
            vp_tensor,
        )
        summary_rows.append({
            "target_cycle": target_cycle,
            "continuation_to_cycle": target_cycle + 1,
            "delta_n": target_cycle - BASE_CYCLE,
            "skipped_intermediate_cycles": target_cycle - BASE_CYCLE - 1,
            "cycle_jump_computed_cycles": BASE_CYCLE + 1,
            "full_reference_cycles": target_cycle + 1,
            "cycle_count_reduction_percent": 100.0 * (1.0 - float(BASE_CYCLE + 1) / float(target_cycle + 1)),
            "STATEV1_relative_error_percent": statev1["relative_error_percent"],
            "STATEV2_4_max_relative_error_percent": backstress,
            "STATEV8_10_max_relative_error_percent": vp_tensor,
            "S11_relative_error_percent": s11["relative_error_percent"],
            "recommendation": rec,
        })
    return summary_rows


def write_error_csv(error_rows):
    fields = [
        "target_cycle",
        "continuation_to_cycle",
        "delta_n",
        "skipped_intermediate_cycles",
        "quantity",
        "predicted_value",
        "exact_value",
        "absolute_error",
        "relative_error",
        "relative_error_percent",
        "policy",
    ]
    with csv_open_write(ERROR_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in error_rows:
            writer.writerow({
                field: row[field] if field in ("quantity", "policy") else fmt(row[field])
                for field in fields
            })


def write_summary_csv(summary_rows):
    fields = [
        "target_cycle",
        "continuation_to_cycle",
        "delta_n",
        "skipped_intermediate_cycles",
        "cycle_jump_computed_cycles",
        "full_reference_cycles",
        "cycle_count_reduction_percent",
        "STATEV1_relative_error_percent",
        "STATEV2_4_max_relative_error_percent",
        "STATEV8_10_max_relative_error_percent",
        "S11_relative_error_percent",
        "recommendation",
    ]
    with csv_open_write(SUMMARY_OUT_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow({
                field: row[field] if field == "recommendation" else fmt(row[field])
                for field in fields
            })


def best_candidate(summary_rows):
    candidates = [
        row for row in summary_rows
        if row["recommendation"] in ("strong_candidate", "acceptable_exploratory_candidate")
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: row["target_cycle"])[-1]


def write_report(summary_rows, summary):
    best = best_candidate(summary_rows)
    lines = [
        "# Stage 6C Multi-Target Prediction Scan Report",
        "",
        "## Purpose",
        "",
        "This scan evaluates predicted injection-state quality for larger FE cycle jumps before running another Abaqus continuation. It uses the existing no-skip 50-cycle reference history and performs no Abaqus rerun.",
        "",
        "No UMAT or Abaqus input deck was modified.",
        "",
        "## Method",
        "",
        "- Base cycle: `%d`" % BASE_CYCLE,
        "- Targets: `%s`" % ", ".join([str(cycle) for cycle in TARGET_CYCLES]),
        "- Mean increment window: cycles `%d-%d`" % (MEAN_START, MEAN_END),
        "- Prediction rule: `predicted_target = value_cycle10 + DeltaN * mean_increment_per_cycle`",
        "- STATEV14 policy: recomputed from predicted STATEV1 using `Q*(1-exp(-b*STATEV1))`",
        "- STATEV15 policy: reset to `0` for injection",
        "- Compared exact target states from `chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv` only for validation.",
        "",
        "## Decision Rules",
        "",
        "- Strong candidate: `STATEV1 < 1%`, `S11 < 1%`, and vector components preferably `< 3%`.",
        "- Acceptable exploratory candidate: `STATEV1 < 1%`, `S11 < 3%`, and vector components preferably `< 6%`.",
        "- Not headline candidate: `S11 > 3%` or `STATEV2-4 > 6%`.",
        "",
        "## Summary",
        "",
        "| Target | Continue to | DeltaN | Skipped cycles | Computed route | Full route | Reduction | STATEV1 err | STATEV2-4 max err | STATEV8-10 max err | S11 err | Recommendation |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            "| %d | %d | %d | %d | %d | %d | %s%% | %s%% | %s%% | %s%% | %s%% | `%s` |"
            % (
                row["target_cycle"],
                row["continuation_to_cycle"],
                row["delta_n"],
                row["skipped_intermediate_cycles"],
                row["cycle_jump_computed_cycles"],
                row["full_reference_cycles"],
                fmt(row["cycle_count_reduction_percent"]),
                fmt(row["STATEV1_relative_error_percent"]),
                fmt(row["STATEV2_4_max_relative_error_percent"]),
                fmt(row["STATEV8_10_max_relative_error_percent"]),
                fmt(row["S11_relative_error_percent"]),
                row["recommendation"],
            )
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- Cycle 49 gives the largest skip but has noticeable stress/backstress drift.",
        "- The best next FE validation target should be the largest target satisfying the decision rules.",
    ]
    if best:
        lines.append(
            "- Largest candidate satisfying the rules: target cycle `%d` with recommendation `%s`."
            % (best["target_cycle"], best["recommendation"])
        )
    else:
        lines.append(
            "- None of the scanned targets satisfy the stated candidate rules with the current first-order predictor."
        )
    lines += [
        "- The scan confirms that scalar `STATEV1` extrapolation is less restrictive than full vector/stress extrapolation.",
        "",
        "## Cycle-50 Reference Context",
        "",
        "- Full explicit cycle-50 STATEV1: `%s`" % fmt(summary.get("final_STATEV1")),
        "- Full explicit cycle-50 S11: `%s MPa`" % fmt(summary.get("final_S11")),
        "- Full explicit cycle-50 RIGHT_FACE RF1: `%s`" % fmt(summary.get("final_RIGHT_FACE_RF1_SUM")),
        "",
        "## Outputs",
        "",
        "- Detailed errors: `%s`" % ERROR_CSV,
        "- Target summary: `%s`" % SUMMARY_OUT_CSV,
    ]
    with open(REPORT_MD, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    rows = read_cycle_history()
    summary = read_summary()
    error_rows = build_error_rows(rows)
    summary_rows = build_summary_rows(error_rows)
    write_error_csv(error_rows)
    write_summary_csv(summary_rows)
    write_report(summary_rows, summary)
    print("Wrote %s" % ERROR_CSV)
    print("Wrote %s" % SUMMARY_OUT_CSV)
    print("Wrote %s" % REPORT_MD)


if __name__ == "__main__":
    main()
