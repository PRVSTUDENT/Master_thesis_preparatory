#!/usr/bin/env python3
"""
Adaptive cycle-jump selector for Stage 16N Abaqus restart-based fatigue runs.

This script is intentionally lightweight: it does not run Abaqus. It reads the
classified comparison table and makes the adaptive accept/reject decision that
controls whether the next jump target may be expanded, reduced, or blocked.

Default input:
    ../data/stage16n_boundary_summary.csv

Example:
    python adaptive_jump_selector.py
    python adaptive_jump_selector.py --csv ../data/stage16n_boundary_summary.csv
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


TRUE_JUMP_MODES = {
    "repeat_true_jump",
    "diagnostic_repeat",
    "8core_calibration",
}

CONTROL_MODES = {
    "exact_native_control",
}


@dataclass(frozen=True)
class JumpResult:
    case: str
    target: int
    mode: str
    status: str
    max_global_error: float
    max_primary_local_error: float
    s11_error: float
    meaning: str

    @property
    def is_pass(self) -> bool:
        return self.status.strip().lower() == "pass"

    @property
    def is_fail(self) -> bool:
        return self.status.strip().lower() == "fail"

    @property
    def is_true_jump_evidence(self) -> bool:
        return self.mode in TRUE_JUMP_MODES

    @property
    def is_control_evidence(self) -> bool:
        return self.mode in CONTROL_MODES


def read_results(csv_path: Path) -> List[JumpResult]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "case",
            "target",
            "mode",
            "status",
            "max_global_error",
            "max_primary_local_error",
            "s11_error",
            "meaning",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

        results: List[JumpResult] = []
        for row in reader:
            results.append(
                JumpResult(
                    case=row["case"].strip(),
                    target=int(row["target"]),
                    mode=row["mode"].strip(),
                    status=row["status"].strip().lower(),
                    max_global_error=float(row["max_global_error"]),
                    max_primary_local_error=float(row["max_primary_local_error"]),
                    s11_error=float(row["s11_error"]),
                    meaning=row["meaning"].strip(),
                )
            )
    return results


def group_by_target(results: Iterable[JumpResult], *, true_jump_only: bool) -> dict[int, List[JumpResult]]:
    grouped: dict[int, List[JumpResult]] = {}
    for result in results:
        if true_jump_only and not result.is_true_jump_evidence:
            continue
        grouped.setdefault(result.target, []).append(result)
    return grouped


def accepted_boundary(results: List[JumpResult]) -> Optional[int]:
    """Return the largest target whose true-jump evidence all passes."""
    grouped = group_by_target(results, true_jump_only=True)
    accepted: List[int] = []
    for target, target_results in grouped.items():
        if target_results and all(item.is_pass for item in target_results):
            accepted.append(target)
    return max(accepted) if accepted else None


def first_rejected_after_boundary(results: List[JumpResult], boundary: Optional[int]) -> Optional[int]:
    grouped = group_by_target(results, true_jump_only=True)
    rejected: List[int] = []
    for target, target_results in grouped.items():
        if boundary is not None and target <= boundary:
            continue
        if any(item.is_fail for item in target_results):
            rejected.append(target)
    return min(rejected) if rejected else None


def exact_native_control_status(results: List[JumpResult], target: Optional[int]) -> Optional[str]:
    if target is None:
        return None
    controls = [item for item in results if item.target == target and item.is_control_evidence]
    if not controls:
        return None
    if all(item.is_pass for item in controls):
        return "pass"
    if any(item.is_fail for item in controls):
        return "fail"
    return "review"


def recommendation(boundary: Optional[int], rejected: Optional[int], control_status: Optional[str]) -> str:
    if boundary is None:
        return "No accepted true-jump boundary found. Run or inspect lower jump targets."
    if rejected is None:
        return "No rejected target after the accepted boundary. A larger gated target may be tested."
    if control_status == "pass":
        return (
            "Stop widening jumps. The native restart control passes, so the rejected target is limited by "
            "extrapolated state prediction. Redesign or diagnose the predictor before any higher target."
        )
    if control_status == "fail":
        return (
            "Stop widening jumps. The exact/native control also fails, so restart mechanics or source "
            "construction must be repaired before predictor work."
        )
    return "Stop widening jumps. Add an exact/native control at the first rejected target."


def print_summary(results: List[JumpResult]) -> None:
    boundary = accepted_boundary(results)
    rejected = first_rejected_after_boundary(results, boundary)
    control_status = exact_native_control_status(results, rejected)

    print("Adaptive cycle-jump decision")
    print("=" * 34)
    print(f"Accepted boundary: target{boundary}" if boundary is not None else "Accepted boundary: none")
    print(
        f"First rejected extrapolated target: target{rejected}"
        if rejected is not None
        else "First rejected extrapolated target: none"
    )
    print(
        f"Exact/native restart at target{rejected}: {control_status}"
        if rejected is not None and control_status is not None
        else "Exact/native restart control: not available"
    )

    print("\nTarget evidence:")
    grouped = group_by_target(results, true_jump_only=False)
    for target in sorted(grouped):
        target_results = grouped[target]
        true_jump_results = [item for item in target_results if item.is_true_jump_evidence]
        control_results = [item for item in target_results if item.is_control_evidence]
        true_jump_statuses = ", ".join(f"{item.case}:{item.status}" for item in true_jump_results) or "none"
        control_statuses = ", ".join(f"{item.case}:{item.status}" for item in control_results) or "none"
        print(f"  target{target}: true-jump [{true_jump_statuses}], controls [{control_statuses}]")

    print("\nConclusion:")
    if boundary is not None and rejected is not None and control_status == "pass":
        print(
            f"  target{boundary} is the accepted true-jump boundary. "
            f"target{rejected} is rejected for extrapolated state prediction, "
            "not for Abaqus native restart continuity."
        )
    else:
        print("  Boundary classification is incomplete; inspect the evidence table.")

    print("\nRecommended next action:")
    print(f"  {recommendation(boundary, rejected, control_status)}")


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    default_csv = script_dir.parent / "data" / "stage16n_boundary_summary.csv"

    parser = argparse.ArgumentParser(description="Select accepted adaptive cycle-jump boundary from classified CSV evidence.")
    parser.add_argument("--csv", type=Path, default=default_csv, help="Path to boundary summary CSV.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = read_results(args.csv)
    print_summary(results)


if __name__ == "__main__":
    main()
