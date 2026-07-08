import csv
import math
import os
import sys


BASE_CYCLE = 10
TARGET_CYCLE = 49
DELTA_N = TARGET_CYCLE - BASE_CYCLE
MEAN_START = 2
MEAN_END = 10
SKIPPED_INTERMEDIATE_CYCLES = TARGET_CYCLE - BASE_CYCLE - 1
FULL_REFERENCE_CYCLES = 50
CYCLE_JUMP_COMPUTED_CYCLES = BASE_CYCLE + 1

HISTORY_CSV = "chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv"
SUMMARY_CSV = "chaboche_vp_v1_cyclic_eps005_50cycles_summary.csv"
OUT_DIR = "stage6_50cycle_jump"

PRED_STATEV_CSV = os.path.join(OUT_DIR, "cycle49_predicted_statev_for_injection.csv")
PRED_STRESS_CSV = os.path.join(OUT_DIR, "cycle49_predicted_stress_for_injection.csv")
ERROR_CSV = os.path.join(OUT_DIR, "cycle49_predicted_vs_exact_error.csv")
REPORT_MD = os.path.join(OUT_DIR, "STAGE6B_PREDICTED_CYCLE49_STATE_REPORT.md")

NSTATEV = 15
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]

ACTIVE_STATEV = set([1, 2, 3, 4, 8, 9, 10])
NEAR_ZERO_STATEV = set([5, 6, 7, 11, 12, 13])
RECOMPUTED_STATEV = set([14])
RESET_STATEV = set([15])

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


def maybe_float(text):
    if text is None or text == "":
        return None
    return float(text)


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
    if index in RECOMPUTED_STATEV:
        return "recomputed_from_predicted_STATEV1"
    if index in RESET_STATEV:
        return "reset_to_zero_for_injection"
    return "first_order_cycle_space"


def predict_statev(rows):
    base = get_cycle_row(rows, BASE_CYCLE)
    window = [row for row in rows if MEAN_START <= row["cycle"] <= MEAN_END]
    predicted = {}
    mean_increments = {}
    for i in range(1, NSTATEV + 1):
        mean_inc = mean([row["Delta_STATEV%d" % i] for row in window])
        mean_increments[i] = mean_inc
        predicted[i] = base["STATEV%d_end" % i] + DELTA_N * mean_inc
    predicted[14] = QISO * (1.0 - math.exp(-BISO * predicted[1]))
    predicted[15] = 0.0
    return predicted, mean_increments, base


def predict_stress(rows):
    base = get_cycle_row(rows, BASE_CYCLE)
    window = [row for row in rows if MEAN_START <= row["cycle"] <= MEAN_END]
    predicted = {}
    mean_increments = {}
    for name in STRESS_COMPONENTS:
        mean_inc = mean([row["Delta_%s" % name] for row in window])
        mean_increments[name] = mean_inc
        predicted[name] = base[name] + DELTA_N * mean_inc
    return predicted, mean_increments, base


