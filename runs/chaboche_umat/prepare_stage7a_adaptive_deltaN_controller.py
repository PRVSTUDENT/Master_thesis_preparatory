import csv
import math
import os
import sys


BASE_CYCLE = 10
MEAN_START = 2
MEAN_END = 10
ETA = 0.75
EPS = 1.0e-12
SMALL_FLOOR = 1.0e-12
JUMPMIN = 1
JUMPMAX = 60

HISTORY_CSV = "chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv"
OUT_DIR = "stage7_adaptive_deltaN"
BY_VARIABLE_CSV = os.path.join(OUT_DIR, "stage7a_adaptive_deltaN_by_variable.csv")
SUMMARY_CSV = os.path.join(OUT_DIR, "stage7a_adaptive_deltaN_summary.csv")
REPORT_MD = os.path.join(OUT_DIR, "STAGE7A_ADAPTIVE_DELTAN_CONTROLLER_REPORT.md")

CONTROL_VARIABLES = [
    ("STATEV1", "STATEV1_end", "Delta_STATEV1", 0.02, "accumulated viscoplastic strain p"),
    ("STATEV2", "STATEV2_end", "Delta_STATEV2", 0.05, "backstress X11"),
    ("STATEV3", "STATEV3_end", "Delta_STATEV3", 0.05, "backstress X22"),
    ("STATEV4", "STATEV4_end", "Delta_STATEV4", 0.05, "backstress X33"),
    ("STATEV8", "STATEV8_end", "Delta_STATEV8", 0.05, "viscoplastic strain eps_vp_11"),
    ("STATEV9", "STATEV9_end", "Delta_STATEV9", 0.05, "viscoplastic strain eps_vp_22"),
    ("STATEV10", "STATEV10_end", "Delta_STATEV10", 0.05, "viscoplastic strain eps_vp_33"),
    ("S11", "S11", "Delta_S11", 0.03, "axial residual stress"),
]


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
    filtered = [value for value in values if value is not None]
    return sum(filtered) / float(len(filtered)) if filtered else None


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def read_cycle_history():
    rows = []
    with open(HISTORY_CSV, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed = {"cycle": int(row["cycle"])}
            for key, value in row.items():
                if key != "cycle" and key not in ("step_name", "right_face_node_set"):
                    parsed[key] = maybe_float(value)
            rows.append(parsed)
    return rows


def get_cycle_row(rows, cycle):
    for row in rows:
        if row["cycle"] == cycle:
            return row
    raise KeyError("Missing cycle %s in %s" % (cycle, HISTORY_CSV))


def compute_by_variable(rows):
    base = get_cycle_row(rows, BASE_CYCLE)
    window = [row for row in rows if MEAN_START <= row["cycle"] <= MEAN_END]
    by_variable = []

    for name, value_key, delta_key, tau, meaning in CONTROL_VARIABLES:
        base_value = base[value_key]
        mean_value = mean([row[value_key] for row in window])
        mean_increment = mean([row[delta_key] for row in window])
        scale = max(abs(base_value), abs(mean_value), SMALL_FLOOR)
        admissible_change = tau * scale
        raw_delta_n = ETA * admissible_change / (abs(mean_increment) + EPS)
        delta_n_unclipped = int(math.floor(raw_delta_n))
        delta_n_clipped = clamp(delta_n_unclipped, JUMPMIN, JUMPMAX)
        by_variable.append({
            "variable": name,
            "meaning": meaning,
            "base_cycle": BASE_CYCLE,
            "base_value": base_value,
            "mean_value_cycles_2_to_10": mean_value,
            "mean_per_cycle_increment": mean_increment,
            "tau": tau,
            "scale_S_i": scale,
            "admissible_change_A_i": admissible_change,
            "eta": ETA,
            "eps": EPS,
            "deltaN_raw": raw_delta_n,
            "deltaN_unclipped": delta_n_unclipped,
            "deltaN_clipped": delta_n_clipped,
        })

    return by_variable


def summarize(by_variable):
    controlling = min(by_variable, key=lambda row: row["deltaN_clipped"])
    global_delta_n = controlling["deltaN_clipped"]
    return {
        "base_cycle": BASE_CYCLE,
        "mean_window": "%d-%d" % (MEAN_START, MEAN_END),
        "eta": ETA,
        "eps": EPS,
        "jumpmin": JUMPMIN,
        "jumpmax": JUMPMAX,
        "deltaN_global": global_delta_n,
        "controlling_variable": controlling["variable"],
        "controlling_mean_increment": controlling["mean_per_cycle_increment"],
        "controlling_admissible_change": controlling["admissible_change_A_i"],
        "recommended_target_cycle": BASE_CYCLE + global_delta_n,
        "skipped_intermediate_fe_cycles": max(0, global_delta_n - 1),
    }


def write_by_variable_csv(rows):
    fields = [
        "variable",
        "meaning",
        "base_cycle",
        "base_value",
        "mean_value_cycles_2_to_10",
        "mean_per_cycle_increment",
        "tau",
        "scale_S_i",
        "admissible_change_A_i",
        "eta",
        "eps",
        "deltaN_raw",
        "deltaN_unclipped",
        "deltaN_clipped",
    ]
    with csv_open_write(BY_VARIABLE_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: row[field] if field in ("variable", "meaning", "base_cycle") else fmt(row[field])
                for field in fields
            })


