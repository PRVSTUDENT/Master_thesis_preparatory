#!/usr/bin/env python3
"""Compare native restart-control outputs against the 1000-cycle reference.

The restart-control extraction outputs are not created yet. This script defines
the comparison contract and exits clearly until those CSVs exist.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
REF = STAGE_DIR / "stage16n_parallel_max_reference" / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
OUT = STAGE_DIR / "stage16n_restart_control" / "stage16n_native_restart_control_comparison.csv"


def read_by_cycle(path: Path) -> dict[int, dict[str, str]]:
    with path.open(newline="") as handle:
        return {int(float(row["cycle"])): row for row in csv.DictReader(handle)}


def rel_pct(value: float, ref: float) -> float:
    return 100.0 * abs(value - ref) / max(abs(ref), 1.0e-12)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restart-metrics", type=Path, required=True)
    parser.add_argument("--cycles", default="500,1000")
    args = parser.parse_args()

    if not args.restart_metrics.exists():
        raise FileNotFoundError(args.restart_metrics)
    ref = read_by_cycle(REF)
    restart = read_by_cycle(args.restart_metrics)
    cycles = [int(part.strip()) for part in args.cycles.split(",") if part.strip()]
    fields = ["cycle", "RF1_max_error_pct", "RF1_min_error_pct", "loop_area_abs_error_pct"]
    rows = []
    for cycle in cycles:
        r_ref = ref[cycle]
        r_restart = restart[cycle]
        rows.append(
            {
                "cycle": cycle,
                "RF1_max_error_pct": f"{rel_pct(float(r_restart['RF1_max']), float(r_ref['RF1_max'])):.6g}",
                "RF1_min_error_pct": f"{rel_pct(float(r_restart['RF1_min']), float(r_ref['RF1_min'])):.6g}",
                "loop_area_abs_error_pct": f"{rel_pct(float(r_restart['loop_area_abs']), float(r_ref['loop_area_abs'])):.6g}",
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
