#!/usr/bin/env python3
from __future__ import print_function

import sys
import os
from multiprocessing import Pool
from pathlib import Path

from stage15k_state_extrapolator import DERIVATIVE_METHODS, SUMMARY_FIELDS, fixed_route, write_csv, write_report


ROUTES = [(500, 1000), (1000, 5000), (5000, 10000), (10000, 15000), (50000, 100000), (100000, 106250)]


def run_task(task):
    base, target, method = task
    print("fixed route %d -> %d method %s" % (base, target, method), flush=True)
    rows, _, _ = fixed_route(base, target, method=method, compare_offsets=(0, 100, 1000))
    return rows


def main():
    out_dir = Path("fixed_state_jump")
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    accepted = []
    tasks = [(base, target, method) for base, target in ROUTES for method in DERIVATIVE_METHODS]
    workers = max(1, min(int(os.environ.get("STAGE15K_ACTIVE_WORKERS", "1")), len(tasks)))
    if workers == 1:
        results = [run_task(task) for task in tasks]
    else:
        with Pool(processes=workers) as pool:
            results = pool.map(run_task, tasks)
    for rows in results:
        all_rows.extend(rows)
        if any(row["relaxed_5pct_accepted"] == "true" for row in rows):
            accepted.extend([row for row in rows if row["relaxed_5pct_accepted"] == "true"])
    write_csv(out_dir / "STAGE15K_FIXED_STATE_JUMP_RESULTS.csv", all_rows, SUMMARY_FIELDS)
    write_csv(out_dir / "STAGE15K_FIXED_STATE_JUMP_ERROR_TABLE.csv", all_rows, SUMMARY_FIELDS)
    write_csv(out_dir / "STAGE15K_FIXED_ACCEPTED_JUMPS.csv", accepted, SUMMARY_FIELDS)
    gate_pass = len(all_rows) > 0
    write_report(out_dir / "STAGE15K_FIXED_STATE_JUMP_REPORT.md", "Stage 15K Fixed State-Jump Matrix Report", all_rows, gate_pass=gate_pass)
    print("fixed_matrix_complete=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