def write_summary_csv(summary):
    with csv_open_write(SUMMARY_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=["quantity", "value"])
        writer.writeheader()
        for key in [
            "base_cycle",
            "mean_window",
            "eta",
            "eps",
            "jumpmin",
            "jumpmax",
            "deltaN_global",
            "controlling_variable",
            "controlling_mean_increment",
            "controlling_admissible_change",
            "recommended_target_cycle",
            "skipped_intermediate_fe_cycles",
        ]:
            writer.writerow({"quantity": key, "value": fmt(summary[key]) if isinstance(summary[key], float) else summary[key]})


def write_report(by_variable, summary):
    lines = [
        "# Stage 7A Adaptive DeltaN Controller Report",
        "",
        "## Purpose",
        "",
        "This report implements a paper-inspired adaptive jump-size estimate for the Chaboche cycle-jump workflow. No damage variable is used. The paper-style damage variable `D` is replaced by generalized control variables `Y_i` based on Chaboche STATEV and stress components.",
        "",
        "No Abaqus run was performed. No UMAT or input deck was modified.",
        "",
        "## Controller Definition",
        "",
        "For each controlled variable `Y_i`, the admissible change is defined as:",
        "",
        "`A_i = tau_i S_i`",
        "",
        "where `S_i = max(|Y_i(N0)|, |mean(Y_i)|, small_floor)`. The paper-style jump estimate is then written as:",
        "",
        "`DeltaN_i = floor(eta A_i / (|mean(Delta Y_i)| + eps))`",
        "",
        "The global jump is controlled by the most restrictive variable:",
        "",
        "`DeltaN = min_i(DeltaN_i)`",
        "",
        "Settings:",
        "",
        "- Base cycle `N0 = %d`" % BASE_CYCLE,
        "- Mean increment window: cycles `%d-%d`" % (MEAN_START, MEAN_END),
        "- Safety factor `eta = %s`" % fmt(ETA),
        "- `eps = %s`" % fmt(EPS),
        "- `JUMPMIN = %d`, `JUMPMAX = %d`" % (JUMPMIN, JUMPMAX),
        "",
        "## Controlled Variables",
        "",
        "| Variable | Meaning | tau | mean Delta Y_i | A_i | DeltaN_i |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in by_variable:
        lines.append("| %s | %s | %s | %s | %s | %d |" % (
            row["variable"],
            row["meaning"],
            fmt(row["tau"]),
            fmt(row["mean_per_cycle_increment"]),
            fmt(row["admissible_change_A_i"]),
            row["deltaN_clipped"],
        ))

    lines += [
        "",
        "## Recommendation",
        "",
        "- Global adaptive DeltaN: `%d`" % summary["deltaN_global"],
        "- Controlling variable: `%s`" % summary["controlling_variable"],
        "- Recommended target cycle: `%d`" % summary["recommended_target_cycle"],
        "- Skipped intermediate FE cycles: `%d`" % summary["skipped_intermediate_fe_cycles"],
        "",
        "## Comparison with Stage 6C Scan",
        "",
        "| Target | DeltaN | Observed Stage 6C decision |",
        "|---:|---:|---|",
        "| 29 | 19 | acceptable exploratory candidate |",
        "| 39 | 29 | not headline candidate |",
        "| 49 | 39 | not headline candidate |",
        "",
        "The adaptive controller should be interpreted as a conservative paper-inspired first estimate. If the recommended DeltaN is below 19, it is stricter than the manual Stage 6C scan. If it is near 19, it agrees with the largest acceptable scan target. If it exceeds 29, it would be less conservative than the observed stress/backstress drift in Stage 6C.",
        "",
    ]
    if summary["deltaN_global"] <= 19:
        lines.append("The computed recommendation is conservative relative to the Stage 6C scan and would not select the non-headline targets 39 or 49.")
    elif summary["deltaN_global"] < 29:
        lines.append("The computed recommendation is close to the Stage 6C acceptable range and remains below the first non-headline target.")
    else:
        lines.append("The computed recommendation is less conservative than the Stage 6C scan; tighter tolerances or a lower safety factor would be needed.")
    lines += [
        "",
        "## Interpretation",
        "",
        "This is a paper-inspired adaptive jump-size controller, not a damage model. It replaces `D` by Chaboche control variables `Y_i` and replaces `DeltaL` by the admissible state-change budget `A_i`. The result supports the thesis observation that scalar `STATEV1` alone permits larger jumps, while stress and backstress consistency restrict physically consistent FE continuation.",
        "",
        "## Outputs",
        "",
        "- Per-variable controller CSV: `%s`" % BY_VARIABLE_CSV,
        "- Summary CSV: `%s`" % SUMMARY_CSV,
    ]
    with open(REPORT_MD, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    rows = read_cycle_history()
    by_variable = compute_by_variable(rows)
    summary = summarize(by_variable)
    write_by_variable_csv(by_variable)
    write_summary_csv(summary)
    write_report(by_variable, summary)
    print("Wrote %s" % BY_VARIABLE_CSV)
    print("Wrote %s" % SUMMARY_CSV)
    print("Wrote %s" % REPORT_MD)


if __name__ == "__main__":
    main()
