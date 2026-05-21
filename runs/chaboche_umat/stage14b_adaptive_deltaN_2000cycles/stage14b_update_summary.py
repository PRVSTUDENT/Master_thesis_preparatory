from __future__ import print_function

import argparse
import csv
import os
from datetime import datetime


HISTORY_FIELDS = [
    "block_id", "base_cycle", "target_cycle", "recovery_end_cycle", "DeltaN",
    "raw_formula_DeltaN", "m_STATEV1", "c_STATEV1", "estimated_local_error_STATEV1_percent",
    "base_STATEV1", "predicted_target_STATEV1", "recovered_end_STATEV1", "final_status",
    "block_final_s11_error_pct", "block_final_rf1_error_pct", "case_dir",
]

SUMMARY_FIELDS = [
    "final_cycle", "final_STATEV1", "reference_STATEV1", "final_statev1_error_pct",
    "final_S11", "reference_S11", "final_s11_error_pct",
    "final_RIGHT_FACE_RF1_SUM", "reference_RIGHT_FACE_RF1_SUM", "final_rf1_error_pct",
    "outcome", "number_of_blocks", "solved_recovery_cycles", "skipped_cycles",
    "effective_speedup_estimate", "best_fixed_stage14_statev1_error_pct",
    "best_fixed_stage14_strategy",
]


def csv_open_write(path):
    return open(path, "w", newline="")


def fmt(value):
    if value is None or value == "":
        return ""
    return "%.12g" % float(value)


def read_first(path):
    with open(path, "r") as handle:
        for row in csv.DictReader(handle):
            return row
    raise RuntimeError("No rows in %s" % path)


def read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, fields, rows):
    with csv_open_write(path) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict((field, row.get(field, "")) for field in fields))


def outcome(statev, s11, rf1):
    statev = float(statev)
    s11 = float(s11)
    rf1 = float(rf1)
    if statev <= 1.0 and s11 <= 1.0 and rf1 <= 1.0:
        return "accepted_clean_success"
    if statev <= 1.0:
        return "accepted_exploratory_success"
    return "not_accepted"


def upsert(rows, row):
    kept = [old for old in rows if old.get("block_id") != row.get("block_id")]
    kept.append(row)
    kept.sort(key=lambda item: int(item["block_id"]))
    return kept


def best_fixed_stage14(stage_dir):
    path = os.path.join(os.path.dirname(stage_dir), "stage14_blockwise_jump_2000cycles", "STAGE14_BLOCKWISE_SUMMARY.csv")
    best_strategy = ""
    best_error = ""
    if not os.path.exists(path):
        return best_strategy, best_error
    with open(path, "r") as handle:
        for row in csv.DictReader(handle):
            if row.get("continue_to_cycle") != "2000" or not row.get("strategy_final_statev1_error_pct"):
                continue
            value = float(row["strategy_final_statev1_error_pct"])
            if best_error == "" or value < float(best_error):
                best_error = row["strategy_final_statev1_error_pct"]
                best_strategy = row["strategy"]
    return best_strategy, best_error


