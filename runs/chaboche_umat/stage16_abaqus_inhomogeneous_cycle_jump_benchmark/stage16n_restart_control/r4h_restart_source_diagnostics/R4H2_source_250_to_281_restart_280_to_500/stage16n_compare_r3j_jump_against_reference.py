#!/usr/bin/env python3
"""Compare Stage 16N-R3J restart-preserved jumps against references."""

import argparse
import csv
from pathlib import Path


GLOBAL_FIELDS = ["U1_max", "U1_min", "RF1_max", "RF1_min", "loop_area_abs"]
PRIMARY_LOCAL_FIELDS = [
    "HOLE_RING_MISES_MAX",
    "HOLE_RING_SDV1_MAX",
    "HOLE_RING_SDV8_MAX",
    "HOLE_RING_SDV11_MAX",
]
DIAGNOSTIC_LOCAL_FIELDS = ["HOLE_RING_S11_MAX_ABS"]


def read_by_cycle(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = {int(float(row["cycle"])): row for row in reader}
    return fields, rows


def rel_pct(value, ref):
    return 100.0 * abs(value - ref) / max(abs(ref), 1.0e-12)


def compare_table(kind, fields, cycles, ref_rows, test_rows):
    rows = []
    for cycle in cycles:
        if cycle not in ref_rows:
            raise KeyError(f"Cycle {cycle} missing from reference {kind} table")
        if cycle not in test_rows:
            raise KeyError(f"Cycle {cycle} missing from jump {kind} table")
        for field in fields:
            ref_value = float(ref_rows[cycle][field])
            test_value = float(test_rows[cycle][field])
            rows.append(
                {
                    "kind": kind,
                    "cycle": str(cycle),
                    "metric": field,
                    "jump_value": "%.12g" % test_value,
                    "reference_value": "%.12g" % ref_value,
                    "error_pct": "%.8g" % rel_pct(test_value, ref_value),
                }
            )
    return rows


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def classify(max_primary_local):
    if max_primary_local <= 5.0:
        return "pass"
    if max_primary_local <= 10.0:
        return "review"
    return "fail"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jump-metrics", type=Path, required=True)
    parser.add_argument("--jump-local-states", type=Path, required=True)
    parser.add_argument("--ref-metrics", type=Path, required=True)
    parser.add_argument("--ref-local-states", type=Path, required=True)
    parser.add_argument("--cycles", required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("."))
    parser.add_argument("--prefix", default="stage16n_r3j_jump")
    args = parser.parse_args()

    cycles = [int(part.strip()) for part in args.cycles.split(",") if part.strip()]
    ref_metric_fields, ref_metrics = read_by_cycle(args.ref_metrics)
    jump_metric_fields, jump_metrics = read_by_cycle(args.jump_metrics)
    ref_local_fields, ref_local = read_by_cycle(args.ref_local_states)
    jump_local_fields, jump_local = read_by_cycle(args.jump_local_states)

    details = []
    details.extend(
        compare_table(
            kind="global_cycle_metric",
            fields=[f for f in GLOBAL_FIELDS if f in ref_metric_fields and f in jump_metric_fields],
            cycles=cycles,
            ref_rows=ref_metrics,
            test_rows=jump_metrics,
        )
    )
    details.extend(
        compare_table(
            kind="primary_local_scalar",
            fields=[f for f in PRIMARY_LOCAL_FIELDS if f in ref_local_fields and f in jump_local_fields],
            cycles=cycles,
            ref_rows=ref_local,
            test_rows=jump_local,
        )
    )
    details.extend(
        compare_table(
            kind="diagnostic_local_scalar",
            fields=[f for f in DIAGNOSTIC_LOCAL_FIELDS if f in ref_local_fields and f in jump_local_fields],
            cycles=cycles,
            ref_rows=ref_local,
            test_rows=jump_local,
        )
    )

    detail_path = args.out_dir / f"{args.prefix}_comparison_details.csv"
    write_csv(
        detail_path,
        details,
        ["kind", "cycle", "metric", "jump_value", "reference_value", "error_pct"],
    )

    max_global = max((float(r["error_pct"]) for r in details if r["kind"] == "global_cycle_metric"), default=0.0)
    max_primary_local = max(
        (float(r["error_pct"]) for r in details if r["kind"] == "primary_local_scalar"),
        default=0.0,
    )
    max_diagnostic_s11 = max(
        (
            float(r["error_pct"])
            for r in details
            if r["kind"] == "diagnostic_local_scalar" and r["metric"] == "HOLE_RING_S11_MAX_ABS"
        ),
        default=0.0,
    )
    summary_rows = [
        {
            "cycles": ",".join(str(c) for c in cycles),
            "status": classify(max_primary_local),
            "max_global_error_pct": "%.8g" % max_global,
            "max_primary_local_error_pct": "%.8g" % max_primary_local,
            "diagnostic_s11_error_pct": "%.8g" % max_diagnostic_s11,
            "details_file": detail_path.name,
        }
    ]
    summary_path = args.out_dir / f"{args.prefix}_comparison_summary.csv"
    write_csv(
        summary_path,
        summary_rows,
        [
            "cycles",
            "status",
            "max_global_error_pct",
            "max_primary_local_error_pct",
            "diagnostic_s11_error_pct",
            "details_file",
        ],
    )
    print("Wrote %s" % summary_path)
    print("Wrote %s" % detail_path)


if __name__ == "__main__":
    main()
