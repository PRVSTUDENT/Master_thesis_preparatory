#!/usr/bin/env python3
"""Compare Stage 16N-B exact reinjection cases against the full reference CSVs."""

from __future__ import print_function

import argparse
import csv
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
REF_DIR = STAGE_DIR / "stage16n_parallel_max_reference"
REF_METRICS = REF_DIR / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
REF_LOCAL = REF_DIR / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"
OUT_DIR = STAGE_DIR / "stage16n_exact_reinjection"

CASES = [
    ("B0_100_to_250", 100, 250),
    ("B0_250_to_500", 250, 500),
    ("B0_500_to_1000", 500, 1000),
]

QUANTITIES = [
    ("RF1_max", "global"),
    ("RF1_min", "global"),
    ("loop_area_abs", "global"),
    ("HOLE_RING_MISES_MAX", "local"),
    ("HOLE_RING_S11_MAX_ABS", "local"),
    ("HOLE_RING_SDV1_MAX", "local"),
    ("HOLE_RING_SDV8_MAX", "local"),
    ("HOLE_RING_SDV11_MAX", "local"),
]


def read_by_cycle(path):
    out = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if not row.get("cycle"):
                continue
            out[int(float(row["cycle"]))] = row
    return out


def rel_pct(value, ref):
    value = float(value)
    ref = float(ref)
    scale = max(abs(ref), 1.0e-12)
    return 100.0 * abs(value - ref) / scale


def fmt(value):
    return "%.6g" % float(value)


def compare_case(name, base_cycle, compare_cycle):
    case_dir = OUT_DIR / "cases" / name
    job = "stage16n_exact_%s" % name.lower()
    metrics_path = case_dir / ("%s_cycle_metrics.csv" % job)
    local_path = case_dir / ("%s_selected_cycle_local_states.csv" % job)
    if not metrics_path.exists() or not local_path.exists():
        return {
            "case": name,
            "base_cycle": base_cycle,
            "compare_cycle": compare_cycle,
            "status": "missing_outputs",
            "max_error_pct": "",
            "controlling_quantity": "",
        }, []

    ref_metrics = read_by_cycle(REF_METRICS)
    ref_local = read_by_cycle(REF_LOCAL)
    case_metrics = read_by_cycle(metrics_path)
    case_local = read_by_cycle(local_path)

    detail_rows = []
    max_error = -1.0
    controlling = ""
    for quantity, group in QUANTITIES:
        source = case_metrics if group == "global" else case_local
        ref_source = ref_metrics if group == "global" else ref_local
        if compare_cycle not in source or compare_cycle not in ref_source:
            continue
        err = rel_pct(source[compare_cycle][quantity], ref_source[compare_cycle][quantity])
        detail_rows.append({
            "case": name,
            "compare_cycle": compare_cycle,
            "quantity": quantity,
            "reinjection_value": source[compare_cycle][quantity],
            "reference_value": ref_source[compare_cycle][quantity],
            "relative_error_pct": fmt(err),
        })
        if err > max_error:
            max_error = err
            controlling = quantity

    status = "pass" if max_error >= 0.0 and max_error <= 1.0 else "review"
    return {
        "case": name,
        "base_cycle": base_cycle,
        "compare_cycle": compare_cycle,
        "status": status,
        "max_error_pct": "" if max_error < 0.0 else fmt(max_error),
        "controlling_quantity": controlling,
    }, detail_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(OUT_DIR))
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    details = []
    for case in CASES:
        summary, detail = compare_case(*case)
        summary_rows.append(summary)
        details.extend(detail)

    summary_csv = outdir / "stage16n_exact_reinjection_comparison_summary.csv"
    detail_csv = outdir / "stage16n_exact_reinjection_comparison_details.csv"
    with summary_csv.open("w", newline="") as handle:
        fields = ["case", "base_cycle", "compare_cycle", "status", "max_error_pct", "controlling_quantity"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary_rows)
    with detail_csv.open("w", newline="") as handle:
        fields = ["case", "compare_cycle", "quantity", "reinjection_value", "reference_value", "relative_error_pct"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(details)

    print("Wrote %s" % summary_csv)
    print("Wrote %s" % detail_csv)


if __name__ == "__main__":
    main()
