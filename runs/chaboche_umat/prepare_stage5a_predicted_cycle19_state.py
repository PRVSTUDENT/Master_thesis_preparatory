from odbAccess import openOdb
import csv
import math
import os
import sys


BASE_CYCLE = 10
TARGET_CYCLE = 19
DELTA_N = TARGET_CYCLE - BASE_CYCLE
MEAN_START = 2
MEAN_END = 10

HISTORY_CSV = "chaboche_v1_full_statev_cycle_history.csv"
ODB_PATH = "chaboche_vp_v1_cyclic_eps005_20cycles.odb"
OUT_DIR = "stage5_predicted_cycle_jump"

EXACT_STATEV_CSV = os.path.join("stage4_injected_cycle_jump", "cycle19_exact_statev_for_injection.csv")
EXACT_STRESS_CSV = os.path.join("stage4_injected_cycle_jump", "cycle19_exact_stress_for_injection.csv")
REF20_STATEV_CSV = os.path.join("stage4_injected_cycle_jump", "cycle20_reference_statev.csv")
REF20_STRESS_CSV = os.path.join("stage4_injected_cycle_jump", "cycle20_reference_stress.csv")

PRED_STATEV_CSV = os.path.join(OUT_DIR, "cycle19_predicted_statev_for_injection.csv")
PRED_STRESS_CSV = os.path.join(OUT_DIR, "cycle19_predicted_stress_for_injection.csv")
ERROR_CSV = os.path.join(OUT_DIR, "cycle19_predicted_vs_exact_error.csv")
REPORT_MD = os.path.join(OUT_DIR, "STAGE5A_PREDICTED_CYCLE19_STATE_REPORT.md")

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


