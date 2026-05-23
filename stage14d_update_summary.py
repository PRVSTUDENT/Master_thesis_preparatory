from __future__ import print_function

import argparse
import csv
import os
from datetime import datetime


HISTORY_FIELDS = [
    "case_id", "block_id", "base_cycle", "target_cycle", "recovery_end_cycle", "DeltaN",
    "raw_formula_DeltaN", "m_STATEV1", "c_STATEV1", "estimated_local_error_STATEV1_percent",
    "base_STATEV1", "predicted_target_STATEV1", "recovered_end_STATEV1", "final_status",
    "block_final_s11_error_pct", "block_final_rf1_error_pct", "case_dir",
    "LOCAL_TOL", "SAFETY_FACTOR", "DN_MIN", "DN_MAX", "RECOVERY_WINDOW",
    "prediction_order", "deltaN_control_variables", "injection_mode", "rollback_enabled",
]

SUMMARY_FIELDS = [
    "case_id", "case_group", "config_name",
    "LOCAL_TOL", "SAFETY_FACTOR", "DN_MIN", "DN_MAX", "RECOVERY_WINDOW",
    "prediction_order", "deltaN_control_variables", "injection_mode",
    "rollback_enabled", "final_cycle", "final_STATEV1", "reference_STATEV1", "final_statev1_error_pct",
    "final_S11", "reference_S11", "final_s11_error_pct",
    "final_RIGHT_FACE_RF1_SUM", "reference_RIGHT_FACE_RF1_SUM", "final_rf1_error_pct",
    "outcome", "number_of_blocks", "solved_recovery_cycles", "skipped_cycles",
    "effective_speedup_estimate", "first_failed_block", "first_failed_base_cycle",
    "first_failed_target_cycle", "first_failed_recovery_end_cycle", "max_m_STATEV1",
    "max_c_STATEV1", "notes",
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
    kept = [old for old in rows if not (old.get("case_id") == row.get("case_id") and old.get("block_id") == row.get("block_id"))]
    kept.append(row)
    kept.sort(key=lambda item: (item.get("case_id", ""), int(item["block_id"])))
    return kept


def write_report(stage_dir, history_rows, summary_rows):
    report_path = os.path.join(stage_dir, "STAGE14D_24H_REPORT.md")
    clean_by_speed = sorted(
        [row for row in summary_rows if row.get("outcome") == "accepted_clean_success"],
        key=lambda row: -float(row.get("effective_speedup_estimate") or 0.0),
    )
    clean_by_accuracy = sorted(
        [row for row in summary_rows if row.get("outcome") == "accepted_clean_success"],
        key=lambda row: float(row.get("final_statev1_error_pct") or 1.0e99),
    )
    exploratory = sorted(
        [row for row in summary_rows if row.get("outcome") == "accepted_exploratory_success"],
        key=lambda row: float(row.get("final_statev1_error_pct") or 1.0e99),
    )
    not_accepted = sorted(
        [row for row in summary_rows if row.get("outcome") == "not_accepted"],
        key=lambda row: float(row.get("final_statev1_error_pct") or 1.0e99),
    )
    runtime_errors = sorted(
        [row for row in summary_rows if row.get("outcome") == "runtime_error"],
        key=lambda row: row.get("case_id", ""),
    )
    lines = [
        "# Stage 14D Adaptive Sweep Report",
        "",
        "Generated: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "## Method",
        "",
        "Configurable adaptive blockwise cycle jumping with Abaqus/Standard recovery windows. This report is updated after each finished case or sanity block.",
        "",
        "## Accepted Clean Success - Fastest First",
        "",
        "| Rank | Case | Outcome | Final Cycle | STATEV1 Error % | S11 Error % | RF1 Error % | Speed-up |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    def append_table(rows):
        for index, row in enumerate(rows, 1):
            lines.append(
                "| %d | %s | %s | %s | %s | %s | %s | %s |"
                % (
                    index,
                    row.get("case_id", ""),
                    row.get("outcome", ""),
                    row.get("final_cycle", ""),
                    row.get("final_statev1_error_pct", ""),
                    row.get("final_s11_error_pct", ""),
                    row.get("final_rf1_error_pct", ""),
                    row.get("effective_speedup_estimate", ""),
                )
            )
    append_table(clean_by_speed)
    lines += [
        "",
        "## Accepted Clean Success - Lowest STATEV1 Error",
        "",
        "| Rank | Case | Outcome | Final Cycle | STATEV1 Error % | S11 Error % | RF1 Error % | Speed-up |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    append_table(clean_by_accuracy)
    lines += [
        "",
        "## Accepted Exploratory Success",
        "",
        "| Rank | Case | Outcome | Final Cycle | STATEV1 Error % | S11 Error % | RF1 Error % | Speed-up |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    append_table(exploratory)
    lines += [
        "",
        "## Not Accepted - Lowest STATEV1 Error",
        "",
        "| Rank | Case | Outcome | Final Cycle | STATEV1 Error % | S11 Error % | RF1 Error % | Speed-up |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    append_table(not_accepted)
    lines += [
        "",
        "## Runtime Errors",
        "",
        "| Case | Notes |",
        "|---|---|",
    ]
    for row in runtime_errors:
        lines.append(
            "| %s | %s |" % (row.get("case_id", ""), row.get("notes", ""))
        )
    lines += [
        "",
        "## Latest Block History",
        "",
        "| Case | Block | Base | Target | Recovery End | DeltaN | Recovered STATEV1 | Status |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in history_rows:
        lines.append(
            "| {case_id} | {block_id} | {base_cycle} | {target_cycle} | {recovery_end_cycle} | {DeltaN} | "
            "{recovered_end_STATEV1} | {final_status} |".format(**row)
        )
    lines += [
        "",
        "## Baselines",
        "",
        "- Stage 14 fixed best: jump25, STATEV1 error about 2.85226684954%.",
        "- Stage 14B adaptive: STATEV1 error 124.209089872%.",
        "- Stage 14C best accuracy: X06, STATEV1 error 0.0418369623642%, speed-up 1.88501413761x.",
        "- Stage 14C fastest accepted: D4, STATEV1 error 0.886575562466%, speed-up 3.59066427289x.",
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
    case_id = os.path.basename(os.path.dirname(meta["case_dir"])).replace("strategy_", "")
    history_row = {
        "case_id": case_id,
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
        "LOCAL_TOL": meta.get("LOCAL_TOL", ""),
        "SAFETY_FACTOR": meta.get("SAFETY_FACTOR", ""),
        "DN_MIN": meta.get("DN_MIN", ""),
        "DN_MAX": meta.get("DN_MAX", ""),
        "RECOVERY_WINDOW": meta.get("RECOVERY_WINDOW", ""),
        "prediction_order": meta.get("prediction_order", ""),
        "deltaN_control_variables": meta.get("deltaN_control_variables", ""),
        "injection_mode": meta.get("injection_mode", ""),
        "rollback_enabled": meta.get("rollback_enabled", "false"),
    }

    history_path = os.path.join(args.stage_dir, "STAGE14D_24H_BLOCK_HISTORY.csv")
    history_rows = upsert(read_rows(history_path), history_row)
    write_rows(history_path, HISTORY_FIELDS, history_rows)

    case_rows = [row for row in history_rows if row.get("case_id") == case_id]
    final = case_rows[-1]
    final_result = read_first(os.path.join(final["case_dir"], "stage14d_%s_block%02d_result.csv" % (case_id, int(final["block_id"]))))
    statev = final_result["block_final_statev1_error_pct"]
    s11 = final_result["block_final_s11_error_pct"]
    rf1 = final_result["block_final_rf1_error_pct"]
    solved_recovery = sum(int(row["recovery_end_cycle"]) - int(row["target_cycle"]) for row in case_rows)
    skipped = sum(int(row["DeltaN"]) - 1 for row in case_rows)
    solved_total = 10 + solved_recovery
    speedup = 2000.0 / float(solved_total) if solved_total > 0 else 0.0
    failed_rows = [row for row in case_rows if row.get("final_status") == "not_accepted"]
    first_failed = failed_rows[0] if failed_rows else {}
    summary_row = {
        "case_id": case_id,
        "case_group": case_id[0] if case_id else "",
        "config_name": case_id,
        "LOCAL_TOL": final.get("LOCAL_TOL", ""),
        "SAFETY_FACTOR": final.get("SAFETY_FACTOR", ""),
        "DN_MIN": final.get("DN_MIN", ""),
        "DN_MAX": final.get("DN_MAX", ""),
        "RECOVERY_WINDOW": final.get("RECOVERY_WINDOW", ""),
        "prediction_order": final.get("prediction_order", ""),
        "deltaN_control_variables": final.get("deltaN_control_variables", ""),
        "injection_mode": final.get("injection_mode", ""),
        "rollback_enabled": final.get("rollback_enabled", "false"),
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
        "number_of_blocks": str(len(case_rows)),
        "solved_recovery_cycles": str(solved_recovery),
        "skipped_cycles": str(skipped),
        "effective_speedup_estimate": fmt(speedup),
        "first_failed_block": first_failed.get("block_id", ""),
        "first_failed_base_cycle": first_failed.get("base_cycle", ""),
        "first_failed_target_cycle": first_failed.get("target_cycle", ""),
        "first_failed_recovery_end_cycle": first_failed.get("recovery_end_cycle", ""),
        "max_m_STATEV1": fmt(max([float(row["m_STATEV1"]) for row in case_rows if row.get("m_STATEV1")], default=0.0)),
        "max_c_STATEV1": fmt(max([abs(float(row["c_STATEV1"])) for row in case_rows if row.get("c_STATEV1")], default=0.0)),
        "notes": "updated_after_block_%s" % final["block_id"],
    }
    summary_path = os.path.join(args.stage_dir, "STAGE14D_24H_CASE_SUMMARY.csv")
    summary_rows = [row for row in read_rows(summary_path) if row.get("case_id") != case_id]
    summary_rows.append(summary_row)
    summary_rows.sort(key=lambda row: row.get("case_id", ""))
    write_rows(summary_path, SUMMARY_FIELDS, summary_rows)
    write_rows(os.path.join(args.stage_dir, "STAGE14D_24H_MASTER_SUMMARY.csv"), SUMMARY_FIELDS, summary_rows)
    write_report(args.stage_dir, history_rows, summary_rows)
    print("Updated %s" % history_path)
    print("Updated %s" % summary_path)


if __name__ == "__main__":
    main()
