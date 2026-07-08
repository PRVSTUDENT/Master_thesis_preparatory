#!/usr/bin/env python3
"""Compare Stage 16N-C fixed jumps against the 1000-cycle reference.

The comparison also reports the B0-1 state-initialized baseline where available
so the first fixed-jump error can be interpreted against the reinjection floor.

Run with Python 3. This script is pure CSV postprocessing and does not require
Abaqus Python.
"""

from __future__ import print_function

import argparse
import csv
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
REF_DIR = STAGE_DIR / "stage16n_parallel_max_reference"
REF_METRICS = REF_DIR / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
REF_LOCAL = REF_DIR / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"
OUT_DIR = STAGE_DIR / "stage16n_fixed_jump_validation"
B0_DIR = STAGE_DIR / "stage16n_exact_reinjection" / "cases" / "B0_100_to_250"

CASES = [
    ("B1_100_to_125_to_250", 100, 125, 250, "B0_100_to_250"),
    ("B2_250_to_300_to_500", 250, 300, 500, ""),
    ("B3_500_to_575_to_750", 500, 575, 750, ""),
]

QUANTITIES = [
    ("RF1_max", "global", "primary"),
    ("RF1_min", "global", "primary"),
    ("loop_area_abs", "global", "primary"),
    ("HOLE_RING_MISES_MAX", "local", "primary"),
    ("HOLE_RING_S11_MAX_ABS", "local", "primary"),
    ("HOLE_RING_SDV1_MAX", "local", "primary"),
    ("HOLE_RING_SDV8_MAX", "local", "diagnostic"),
    ("HOLE_RING_SDV11_MAX", "local", "primary"),
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
    if value == "":
        return ""
    return "%.6g" % float(value)


def load_case_outputs(case_dir, job):
    metrics = case_dir / ("%s_cycle_metrics.csv" % job)
    local = case_dir / ("%s_selected_cycle_local_states.csv" % job)
    if not metrics.exists() or not local.exists():
        return None, None
    return read_by_cycle(metrics), read_by_cycle(local)


def compare_case(name, base_cycle, jump_target_cycle, compare_cycle, baseline_case):
    case_dir = OUT_DIR / "cases" / name
    job = "stage16n_fixed_%s" % name.lower()
    case_metrics, case_local = load_case_outputs(case_dir, job)
    if case_metrics is None:
        return {
            "case": name,
            "base_cycle": base_cycle,
            "jump_target_cycle": jump_target_cycle,
            "compare_cycle": compare_cycle,
            "status": "missing_outputs",
            "max_primary_total_error_pct": "",
            "controlling_primary_quantity": "",
        }, []

    ref_metrics = read_by_cycle(REF_METRICS)
    ref_local = read_by_cycle(REF_LOCAL)
    b0_metrics, b0_local = load_case_outputs(B0_DIR, "stage16n_exact_b0_100_to_250")

    detail_rows = []
    max_primary = -1.0
    controlling = ""
    for quantity, group, role in QUANTITIES:
        source = case_metrics if group == "global" else case_local
        ref_source = ref_metrics if group == "global" else ref_local
        if compare_cycle not in source or compare_cycle not in ref_source:
            continue
        total_error = rel_pct(source[compare_cycle][quantity], ref_source[compare_cycle][quantity])

        baseline_error = ""
        additional_error = ""
        if baseline_case == "B0_100_to_250" and b0_metrics is not None:
            b0_source = b0_metrics if group == "global" else b0_local
            if compare_cycle in b0_source:
                baseline_error = rel_pct(b0_source[compare_cycle][quantity], ref_source[compare_cycle][quantity])
                additional_error = total_error - baseline_error

        detail_rows.append({
            "case": name,
            "compare_cycle": compare_cycle,
            "quantity": quantity,
            "metric_role": role,
            "fixed_jump_value": source[compare_cycle][quantity],
            "reference_value": ref_source[compare_cycle][quantity],
            "total_error_pct": fmt(total_error),
            "b0_reinjection_baseline_error_pct": fmt(baseline_error),
            "additional_error_minus_b0_pct": fmt(additional_error),
        })
        if role == "primary" and total_error > max_primary:
            max_primary = total_error
            controlling = quantity

    status = "pass" if max_primary >= 0.0 and max_primary <= 5.0 else "review"
    return {
        "case": name,
        "base_cycle": base_cycle,
        "jump_target_cycle": jump_target_cycle,
        "compare_cycle": compare_cycle,
        "status": status,
        "max_primary_total_error_pct": "" if max_primary < 0.0 else fmt(max_primary),
        "controlling_primary_quantity": controlling,
    }, detail_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="all", help="all or comma-separated case names")
    args = parser.parse_args()
    selected = None
    if args.cases != "all":
        selected = set(part.strip() for part in args.cases.split(",") if part.strip())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    details = []
    for case in CASES:
        if selected is not None and case[0] not in selected:
            continue
        summary, detail = compare_case(*case)
        summary_rows.append(summary)
        details.extend(detail)

    summary_csv = OUT_DIR / "stage16n_fixed_jump_comparison_summary.csv"
    detail_csv = OUT_DIR / "stage16n_fixed_jump_comparison_details.csv"
    with summary_csv.open("w", newline="") as handle:
        fields = [
            "case",
            "base_cycle",
            "jump_target_cycle",
            "compare_cycle",
            "status",
            "max_primary_total_error_pct",
            "controlling_primary_quantity",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary_rows)
    with detail_csv.open("w", newline="") as handle:
        fields = [
            "case",
            "compare_cycle",
            "quantity",
            "metric_role",
            "fixed_jump_value",
            "reference_value",
            "total_error_pct",
            "b0_reinjection_baseline_error_pct",
            "additional_error_minus_b0_pct",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(details)

    print("Wrote %s" % summary_csv)
    print("Wrote %s" % detail_csv)


if __name__ == "__main__":
    main()
