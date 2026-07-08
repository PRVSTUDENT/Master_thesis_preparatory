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
BY_VARIABLE_CSV = os.path.join(OUT_DIR, "stage7b_grouped_adaptive_deltaN_by_variable.csv")
SUMMARY_CSV = os.path.join(OUT_DIR, "stage7b_grouped_adaptive_deltaN_summary.csv")
REPORT_MD = os.path.join(OUT_DIR, "STAGE7B_GROUPED_ADAPTIVE_DELTAN_CONTROLLER_REPORT.md")

SCANNED_TARGETS = [29, 39, 49]

CONTROL_VARIABLES = [
    ("STATEV1", "STATEV1_end", "Delta_STATEV1", 0.02, "accuracy_monitor", "accumulated viscoplastic strain p"),
    ("STATEV2", "STATEV2_end", "Delta_STATEV2", 0.05, "restart_state", "backstress X11"),
    ("STATEV3", "STATEV3_end", "Delta_STATEV3", 0.05, "restart_state", "backstress X22"),
    ("STATEV4", "STATEV4_end", "Delta_STATEV4", 0.05, "restart_state", "backstress X33"),
    ("STATEV8", "STATEV8_end", "Delta_STATEV8", 0.05, "restart_state", "viscoplastic strain eps_vp_11"),
    ("STATEV9", "STATEV9_end", "Delta_STATEV9", 0.05, "restart_state", "viscoplastic strain eps_vp_22"),
    ("STATEV10", "STATEV10_end", "Delta_STATEV10", 0.05, "restart_state", "viscoplastic strain eps_vp_33"),
    ("S11", "S11", "Delta_S11", 0.03, "stress_consistency", "axial residual stress"),
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

    for name, value_key, delta_key, tau, group, meaning in CONTROL_VARIABLES:
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
            "group": group,
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
            "included_in_restart_minimum": group in ("restart_state", "stress_consistency"),
        })

    return by_variable


def nearest_scanned_target(target_cycle):
    return min(SCANNED_TARGETS, key=lambda target: abs(target - target_cycle))


def summarize(by_variable):
    restart_rows = [row for row in by_variable if row["included_in_restart_minimum"]]
    monitor_rows = [row for row in by_variable if row["group"] == "accuracy_monitor"]
    controlling = min(restart_rows, key=lambda row: row["deltaN_clipped"])
    monitor = monitor_rows[0]
    delta_n_restart = controlling["deltaN_clipped"]
    recommended_target_cycle = BASE_CYCLE + delta_n_restart
    nearest_target = nearest_scanned_target(recommended_target_cycle)

    return {
        "base_cycle": BASE_CYCLE,
        "mean_window": "%d-%d" % (MEAN_START, MEAN_END),
        "eta": ETA,
        "eps": EPS,
        "jumpmin": JUMPMIN,
        "jumpmax": JUMPMAX,
        "deltaN_restart": delta_n_restart,
        "controlling_restart_variable": controlling["variable"],
        "controlling_restart_group": controlling["group"],
        "controlling_mean_increment": controlling["mean_per_cycle_increment"],
        "controlling_admissible_change": controlling["admissible_change_A_i"],
        "statev1_monitor_deltaN": monitor["deltaN_clipped"],
        "statev1_monitor_mean_increment": monitor["mean_per_cycle_increment"],
        "statev1_monitor_admissible_change": monitor["admissible_change_A_i"],
        "recommended_target_cycle": recommended_target_cycle,
        "skipped_intermediate_fe_cycles": max(0, delta_n_restart - 1),
        "nearest_scanned_target": nearest_target,
        "nearest_scanned_deltaN": nearest_target - BASE_CYCLE,
    }


def write_by_variable_csv(rows):
    fields = [
        "variable",
        "group",
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
        "included_in_restart_minimum",
    ]
    with csv_open_write(BY_VARIABLE_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: row[field] if field in ("variable", "group", "meaning", "base_cycle", "included_in_restart_minimum") else fmt(row[field])
                for field in fields
            })


def write_summary_csv(summary):
    keys = [
        "base_cycle",
        "mean_window",
        "eta",
        "eps",
        "jumpmin",
        "jumpmax",
        "deltaN_restart",
        "controlling_restart_variable",
        "controlling_restart_group",
        "controlling_mean_increment",
        "controlling_admissible_change",
        "statev1_monitor_deltaN",
        "statev1_monitor_mean_increment",
        "statev1_monitor_admissible_change",
        "recommended_target_cycle",
        "skipped_intermediate_fe_cycles",
        "nearest_scanned_target",
        "nearest_scanned_deltaN",
    ]
    with csv_open_write(SUMMARY_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=["quantity", "value"])
        writer.writeheader()
        for key in keys:
            value = summary[key]
            writer.writerow({"quantity": key, "value": fmt(value) if isinstance(value, float) else value})


def grouped_minimum(rows, group):
    return min([row["deltaN_clipped"] for row in rows if row["group"] == group])


