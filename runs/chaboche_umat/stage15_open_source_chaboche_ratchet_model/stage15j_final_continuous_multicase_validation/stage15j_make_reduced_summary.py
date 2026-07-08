#!/usr/bin/env python3
"""Aggregate Stage 15J per-case target values into one compact table."""

import argparse
import csv
from pathlib import Path

FIELDS = [
    "case_name", "group", "cycle", "stress_min", "stress_max", "strain_min", "strain_max",
    "strain_mean", "strain_range", "ratcheting_strain", "hysteresis_area",
    "accumulated_inelastic_strain_end", "backstress_norm_end",
    "points_per_cycle", "walltime_seconds", "cycles_per_hour", "backend",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="case_outputs")
    parser.add_argument("--output", default="STAGE15J_TARGET_CYCLE_VALUES.csv")
    args = parser.parse_args()

    by_case_cycle = {}
    for path in sorted(Path(args.input_dir).glob("*_target_values.csv")):
        with path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                key = (row.get("case_name", ""), int(float(row.get("cycle", 0))))
                by_case_cycle[key] = row

    rows = list(by_case_cycle.values())
    rows.sort(key=lambda row: (row.get("case_name", ""), int(float(row.get("cycle", 0)))))
    with Path(args.output).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print("wrote %d rows to %s" % (len(rows), args.output))


if __name__ == "__main__":
    main()
