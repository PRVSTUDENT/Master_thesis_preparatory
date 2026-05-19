from __future__ import print_function

import argparse
import csv
import os
from datetime import datetime


SUMMARY_FIELDS = [
    "strategy",
    "block_index",
    "base_cycle",
    "target_cycle",
    "continue_to_cycle",
    "delta_N",
    "skipped_intermediate_cycles",
    "recovery_cycles",
    "pre_target_statev1_error_pct",
    "pre_target_s11_error_pct",
    "block_final_statev1_error_pct",
    "block_final_s11_error_pct",
    "block_final_rf1_error_pct",
    "strategy_final_statev1_error_pct",
    "strategy_final_s11_error_pct",
    "strategy_final_rf1_error_pct",
    "outcome",
    "case_dir",
]

STRATEGIES = {
    "jump25": [
        {"base": 10, "target": 500, "continue": 510},
        {"base": 510, "target": 1000, "continue": 1010},
        {"base": 1010, "target": 1500, "continue": 1510},
        {"base": 1510, "target": 1990, "continue": 2000},
    ],
    "jump37": [
        {"base": 10, "target": 740, "continue": 750},
        {"base": 750, "target": 1480, "continue": 1490},
        {"base": 1490, "target": 1990, "continue": 2000},
    ],
    "jump50": [
        {"base": 10, "target": 1000, "continue": 1010},
        {"base": 1010, "target": 1990, "continue": 2000},
    ],
    "jump65": [
        {"base": 10, "target": 1300, "continue": 1310},
        {"base": 1310, "target": 1990, "continue": 2000},
    ],
}


def fmt(value):
    if value is None or value == "":
        return ""
    return "%.12g" % float(value)


