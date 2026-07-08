#!/usr/bin/env python3
from __future__ import print_function

import sys
from pathlib import Path

from stage15k_state_extrapolator import SUMMARY_FIELDS, fixed_route, write_csv, write_report


def main():
    out_dir = Path("fixed_state_jump")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, base, pred = fixed_route(500, 1000, method="least_squares_last_20", compare_offsets=(0, 50, 100))
    csv_path = out_dir / "STAGE15K_FIXED_SMOKE_500_TO_1000.csv"
    write_csv(csv_path, rows, SUMMARY_FIELDS)
    smoke_pass = all(row["relaxed_5pct_accepted"] == "true" for row in rows)
    extra = [
        "## Route",
        "- Route: `500 -> 1000`",
        "- Method: `least_squares_last_20`",
        "- Full state extrapolated and reinjected: `true`",
        "- Post-jump continuation cycles checked: `0, 50, 100`",
        "- `fixed_smoke_pass`: `%s`" % str(bool(smoke_pass)).lower(),
    ]
    write_report(out_dir / "STAGE15K_FIXED_SMOKE_REPORT.md", "Stage 15K Fixed State-Jump Smoke Report", rows, extra, gate_pass=smoke_pass)
    print("Wrote %s" % csv_path)
    print("fixed_smoke_pass=%s" % str(bool(smoke_pass)).lower())
    return 0 if smoke_pass else 1


if __name__ == "__main__":
    sys.exit(main())
