#!/usr/bin/env python3
"""No-solver diagnostics for the R4Q3 cycle1000 repaired comparison."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JUMP_LOCAL = ROOT / "stage16n_r4q3_block03_750_to_771_solve_772_to_1000_selected_cycle_local_states.csv"
REF_LOCAL = ROOT / "R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv"
DETAILS = ROOT / "R4Q3_REFERENCE_REPAIR_cycle1000_comparison_details.csv"
SUMMARY = ROOT / "R4Q3_REFERENCE_REPAIR_cycle1000_comparison_summary.csv"

OUT_D1 = ROOT / "R4Q3D1_local_error_decomposition.csv"
OUT_D1_MD = ROOT / "R4Q3D1_local_error_decomposition.md"
OUT_D2 = ROOT / "R4Q3D2_HOLE_RING_SDV1_trace_compare.csv"
OUT_D2_MD = ROOT / "R4Q3D2_HOLE_RING_SDV1_trace_compare.md"
OUT_D3 = ROOT / "R4Q3D3_tolerance_sensitivity.csv"
OUT_D3_MD = ROOT / "R4Q3D3_tolerance_sensitivity.md"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


def rel_error_pct(jump_value: float, reference_value: float) -> float:
    denom = max(abs(reference_value), 1.0e-12)
    return abs(jump_value - reference_value) / denom * 100.0


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def row_for_cycle(rows: list[dict[str, str]], cycle: int) -> dict[str, str]:
    for row in rows:
        if int(float(row["cycle"])) == cycle:
            return row
    raise KeyError(f"cycle {cycle} not found")


def diagnostic_d1() -> list[dict[str, object]]:
    jump = row_for_cycle(read_rows(JUMP_LOCAL), 1000)
    ref = row_for_cycle(read_rows(REF_LOCAL), 1000)
    rows: list[dict[str, object]] = []
    for metric in sorted(set(jump) & set(ref) - {"cycle"}):
        jump_value = as_float(jump[metric])
        ref_value = as_float(ref[metric])
        rows.append(
            {
                "cycle": 1000,
                "metric": metric,
                "jump_value": f"{jump_value:.12g}",
                "reference_value": f"{ref_value:.12g}",
                "absolute_error": f"{abs(jump_value - ref_value):.12g}",
                "error_pct": f"{rel_error_pct(jump_value, ref_value):.9g}",
                "location_available": "no",
                "location_detail": "aggregate selected-cycle scalar only; no element/IP in lightweight CSV",
            }
        )
    rows.sort(key=lambda item: float(item["error_pct"]), reverse=True)
    write_csv(
        OUT_D1,
        rows,
        [
            "cycle",
            "metric",
            "jump_value",
            "reference_value",
            "absolute_error",
            "error_pct",
            "location_available",
            "location_detail",
        ],
    )
    top = rows[0]
    OUT_D1_MD.write_text(
        "\n".join(
            [
                "# R4Q3D1 Local Error Decomposition",
                "",
                "status=completed_no_abaqus",
                "classification_scope=diagnostic_after_cycle1000_accuracy_fail",
                "",
                f"Top ranked metric: `{top['metric']}`.",
                f"Top ranked error: `{top['error_pct']}%`.",
                "",
                "The current lightweight evidence contains aggregate selected-cycle scalar metrics, not per-element/per-integration-point local records. Therefore the exact element/IP for `HOLE_RING_SDV1_MAX` cannot be identified from the retained files.",
                "",
                f"CSV: `{OUT_D1.name}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return rows


def diagnostic_d2() -> list[dict[str, object]]:
    jump_rows = read_rows(JUMP_LOCAL)
    ref_rows = read_rows(REF_LOCAL)
    ref_by_cycle = {int(float(row["cycle"])): row for row in ref_rows}
    jump_by_cycle = {int(float(row["cycle"])): row for row in jump_rows}
    rows: list[dict[str, object]] = []
    for cycle in sorted(set(ref_by_cycle) | set(jump_by_cycle)):
        ref_value = as_float(ref_by_cycle[cycle]["HOLE_RING_SDV1_MAX"]) if cycle in ref_by_cycle else None
        jump_value = as_float(jump_by_cycle[cycle]["HOLE_RING_SDV1_MAX"]) if cycle in jump_by_cycle else None
        if ref_value is not None and jump_value is not None:
            error = rel_error_pct(jump_value, ref_value)
            status = "compared"
        elif ref_value is not None:
            error = None
            status = "reference_only"
        else:
            error = None
            status = "jump_only"
        rows.append(
            {
                "cycle": cycle,
                "reference_HOLE_RING_SDV1_MAX": "" if ref_value is None else f"{ref_value:.12g}",
                "jump_HOLE_RING_SDV1_MAX": "" if jump_value is None else f"{jump_value:.12g}",
                "error_pct": "" if error is None else f"{error:.9g}",
                "status": status,
            }
        )
    write_csv(
        OUT_D2,
        rows,
        ["cycle", "reference_HOLE_RING_SDV1_MAX", "jump_HOLE_RING_SDV1_MAX", "error_pct", "status"],
    )
    OUT_D2_MD.write_text(
        "\n".join(
            [
                "# R4Q3D2 HOLE_RING_SDV1 Trace Compare",
                "",
                "status=completed_no_abaqus",
                "classification_scope=diagnostic_after_cycle1000_accuracy_fail",
                "",
                "The repaired reference has selected local-state anchors at cycles 1, 2, 10, 50, 100, 250, 500, 750, and 1000.",
                "The retained R4Q3 selected local-state file has only the cycle1000 endpoint, so the SDV1 deviation cannot be classified as sudden or gradual from lightweight R4Q3 history alone.",
                "At cycle1000, `HOLE_RING_SDV1_MAX` is 24.4159812927 for R4Q3 and 26.0519256592 for the repaired reference, giving 6.2795526% relative error.",
                "",
                f"CSV: `{OUT_D2.name}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return rows


def diagnostic_d3() -> list[dict[str, object]]:
    summary = read_rows(SUMMARY)[0]
    max_global = as_float(summary["max_global_error_pct"])
    max_primary = as_float(summary["max_primary_local_error_pct"])
    s11 = as_float(summary["diagnostic_s11_error_pct"])
    rows: list[dict[str, object]] = []
    for tolerance in (5.0, 7.5, 10.0):
        primary_pass = max_primary <= tolerance
        global_pass = max_global <= 1.0
        s11_pass = s11 <= 1.0
        rows.append(
            {
                "primary_local_tolerance_pct": f"{tolerance:g}",
                "official_strict_gate": "yes" if tolerance == 5.0 else "no",
                "max_global_error_pct": f"{max_global:.9g}",
                "global_pass_1pct": str(global_pass).lower(),
                "max_primary_local_error_pct": f"{max_primary:.9g}",
                "primary_local_pass": str(primary_pass).lower(),
                "diagnostic_s11_error_pct": f"{s11:.9g}",
                "s11_pass_1pct": str(s11_pass).lower(),
                "overall_status": "pass" if global_pass and primary_pass and s11_pass else "fail",
            }
        )
    write_csv(
        OUT_D3,
        rows,
        [
            "primary_local_tolerance_pct",
            "official_strict_gate",
            "max_global_error_pct",
            "global_pass_1pct",
            "max_primary_local_error_pct",
            "primary_local_pass",
            "diagnostic_s11_error_pct",
            "s11_pass_1pct",
            "overall_status",
        ],
    )
    OUT_D3_MD.write_text(
        "\n".join(
            [
                "# R4Q3D3 Tolerance Sensitivity",
                "",
                "status=completed_no_abaqus",
                "classification_scope=diagnostic_after_cycle1000_accuracy_fail",
                "",
                "The official strict gate remains 5% primary-local error.",
                "R4Q3 fails the 5% primary-local gate, but would pass 7.5% and 10% primary-local sensitivity gates while global and S11 stay comfortably below 1%.",
                "",
                f"CSV: `{OUT_D3.name}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return rows


def main() -> None:
    d1 = diagnostic_d1()
    diagnostic_d2()
    diagnostic_d3()
    print(f"Wrote {OUT_D1.name} with {len(d1)} ranked local metrics")
    print(f"Wrote {OUT_D2.name}")
    print(f"Wrote {OUT_D3.name}")


if __name__ == "__main__":
    main()
