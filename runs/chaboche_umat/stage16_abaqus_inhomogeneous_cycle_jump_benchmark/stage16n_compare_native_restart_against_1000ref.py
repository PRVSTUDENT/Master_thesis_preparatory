#!/usr/bin/env python3
"""Compare Stage 16N native restart-control outputs against references."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
DEFAULT_REF_METRICS = STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv"
DEFAULT_REF_LOCAL = (
    STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv"
)
GLOBAL_FIELDS = ["U1_max", "U1_min", "RF1_max", "RF1_min", "loop_area_abs"]
PRIMARY_LOCAL_FIELDS = [
    "HOLE_RING_MISES_MAX",
    "HOLE_RING_S11_MAX_ABS",
    "HOLE_RING_SDV1_MAX",
    "HOLE_RING_SDV8_MAX",
    "HOLE_RING_SDV11_MAX",
]


def read_by_cycle(path: Path) -> tuple[list[str], dict[int, dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = {int(float(row["cycle"])): row for row in reader}
    return fields, rows


def rel_pct(value: float, ref: float) -> float:
    return 100.0 * abs(value - ref) / max(abs(ref), 1.0e-12)


def compare_table(
    *,
    kind: str,
    fields: list[str],
    cycles: list[int],
    ref_rows: dict[int, dict[str, str]],
    test_rows: dict[int, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for cycle in cycles:
        if cycle not in ref_rows:
            raise KeyError(f"Cycle {cycle} missing from reference {kind} table")
        if cycle not in test_rows:
            raise KeyError(f"Cycle {cycle} missing from restart {kind} table")
        for field in fields:
            ref_value = float(ref_rows[cycle][field])
            test_value = float(test_rows[cycle][field])
            rows.append(
                {
                    "kind": kind,
                    "cycle": str(cycle),
                    "metric": field,
                    "restart_value": f"{test_value:.12g}",
                    "reference_value": f"{ref_value:.12g}",
                    "error_pct": f"{rel_pct(test_value, ref_value):.8g}",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restart-metrics", type=Path, required=True)
    parser.add_argument("--restart-local-states", type=Path)
    parser.add_argument("--ref-metrics", type=Path, default=DEFAULT_REF_METRICS)
    parser.add_argument("--ref-local-states", type=Path, default=DEFAULT_REF_LOCAL)
    parser.add_argument("--cycles", required=True, help="Comma-separated cycles to compare.")
    parser.add_argument("--out-dir", type=Path, default=Path("."))
    parser.add_argument("--prefix", default="stage16n_native_restart")
    args = parser.parse_args()

    cycles = [int(part.strip()) for part in args.cycles.split(",") if part.strip()]
    ref_metric_fields, ref_metrics = read_by_cycle(args.ref_metrics)
    test_metric_fields, test_metrics = read_by_cycle(args.restart_metrics)
    global_fields = [f for f in GLOBAL_FIELDS if f in ref_metric_fields and f in test_metric_fields]

    details = compare_table(
        kind="global_cycle_metric",
        fields=global_fields,
        cycles=cycles,
        ref_rows=ref_metrics,
        test_rows=test_metrics,
    )

    if args.restart_local_states is not None and args.restart_local_states.exists():
        ref_local_fields, ref_local = read_by_cycle(args.ref_local_states)
        test_local_fields, test_local = read_by_cycle(args.restart_local_states)
        local_fields = [f for f in PRIMARY_LOCAL_FIELDS if f in ref_local_fields and f in test_local_fields]
        details.extend(
            compare_table(
                kind="primary_local_scalar",
                fields=local_fields,
                cycles=cycles,
                ref_rows=ref_local,
                test_rows=test_local,
            )
        )

    detail_path = args.out_dir / f"{args.prefix}_comparison_details.csv"
    write_csv(
        detail_path,
        details,
        ["kind", "cycle", "metric", "restart_value", "reference_value", "error_pct"],
    )

    max_global = max((float(r["error_pct"]) for r in details if r["kind"] == "global_cycle_metric"), default=0.0)
    max_local = max((float(r["error_pct"]) for r in details if r["kind"] == "primary_local_scalar"), default=0.0)
    status = "pass" if max_global <= 1.0e-6 and max_local <= 1.0e-6 else "review"
    summary_rows = [
        {
            "cycles": ",".join(str(c) for c in cycles),
            "status": status,
            "max_global_error_pct": f"{max_global:.8g}",
            "max_primary_local_error_pct": f"{max_local:.8g}",
            "details_file": detail_path.name,
        }
    ]
    summary_path = args.out_dir / f"{args.prefix}_comparison_summary.csv"
    write_csv(
        summary_path,
        summary_rows,
        ["cycles", "status", "max_global_error_pct", "max_primary_local_error_pct", "details_file"],
    )
    print(f"Wrote {summary_path}")
    print(f"Wrote {detail_path}")


if __name__ == "__main__":
    main()
