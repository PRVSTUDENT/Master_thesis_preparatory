#!/usr/bin/env python3
"""Build robust scalar-metric re-score tables for Stage 16N B1 cases.

This is not a full pointwise field percentile study. It uses the lightweight
metrics already copied back to the repository: global cycle metrics, selected
hole-ring extrema, and selected cycle loop samples.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
FIXED = STAGE_DIR / "stage16n_fixed_jump_validation"
CASES_DIR = FIXED / "cases"
REF_DIR = STAGE_DIR / "stage16n_parallel_max_reference"
REF_METRICS = REF_DIR / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
REF_LOCAL = REF_DIR / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"
REF_LOOPS = REF_DIR / "stage16n_parallel_max_reference_1000cycles_selected_cycle_loops.csv"
OUT_CSV = FIXED / "stage16n_b1_robust_scalar_metric_rescore.csv"
OUT_MD = FIXED / "STAGE16N_B1_ROBUST_SCALAR_METRIC_RESCORE.md"

CASES = [
    "B1D1_100_to_101_to_250",
    "B1D1_EQ_100_to_101_to_250",
    "B1D2_100_to_102_to_250",
    "B1D2_EQ_100_to_102_to_250",
    "B1D3_100_to_103_to_250",
    "B1D3_EQ_100_to_103_to_250",
    "B1D4_100_to_104_to_250",
    "B1D4_EQ_100_to_104_to_250",
    "B1D5_100_to_105_to_250",
    "B1D5_EQ_100_to_105_to_250",
    "B1Q_100_to_106_to_250",
    "B1Q_EQ_100_to_106_to_250",
    "B1S_100_to_112_to_250",
    "B1S_EQ_100_to_112_to_250",
    "B1_100_to_125_to_250",
    "B1_EQ_100_to_125_to_250",
]

PRIMARY_METRICS = [
    "RF1_max",
    "RF1_min",
    "loop_area_abs",
    "HOLE_RING_MISES_MAX",
    "HOLE_RING_SDV1_MAX",
    "HOLE_RING_SDV11_MAX",
]

DIAGNOSTIC_METRICS = [
    "HOLE_RING_S11_MAX_ABS",
    "HOLE_RING_SDV8_MAX",
]


def read_cycle_row(path: Path, cycle: int) -> dict[str, str]:
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(float(row["cycle"])) == cycle:
                return row
    raise KeyError(f"cycle {cycle} not found in {path}")


def read_loop_rows(path: Path, cycle: int) -> list[dict[str, str]]:
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(float(row["cycle"])) == cycle:
                rows.append(row)
    return rows


def pct_error(value: float, ref: float) -> float:
    return 100.0 * abs(value - ref) / max(abs(ref), 1.0e-12)


def amplitude_error(value: float, ref: float, amplitude: float) -> float:
    return 100.0 * abs(value - ref) / max(abs(amplitude), 1.0e-12)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * pct / 100.0
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def summarize(errors: list[float]) -> dict[str, float]:
    return {
        "mean_error_pct": sum(errors) / len(errors) if errors else math.nan,
        "median_error_pct": percentile(errors, 50.0),
        "p95_error_pct": percentile(errors, 95.0),
        "p99_error_pct": percentile(errors, 99.0),
        "max_error_pct": max(errors) if errors else math.nan,
    }


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.6g}"


def classify(max_primary: float, p95_primary: float) -> str:
    if max_primary <= 5.0:
        return "pass_by_max"
    if p95_primary <= 5.0:
        return "robust_pass_but_max_review"
    return "review"


def main() -> None:
    ref_metrics = read_cycle_row(REF_METRICS, 250)
    ref_local = read_cycle_row(REF_LOCAL, 250)
    ref_loops = read_loop_rows(REF_LOOPS, 250)
    loop_amplitudes = {}
    for name in ("U1_avg", "RF1_sum"):
        vals = [float(row[name]) for row in ref_loops]
        loop_amplitudes[name] = max(vals) - min(vals)

    rows = []
    for case in CASES:
        job = f"stage16n_fixed_{case.lower()}"
        case_dir = CASES_DIR / case
        metrics_path = case_dir / f"{job}_cycle_metrics.csv"
        local_path = case_dir / f"{job}_selected_cycle_local_states.csv"
        loops_path = case_dir / f"{job}_selected_cycle_loops.csv"
        if not metrics_path.exists() or not local_path.exists() or not loops_path.exists():
            continue

        case_metrics = read_cycle_row(metrics_path, 250)
        case_local = read_cycle_row(local_path, 250)
        case_loops = read_loop_rows(loops_path, 250)

        primary_errors = []
        diagnostic_errors = []
        for name in PRIMARY_METRICS:
            source = case_metrics if name in case_metrics else case_local
            ref = ref_metrics if name in ref_metrics else ref_local
            primary_errors.append(pct_error(float(source[name]), float(ref[name])))
        for name in DIAGNOSTIC_METRICS:
            source = case_metrics if name in case_metrics else case_local
            ref = ref_metrics if name in ref_metrics else ref_local
            diagnostic_errors.append(pct_error(float(source[name]), float(ref[name])))

        loop_errors = []
        for c_row, r_row in zip(case_loops, ref_loops):
            for name in ("U1_avg", "RF1_sum"):
                loop_errors.append(
                    amplitude_error(
                        float(c_row[name]),
                        float(r_row[name]),
                        loop_amplitudes[name],
                    )
                )

        primary = summarize(primary_errors)
        diagnostic = summarize(diagnostic_errors)
        loops = summarize(loop_errors)
        rows.append(
            {
                "case": case,
                "status": classify(primary["max_error_pct"], primary["p95_error_pct"]),
                "primary_metric_count": len(primary_errors),
                **{f"primary_{key}": fmt(value) for key, value in primary.items()},
                "diagnostic_metric_count": len(diagnostic_errors),
                **{f"diagnostic_{key}": fmt(value) for key, value in diagnostic.items()},
                "loop_sample_count": len(loop_errors),
                **{f"loop_{key}": fmt(value) for key, value in loops.items()},
            }
        )

    fields = [
        "case",
        "status",
        "primary_metric_count",
        "primary_mean_error_pct",
        "primary_median_error_pct",
        "primary_p95_error_pct",
        "primary_p99_error_pct",
        "primary_max_error_pct",
        "diagnostic_metric_count",
        "diagnostic_mean_error_pct",
        "diagnostic_median_error_pct",
        "diagnostic_p95_error_pct",
        "diagnostic_p99_error_pct",
        "diagnostic_max_error_pct",
        "loop_sample_count",
        "loop_mean_error_pct",
        "loop_median_error_pct",
        "loop_p95_error_pct",
        "loop_p99_error_pct",
        "loop_max_error_pct",
    ]
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    md = [
        "# Stage 16N B1 Robust Scalar-Metric Re-score",
        "",
        "This table re-scores the completed B1/B1_EQ family using robust statistics over the lightweight scalar metrics already stored in the repository. It is not a full pointwise field percentile study because full per-integration-point fields were not retained for every B1 case.",
        "",
        "Loop errors are normalized by the full reference loop amplitude for `U1_avg` and `RF1_sum`, not by each individual reference point. This avoids artificial blow-ups at zero crossings.",
        "",
        "## Interpretation Rule",
        "",
        "- `pass_by_max`: maximum primary scalar-metric error is at or below 5%.",
        "- `robust_pass_but_max_review`: p95 primary scalar-metric error is at or below 5%, but the maximum is above 5%.",
        "- `review`: p95 and maximum primary scalar-metric errors are above 5%.",
        "",
        "## Summary",
        "",
        "| Case | Status | Primary mean % | Primary median % | Primary p95 % | Primary p99 % | Primary max % | Loop p95 % |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md.append(
            "| {case} | {status} | {primary_mean_error_pct} | {primary_median_error_pct} | {primary_p95_error_pct} | {primary_p99_error_pct} | {primary_max_error_pct} | {loop_p95_error_pct} |".format(
                **row
            )
        )
    md.extend(
        [
            "",
            "## Conclusion",
            "",
            "The robust scalar re-score keeps the same conservative conclusion as the max-error gate. `B1D5` and `B1D5_EQ` are clean passes. Several neighboring cases have low global loop errors but remain review cases because their primary local scalar metrics exceed the 5% threshold. A future pointwise field-percentile study should use full ODB-extracted integration-point fields if a less brittle local acceptance rule is needed.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