def write_predicted_statev(predicted, mean_increments, base):
    fields = ["variable", "value", "base_cycle_value", "mean_increment_cycles_2_to_10", "delta_n", "policy"]
    with csv_open_write(PRED_STATEV_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            writer.writerow({
                "variable": "STATEV%d_end" % i,
                "value": fmt(predicted[i]),
                "base_cycle_value": fmt(base["STATEV%d_end" % i]),
                "mean_increment_cycles_2_to_10": fmt(mean_increments[i]),
                "delta_n": DELTA_N,
                "policy": statev_policy(i),
            })


def write_predicted_stress(predicted, mean_increments, base):
    fields = ["component", "value", "base_cycle_value", "mean_increment_cycles_2_to_10", "delta_n", "policy"]
    with csv_open_write(PRED_STRESS_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name in STRESS_COMPONENTS:
            writer.writerow({
                "component": name,
                "value": fmt(predicted[name]),
                "base_cycle_value": fmt(base[name]),
                "mean_increment_cycles_2_to_10": fmt(mean_increments[name]),
                "delta_n": DELTA_N,
                "policy": "first_order_cycle_space",
            })


def write_error_csv(pred_statev, pred_stress, exact):
    fields = [
        "quantity",
        "predicted_cycle49",
        "exact_cycle49",
        "absolute_error",
        "relative_error",
        "relative_error_percent",
        "policy",
    ]
    rows = []
    for i in range(1, NSTATEV + 1):
        key = "STATEV%d_end" % i
        pred = pred_statev[i]
        exact_value = exact.get(key)
        rows.append({
            "quantity": "STATEV%d" % i,
            "predicted_cycle49": pred,
            "exact_cycle49": exact_value,
            "absolute_error": abs_err(pred, exact_value),
            "relative_error": rel_err(pred, exact_value),
            "relative_error_percent": None if rel_err(pred, exact_value) is None else 100.0 * rel_err(pred, exact_value),
            "policy": statev_policy(i),
        })
    for name in STRESS_COMPONENTS:
        pred = pred_stress[name]
        exact_value = exact.get(name)
        rows.append({
            "quantity": name,
            "predicted_cycle49": pred,
            "exact_cycle49": exact_value,
            "absolute_error": abs_err(pred, exact_value),
            "relative_error": rel_err(pred, exact_value),
            "relative_error_percent": None if rel_err(pred, exact_value) is None else 100.0 * rel_err(pred, exact_value),
            "policy": "first_order_cycle_space",
        })
    with csv_open_write(ERROR_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {}
            for field in fields:
                out[field] = row[field] if field in ("quantity", "policy") else fmt(row[field])
            writer.writerow(out)
    return rows


def row_by_quantity(rows, quantity):
    for row in rows:
        if row["quantity"] == quantity:
            return row
    return None


def write_report(error_rows, summary):
    key_quantities = ["STATEV1", "STATEV2", "STATEV3", "STATEV4", "STATEV8", "STATEV9", "STATEV10", "S11"]
    lines = [
        "# Stage 6B.1 Predicted Cycle-49 State Report",
        "",
        "## Purpose",
        "",
        "This report prepares the predicted cycle-49 state for a larger 50-cycle FE cycle-jump validation. The intended FE test is: cycle-10 data -> predicted cycle-49 state -> one computed continuation cycle -> comparison with explicit cycle-50 reference.",
        "",
        "Exact cycle-49 data from the no-skip 50-cycle reference are used only for validation/error comparison.",
        "",
        "## Method",
        "",
        "- Base cycle: `%d`" % BASE_CYCLE,
        "- Target cycle: `%d`" % TARGET_CYCLE,
        "- DeltaN: `%d`" % DELTA_N,
        "- Actually skipped intermediate FE cycles in the next test: `%d`" % SKIPPED_INTERMEDIATE_CYCLES,
        "- Cycle-jump route computed cycles: `%d` base cycles + `1` continuation cycle = `%d` cycles" % (BASE_CYCLE, CYCLE_JUMP_COMPUTED_CYCLES),
        "- Full no-skip reference cycles: `%d`" % FULL_REFERENCE_CYCLES,
        "- Mean increment window: cycles `%d-%d`" % (MEAN_START, MEAN_END),
        "- Prediction formula: `predicted_cycle49 = value_cycle10 + DeltaN * mean_increment_per_cycle`",
        "- STATEV14 policy: recomputed from predicted STATEV1 using `Q*(1-exp(-b*STATEV1))`",
        "- STATEV15 policy: reset to `0` for injection",
        "",
        "No Abaqus rerun was performed. No UMAT or Abaqus input deck was modified.",
        "",
        "## Key Validation Errors",
        "",
        "| Quantity | Predicted cycle-49 | Exact cycle-49 | Absolute error | Relative error |",
        "|---|---:|---:|---:|---:|",
    ]
    for quantity in key_quantities:
        row = row_by_quantity(error_rows, quantity)
        lines.append("| %s | %s | %s | %s | %s%% |" % (
            quantity,
            fmt(row["predicted_cycle49"]),
            fmt(row["exact_cycle49"]),
            fmt(row["absolute_error"]),
            fmt(row["relative_error_percent"]),
        ))

    statev1 = row_by_quantity(error_rows, "STATEV1")
    s11 = row_by_quantity(error_rows, "S11")
    lines += [
        "",
        "## Cycle-50 Reference for Intended Stage 6B.2 Comparison",
        "",
        "- Final explicit cycle-50 STATEV1: `%s`" % fmt(summary.get("final_STATEV1")),
        "- Final explicit cycle-50 S11: `%s MPa`" % fmt(summary.get("final_S11")),
        "- Final explicit cycle-50 RIGHT_FACE RF1: `%s`" % fmt(summary.get("final_RIGHT_FACE_RF1_SUM")),
        "",
        "## Interpretation",
        "",
        "- Predicted cycle-49 STATEV1 absolute error: `%s`" % fmt(statev1["absolute_error"]),
        "- Predicted cycle-49 STATEV1 relative error: `%s%%`" % fmt(statev1["relative_error_percent"]),
        "- Predicted cycle-49 S11 absolute error: `%s MPa`" % fmt(s11["absolute_error"]),
        "- Predicted cycle-49 S11 relative error: `%s%%`" % fmt(s11["relative_error_percent"]),
        "- Active STATEV components predicted directly: `STATEV1, STATEV2-4, STATEV8-10`",
        "- Near-zero shear components were predicted and flagged: `STATEV5-7, STATEV11-13`",
        "- This is the input-state quality check for Stage 6B.2; the FE injection run should only proceed if these errors are acceptable.",
        "",
        "## Outputs",
        "",
        "- Predicted STATEV CSV: `%s`" % PRED_STATEV_CSV,
        "- Predicted stress CSV: `%s`" % PRED_STRESS_CSV,
        "- Error CSV: `%s`" % ERROR_CSV,
    ]
    with open(REPORT_MD, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    rows = read_cycle_history()
    summary = read_summary()
    exact_cycle49 = get_cycle_row(rows, TARGET_CYCLE)
    pred_statev, statev_mean_inc, statev_base = predict_statev(rows)
    pred_stress, stress_mean_inc, stress_base = predict_stress(rows)

    write_predicted_statev(pred_statev, statev_mean_inc, statev_base)
    write_predicted_stress(pred_stress, stress_mean_inc, stress_base)
    error_rows = write_error_csv(pred_statev, pred_stress, exact_cycle49)
    write_report(error_rows, summary)

    print("Wrote %s" % PRED_STATEV_CSV)
    print("Wrote %s" % PRED_STRESS_CSV)
    print("Wrote %s" % ERROR_CSV)
    print("Wrote %s" % REPORT_MD)


if __name__ == "__main__":
    main()
