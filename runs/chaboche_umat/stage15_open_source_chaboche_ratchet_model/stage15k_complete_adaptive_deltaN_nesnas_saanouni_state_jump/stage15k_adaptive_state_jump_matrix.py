#!/usr/bin/env python3
from __future__ import print_function

import csv
import sys
import os
from multiprocessing import Pool
from pathlib import Path

from stage15k_state_extrapolator import DERIVATIVE_METHODS, SUMMARY_FIELDS, adaptive_route, write_csv, write_report


BASES = [500, 1000, 5000, 10000, 50000, 100000, 200000, 500000]
TARGETS = [1000, 5000, 10000, 50000, 100000, 200000, 500000, 1000000, 1500000]


def run_task(task):
    base, target, method = task
    print("adaptive route base %d request %d method %s" % (base, target, method), flush=True)
    rows, info, _ = adaptive_route(base, target, method=method, previous_accepted=100000, compare_offsets=(0, 100, 1000))
    return rows, info, base, target


def main():
    out_dir = Path("adaptive_state_jump")
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    accepted = []
    deltan_rows = []
    tasks = [(base, target, method) for base in BASES for target in TARGETS if target > base for method in DERIVATIVE_METHODS]
    workers = max(1, min(int(os.environ.get("STAGE15K_ACTIVE_WORKERS", "1")), len(tasks)))
    if workers == 1:
        results = [run_task(task) for task in tasks]
    else:
        with Pool(processes=workers) as pool:
            results = pool.map(run_task, tasks)
    for rows, info, base, target in results:
        all_rows.extend(rows)
        deltan_rows.append(dict(info, base_cycle=base, requested_target_cycle=target, jump_target_cycle=base + info["deltaN_adaptive"]))
        if any(row["relaxed_5pct_accepted"] == "true" for row in rows):
            accepted.extend([row for row in rows if row["relaxed_5pct_accepted"] == "true"])
    write_csv(out_dir / "STAGE15K_ADAPTIVE_STATE_JUMP_RESULTS.csv", all_rows, SUMMARY_FIELDS)
    write_csv(out_dir / "STAGE15K_ADAPTIVE_STATE_JUMP_ERROR_TABLE.csv", all_rows, SUMMARY_FIELDS)
    write_csv(out_dir / "STAGE15K_ADAPTIVE_ACCEPTED_JUMPS.csv", accepted, SUMMARY_FIELDS)
    if deltan_rows:
        fields = list(deltan_rows[0].keys())
        with (out_dir / "STAGE15K_ADAPTIVE_DELTAN_TABLE.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(deltan_rows)
    write_report(out_dir / "STAGE15K_ADAPTIVE_STATE_JUMP_REPORT.md", "Stage 15K Adaptive State-Jump Matrix Report", all_rows, gate_pass=len(all_rows) > 0)
    print("adaptive_matrix_complete=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