def read_key_value_csv(path, key_field):
    out = {}
    with open(path, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            out[row[key_field]] = float(row["value"])
    return out


def read_statev_history():
    rows = []
    with open(HISTORY_CSV, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed = {"cycle": int(row["cycle"])}
            for i in range(1, NSTATEV + 1):
                parsed["STATEV%d_end" % i] = float(row["STATEV%d_end" % i])
                parsed["Delta_STATEV%d" % i] = float(row["Delta_STATEV%d" % i])
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


def frame_field_average(frame, field_name, count=None):
    if field_name not in frame.fieldOutputs.keys():
        return None
    values = frame.fieldOutputs[field_name].values
    if count is None:
        data = [value.data for value in values]
        return mean(data)

    accum = [0.0] * count
    n = 0
    for value in values:
        for i in range(count):
            accum[i] += value.data[i]
        n += 1
    if n == 0:
        return [None] * count
    return [item / float(n) for item in accum]


def extract_stress_history():
    odb = openOdb(ODB_PATH, readOnly=True)
    rows = []
    try:
        frames = []
        for step_name in odb.steps.keys():
            step = odb.steps[step_name]
            for frame in step.frames:
                frames.append((frame.frameValue, frame))
        frames.sort(key=lambda item: item[0])

        previous = None
        for cycle in range(1, 21):
            nearest_time, frame = min(frames, key=lambda item: abs(item[0] - float(cycle)))
            stress = frame_field_average(frame, "S", len(STRESS_COMPONENTS))
            row = {
                "cycle": cycle,
                "time": nearest_time,
                "target_time": float(cycle),
                "time_error": nearest_time - float(cycle),
            }
            for name, value in zip(STRESS_COMPONENTS, stress):
                row[name] = value
                row["Delta_%s" % name] = None if previous is None else value - previous[name]
            rows.append(row)
            previous = row
    finally:
        odb.close()
    return rows


def predict_stress(rows):
    base = None
    for row in rows:
        if row["cycle"] == BASE_CYCLE:
            base = row
            break
    if base is None:
        raise KeyError("Missing stress cycle %s" % BASE_CYCLE)
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


def write_error_csv(pred_statev, pred_stress, exact_statev, exact_stress):
    fields = [
        "quantity",
        "predicted_cycle19",
        "exact_cycle19",
        "absolute_error",
        "relative_error",
        "relative_error_percent",
        "policy",
    ]
    rows = []
    for i in range(1, NSTATEV + 1):
        key = "STATEV%d_end" % i
        pred = pred_statev[i]
        exact = exact_statev.get(key)
        rows.append({
            "quantity": "STATEV%d" % i,
            "predicted_cycle19": pred,
            "exact_cycle19": exact,
            "absolute_error": abs_err(pred, exact),
            "relative_error": rel_err(pred, exact),
            "relative_error_percent": None if rel_err(pred, exact) is None else 100.0 * rel_err(pred, exact),
            "policy": statev_policy(i),
        })
    for name in STRESS_COMPONENTS:
        pred = pred_stress[name]
        exact = exact_stress.get(name)
        rows.append({
            "quantity": name,
            "predicted_cycle19": pred,
            "exact_cycle19": exact,
            "absolute_error": abs_err(pred, exact),
            "relative_error": rel_err(pred, exact),
            "relative_error_percent": None if rel_err(pred, exact) is None else 100.0 * rel_err(pred, exact),
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


def write_report(error_rows, pred_statev, pred_stress):
    key_quantities = ["STATEV1", "STATEV2", "STATEV3", "STATEV4", "STATEV8", "STATEV9", "STATEV10", "S11"]
    lines = [
        "# Stage 5A Predicted Cycle-19 State Report",
        "",
        "## Purpose",
        "",
        "This report prepares the first predicted cycle-jump state for Abaqus FE cycle skipping. It predicts cycle-19 STATEV and residual stress from cycle-10 data using a cycle-level first-order extrapolation.",
        "",
        "Exact cycle-19 data are used only for validation/error comparison, not for prediction.",
        "",
        "## Method",
        "",
        "- Base cycle: `%d`" % BASE_CYCLE,
        "- Target cycle: `%d`" % TARGET_CYCLE,
        "- DeltaN: `%d`" % DELTA_N,
        "- Mean increment window: cycles `%d-%d`" % (MEAN_START, MEAN_END),
        "- Prediction formula: `predicted_cycle19 = value_cycle10 + DeltaN * mean_increment_per_cycle`",
        "- STATEV14 policy: recomputed from predicted STATEV1 using `Q*(1-exp(-b*STATEV1))`",
        "- STATEV15 policy: reset to `0` for injection",
        "",
        "No Abaqus rerun was performed. No UMAT was modified.",
        "",
        "## Key Validation Errors",
        "",
        "| Quantity | Predicted cycle-19 | Exact cycle-19 | Absolute error | Relative error |",
        "|---|---:|---:|---:|---:|",
    ]
    for quantity in key_quantities:
        row = row_by_quantity(error_rows, quantity)
        lines.append("| %s | %s | %s | %s | %s%% |" % (
            quantity,
            fmt(row["predicted_cycle19"]),
            fmt(row["exact_cycle19"]),
            fmt(row["absolute_error"]),
            fmt(row["relative_error_percent"]),
        ))

    s11 = row_by_quantity(error_rows, "S11")
    statev1 = row_by_quantity(error_rows, "STATEV1")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Predicted STATEV1 absolute error: `%s`" % fmt(statev1["absolute_error"]),
        "- Predicted STATEV1 relative error: `%s%%`" % fmt(statev1["relative_error_percent"]),
        "- Predicted S11 absolute error: `%s MPa`" % fmt(s11["absolute_error"]),
        "- Predicted S11 relative error: `%s%%`" % fmt(s11["relative_error_percent"]),
        "- Active STATEV components predicted directly: `STATEV1, STATEV2-4, STATEV8-10`",
        "- Near-zero shear components were predicted and flagged: `STATEV5-7, STATEV11-13`",
        "- This predicted state is the candidate input for the next FE skipped-cycle continuation test.",
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

    statev_rows = read_statev_history()
    pred_statev, statev_mean_inc, statev_base = predict_statev(statev_rows)

    stress_rows = extract_stress_history()
    pred_stress, stress_mean_inc, stress_base = predict_stress(stress_rows)

    exact_statev = read_key_value_csv(EXACT_STATEV_CSV, "variable")
    exact_stress = read_key_value_csv(EXACT_STRESS_CSV, "component")

    write_predicted_statev(pred_statev, statev_mean_inc, statev_base)
    write_predicted_stress(pred_stress, stress_mean_inc, stress_base)
    error_rows = write_error_csv(pred_statev, pred_stress, exact_statev, exact_stress)
    write_report(error_rows, pred_statev, pred_stress)

    print("Wrote %s" % PRED_STATEV_CSV)
    print("Wrote %s" % PRED_STRESS_CSV)
    print("Wrote %s" % ERROR_CSV)
    print("Wrote %s" % REPORT_MD)


if __name__ == "__main__":
    main()