def write_report(by_variable, summary):
    restart_state_delta = grouped_minimum(by_variable, "restart_state")
    stress_delta = grouped_minimum(by_variable, "stress_consistency")
    monitor_delta = grouped_minimum(by_variable, "accuracy_monitor")

    lines = [
        "# Stage 7B Grouped Adaptive DeltaN Controller Report",
        "",
        "## Purpose",
        "",
        "This report refines the Stage 7A paper-inspired adaptive jump-size estimate by grouping Chaboche state quantities according to their role in restart continuation. The accumulated scalar `STATEV1 = p` is retained as an accuracy monitor, but it is not allowed to control the global restart jump size.",
        "",
        "No Abaqus run was performed. No UMAT or input deck was modified.",
        "",
        "## Notation",
        "",
        "The damage variable `D` from the original cycle-jump formulation is not used here because the present UMAT is a Chaboche viscoplasticity implementation, not a damage model. It is replaced by a generic cycle-control quantity `Y_i`, where `Y_i` may be accumulated viscoplastic strain, backstress, viscoplastic strain tensor, or residual stress.",
        "",
        "The paper-style load-cycle increment notation `DeltaL` is replaced by `A_i`, the admissible state change for each control variable:",
        "",
        "`A_i = tau_i S_i`",
        "",
        "with `S_i = max(|Y_i(N0)|, |mean(Y_i)|, small_floor)`. The per-variable estimate is:",
        "",
        "`DeltaN_i = floor(eta A_i / (|mean(Delta Y_i)| + eps))`",
        "",
        "The grouped restart recommendation is:",
        "",
        "`DeltaN_restart = min(DeltaN_X, DeltaN_eps_vp, DeltaN_S)`",
        "",
        "`STATEV1 = p` is evaluated afterward as a scalar cumulative accuracy monitor.",
        "",
        "Settings:",
        "",
        "- Base cycle `N0 = %d`" % BASE_CYCLE,
        "- Mean increment window: cycles `%d-%d`" % (MEAN_START, MEAN_END),
        "- Safety factor `eta = %s`" % fmt(ETA),
        "- `eps = %s`" % fmt(EPS),
        "- `JUMPMIN = %d`, `JUMPMAX = %d`" % (JUMPMIN, JUMPMAX),
        "",
        "## Variable Groups",
        "",
        "| Group | Role | Variables | Included in restart minimum? |",
        "|---|---|---|---|",
        "| A | Accuracy monitor | `STATEV1 = p` | no |",
        "| B | Restart-state controller | `STATEV2-4`, `STATEV8-10` | yes |",
        "| C | Stress consistency controller | `S11` | yes |",
        "",
        "## Per-Variable Results",
        "",
        "| Variable | Group | Meaning | tau | mean Delta Y_i | A_i | DeltaN_i | Restart minimum |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in by_variable:
        lines.append("| %s | %s | %s | %s | %s | %s | %d | %s |" % (
            row["variable"],
            row["group"],
            row["meaning"],
            fmt(row["tau"]),
            fmt(row["mean_per_cycle_increment"]),
            fmt(row["admissible_change_A_i"]),
            row["deltaN_clipped"],
            "yes" if row["included_in_restart_minimum"] else "no",
        ))

    lines += [
        "",
        "## Grouped Recommendation",
        "",
        "- `STATEV1` monitor DeltaN: `%d`" % monitor_delta,
        "- Restart-state controller minimum (`STATEV2-4`, `STATEV8-10`): `%d`" % restart_state_delta,
        "- Stress consistency controller (`S11`): `%d`" % stress_delta,
        "- Grouped restart DeltaN: `%d`" % summary["deltaN_restart"],
        "- Controlling restart variable: `%s`" % summary["controlling_restart_variable"],
        "- Recommended target cycle: `%d`" % summary["recommended_target_cycle"],
        "- Skipped intermediate FE cycles: `%d`" % summary["skipped_intermediate_fe_cycles"],
        "- Nearest scanned Stage 6C target: `%d` (DeltaN `%d`)" % (summary["nearest_scanned_target"], summary["nearest_scanned_deltaN"]),
        "",
        "With the Stage 7A values, excluding the cumulative monitor gives:",
        "",
        "`min(STATEV2-4, STATEV8-10, S11) = min(17, 43, 23) = 17`",
        "",
        "## Validation Context",
        "",
        "| Reference | DeltaN | Outcome |",
        "|---|---:|---|",
        "| Stage 5B clean jump | 9 | clean success |",
        "| Stage 6C target 29 scan | 19 | acceptable exploratory candidate |",
        "| Stage 6D cycle-29 FE continuation | 19 | acceptable exploratory success |",
        "| Stage 6C targets 39/49 | 29/39 | not headline candidates |",
        "",
        "The grouped recommendation `DeltaN_restart = %d` is close to the validated Stage 6D exploratory jump `DeltaN = 19`, while remaining slightly more conservative. It also avoids the Stage 7A failure mode where cumulative `p` alone forced `DeltaN = 1` despite being one of the most accurately predicted quantities in the FE validation." % summary["deltaN_restart"],
        "",
        "Stage 6D reported `STATEV1` final relative error `0.0458269043313%` and `S11` final relative error `2.34365652874%`, confirming that the scalar cumulative variable can remain accurate while stress consistency becomes the practical limiter.",
        "",
        "## Thesis Wording",
        "",
        "In the present Chaboche implementation, the damage variable D of the original cycle-jump formulation is replaced by a generalized state-control variable Y_i. The admissible jump is then governed by a prescribed admissible change A_i = tau_i S_i. Because accumulated viscoplastic strain p is cumulative and accurately predicted over large jumps, it is used as an accuracy monitor, while the global jump size is controlled by backstress, viscoplastic strain tensor, and residual stress consistency.",
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
    print("Grouped restart DeltaN: %d" % summary["deltaN_restart"])
    print("Recommended target cycle: %d" % summary["recommended_target_cycle"])


if __name__ == "__main__":
    main()