def read_first(path):
    with open(path, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            return row
    raise RuntimeError("No rows in %s" % path)


def pre_errors(path):
    statev1 = ""
    s11 = ""
    with open(path, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["quantity"] == "STATEV1":
                statev1 = row["relative_error_percent"]
            elif row["quantity"] == "S11":
                s11 = row["relative_error_percent"]
    return statev1, s11


def outcome(statev, s11, rf1):
    statev = float(statev)
    s11 = float(s11)
    rf1 = float(rf1)
    if statev <= 1.0 and s11 <= 1.0 and rf1 <= 1.0:
        return "accepted_clean_success"
    if statev <= 1.0:
        return "accepted_exploratory_success"
    return "not_accepted"


def read_summary(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as handle:
        return list(csv.DictReader(handle))


def write_summary(path, rows):
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def upsert_row(rows, new_row):
    kept = []
    for row in rows:
        same = row["strategy"] == new_row["strategy"] and row["block_index"] == new_row["block_index"]
        if not same:
            kept.append(row)
    kept.append(new_row)
    return kept


def reference_cycle2000(reference_csv):
    if not os.path.exists(reference_csv):
        return None
    with open(reference_csv, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if int(row["cycle"]) == 2000:
                return row
    return None


def write_report(stage_dir, rows):
    report_path = os.path.join(stage_dir, "STAGE14_BLOCKWISE_REPORT.md")
    reference_csv = os.path.join(
        stage_dir,
        "reference_2000cycles",
        "chaboche_vp_v1_cyclic_eps005_2000cycles_cycle_history.csv",
    )
    ref = reference_cycle2000(reference_csv)

    lines = [
        "# Stage 14 Blockwise Report",
        "",
        "Generated: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "## Purpose",
        "",
        "Repeated, re-anchored blockwise cycle-jump controller for a 2000-cycle Chaboche UMAT problem.",
        "",
        "## Reference Cycle 2000 Values",
        "",
    ]
    if ref:
        lines += [
            "- STATEV1: `%s`" % ref["STATEV1_end"],
            "- S11: `%s`" % ref["S11"],
            "- RF1: `%s`" % ref["RIGHT_FACE_RF1_SUM"],
        ]
    else:
        lines.append("- Pending reference extraction.")

    lines += [
        "",
        "## Strategy Definitions",
        "",
    ]
    for name in ["jump25", "jump37", "jump50", "jump65"]:
        route = "; ".join("%d->%d->%d" % (b["base"], b["target"], b["continue"]) for b in STRATEGIES[name])
        lines.append("- `%s`: %s" % (name, route))

    lines += [
        "",
        "## Block-By-Block Results",
        "",
        "| Strategy | Block | Base | Target | Continue | Pre STATEV1 % | Pre S11 % | Final STATEV1 % | Final S11 % | Final RF1 % | Outcome |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {strategy} | {block_index} | {base_cycle} | {target_cycle} | {continue_to_cycle} | "
            "{pre_target_statev1_error_pct} | {pre_target_s11_error_pct} | {block_final_statev1_error_pct} | "
            "{block_final_s11_error_pct} | {block_final_rf1_error_pct} | {outcome} |".format(**row)
        )

    lines += [
        "",
        "## Final Cycle 2000 Comparison",
        "",
        "| Strategy | STATEV1 % | S11 % | RF1 % | Outcome |",
        "|---|---:|---:|---:|---|",
    ]
    for name in ["jump25", "jump37", "jump50", "jump65"]:
        final_rows = [r for r in rows if r["strategy"] == name and r["continue_to_cycle"] == "2000"]
        if final_rows:
            row = final_rows[-1]
            lines.append(
                "| %s | %s | %s | %s | %s |"
                % (
                    name,
                    row["strategy_final_statev1_error_pct"],
                    row["strategy_final_s11_error_pct"],
                    row["strategy_final_rf1_error_pct"],
                    row["outcome"],
                )
            )

    lines += [
        "",
        "## Scientific Interpretation",
        "",
        "Later blocks use the previous block's actual recovered route history as the prediction base. This tests a true repeated controller rather than independent idealized jumps from the no-skip reference.",
    ]
    with open(report_path, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-dir", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--block-index", type=int, required=True)
    parser.add_argument("--base-cycle", type=int, required=True)
    parser.add_argument("--target-cycle", type=int, required=True)
    parser.add_argument("--continue-to-cycle", type=int, required=True)
    parser.add_argument("--case-dir", required=True)
    args = parser.parse_args()

    pre_csv = os.path.join(args.case_dir, "cycle%d_predicted_vs_reference_error.csv" % args.target_cycle)
    result_csv = os.path.join(args.case_dir, "stage14_%s_block%02d_result.csv" % (args.strategy, args.block_index))
    pre_statev, pre_s11 = pre_errors(pre_csv)
    result = read_first(result_csv)

    final_statev = result["block_final_statev1_error_pct"]
    final_s11 = result["block_final_s11_error_pct"]
    final_rf1 = result["block_final_rf1_error_pct"]
    is_strategy_final = args.continue_to_cycle == 2000
    row_outcome = outcome(final_statev, final_s11, final_rf1) if is_strategy_final else result["outcome"]
    delta_n = args.target_cycle - args.base_cycle

    new_row = {
        "strategy": args.strategy,
        "block_index": str(args.block_index),
        "base_cycle": str(args.base_cycle),
        "target_cycle": str(args.target_cycle),
        "continue_to_cycle": str(args.continue_to_cycle),
        "delta_N": str(delta_n),
        "skipped_intermediate_cycles": str(delta_n - 1),
        "recovery_cycles": str(args.continue_to_cycle - args.target_cycle),
        "pre_target_statev1_error_pct": fmt(pre_statev),
        "pre_target_s11_error_pct": fmt(pre_s11),
        "block_final_statev1_error_pct": fmt(final_statev),
        "block_final_s11_error_pct": fmt(final_s11),
        "block_final_rf1_error_pct": fmt(final_rf1),
        "strategy_final_statev1_error_pct": fmt(final_statev) if is_strategy_final else "",
        "strategy_final_s11_error_pct": fmt(final_s11) if is_strategy_final else "",
        "strategy_final_rf1_error_pct": fmt(final_rf1) if is_strategy_final else "",
        "outcome": row_outcome,
        "case_dir": args.case_dir,
    }

    summary_path = os.path.join(args.stage_dir, "STAGE14_BLOCKWISE_SUMMARY.csv")
    rows = upsert_row(read_summary(summary_path), new_row)
    rows.sort(key=lambda item: (["jump25", "jump37", "jump50", "jump65"].index(item["strategy"]), int(item["block_index"])))
    write_summary(summary_path, rows)
    write_report(args.stage_dir, rows)
    print("Updated %s" % summary_path)


if __name__ == "__main__":
    main()