def write_report(stage_dir, history_rows, summary_row):
    report_path = os.path.join(stage_dir, "STAGE14B_ADAPTIVE_REPORT.md")
    lines = [
        "# Stage 14B Adaptive DeltaN Report",
        "",
        "Generated: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "## Method",
        "",
        "Adaptive blockwise cycle jumping with Abaqus/Standard recovery windows. DeltaN is selected from a local STATEV1 curvature estimate, then limited by safety factor and min/max bounds.",
        "",
        "## Final Summary",
        "",
    ]
    for field in SUMMARY_FIELDS:
        lines.append("- %s: `%s`" % (field, summary_row.get(field, "")))
    lines += [
        "",
        "## Block History",
        "",
        "| Block | Base | Target | Recovery End | DeltaN | m STATEV1 | c STATEV1 | Est. local err % | Recovered STATEV1 | Status |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in history_rows:
        lines.append(
            "| {block_id} | {base_cycle} | {target_cycle} | {recovery_end_cycle} | {DeltaN} | "
            "{m_STATEV1} | {c_STATEV1} | {estimated_local_error_STATEV1_percent} | "
            "{recovered_end_STATEV1} | {final_status} |".format(**row)
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "Compare this adaptive run against the completed fixed Stage 14 strategies. If STATEV1 remains above 1%, the limiting factor is likely recovery-window length, linear state prediction, or reinjection transient rather than only fixed DeltaN selection.",
    ]
    with open(report_path, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-dir", required=True)
    parser.add_argument("--metadata", required=True)
    args = parser.parse_args()

    meta = read_first(args.metadata)
    result = read_first(meta["result_csv"])
    block_status = result["outcome"]
    history_row = {
        "block_id": meta["block_id"],
        "base_cycle": meta["base_cycle"],
        "target_cycle": meta["target_cycle"],
        "recovery_end_cycle": meta["recovery_end_cycle"],
        "DeltaN": meta["DeltaN"],
        "raw_formula_DeltaN": meta["raw_formula_DeltaN"],
        "m_STATEV1": fmt(meta["m_STATEV1"]),
        "c_STATEV1": fmt(meta["c_STATEV1"]),
        "estimated_local_error_STATEV1_percent": fmt(meta["estimated_local_error_STATEV1_percent"]),
        "base_STATEV1": fmt(meta["base_STATEV1"]),
        "predicted_target_STATEV1": fmt(meta["predicted_target_STATEV1"]),
        "recovered_end_STATEV1": fmt(result["block_final_STATEV1"]),
        "final_status": block_status,
        "block_final_s11_error_pct": fmt(result["block_final_s11_error_pct"]),
        "block_final_rf1_error_pct": fmt(result["block_final_rf1_error_pct"]),
        "case_dir": meta["case_dir"],
    }

    history_path = os.path.join(args.stage_dir, "STAGE14B_ADAPTIVE_BLOCK_HISTORY.csv")
    history_rows = upsert(read_rows(history_path), history_row)
    write_rows(history_path, HISTORY_FIELDS, history_rows)

    final = history_rows[-1]
    final_result = read_first(os.path.join(final["case_dir"], "stage14b_adaptive_block%02d_result.csv" % int(final["block_id"])))
    statev = final_result["block_final_statev1_error_pct"]
    s11 = final_result["block_final_s11_error_pct"]
    rf1 = final_result["block_final_rf1_error_pct"]
    solved_recovery = sum(int(row["recovery_end_cycle"]) - int(row["target_cycle"]) for row in history_rows)
    skipped = sum(int(row["DeltaN"]) - 1 for row in history_rows)
    solved_total = 10 + solved_recovery
    speedup = 2000.0 / float(solved_total) if solved_total > 0 else 0.0
    best_strategy, best_error = best_fixed_stage14(args.stage_dir)
    summary_row = {
        "final_cycle": final["recovery_end_cycle"],
        "final_STATEV1": fmt(final_result["block_final_STATEV1"]),
        "reference_STATEV1": fmt(final_result["reference_STATEV1"]),
        "final_statev1_error_pct": fmt(statev),
        "final_S11": fmt(final_result["block_final_S11"]),
        "reference_S11": fmt(final_result["reference_S11"]),
        "final_s11_error_pct": fmt(s11),
        "final_RIGHT_FACE_RF1_SUM": fmt(final_result["block_final_RIGHT_FACE_RF1_SUM"]),
        "reference_RIGHT_FACE_RF1_SUM": fmt(final_result["reference_RIGHT_FACE_RF1_SUM"]),
        "final_rf1_error_pct": fmt(rf1),
        "outcome": outcome(statev, s11, rf1) if final["recovery_end_cycle"] == "2000" else "in_progress",
        "number_of_blocks": str(len(history_rows)),
        "solved_recovery_cycles": str(solved_recovery),
        "skipped_cycles": str(skipped),
        "effective_speedup_estimate": fmt(speedup),
        "best_fixed_stage14_statev1_error_pct": fmt(best_error) if best_error else "",
        "best_fixed_stage14_strategy": best_strategy,
    }
    summary_path = os.path.join(args.stage_dir, "STAGE14B_ADAPTIVE_SUMMARY.csv")
    write_rows(summary_path, SUMMARY_FIELDS, [summary_row])
    write_report(args.stage_dir, history_rows, summary_row)
    print("Updated %s" % history_path)
    print("Updated %s" % summary_path)


if __name__ == "__main__":
    main()
