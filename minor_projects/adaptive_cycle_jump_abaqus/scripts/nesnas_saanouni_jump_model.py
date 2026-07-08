#!/usr/bin/env python3
"""
Nesnas-Saanouni-style adaptive cycle-jump model for Stage 16N.

Reference basis:
    Nesnas & Saanouni (2000), "A cycle jumping scheme for numerical
    integration of coupled damage and viscoplastic models for cyclic loading
    paths", DOI: 10.1080/12506559.2000.10511493.

Important scope note:
    This is a lightweight, engineering implementation inspired by the
    Nesnas-Saanouni idea of choosing the cycle jump from bounded evolution of
    monitored internal/state quantities. It is not a full reproduction of every
    constitutive integration equation from the paper because this repository's
    current lightweight evidence contains comparison metrics, not complete
    per-integration-point internal variable histories.

What this script does:
    1. Reads classified candidate jump results.
    2. Converts each candidate into a normalized monitor ratio:

          R = max(global_error/global_tol,
                  primary_local_error/primary_local_tol,
                  s11_error/s11_tol)

       A candidate is admissible when R <= 1 and the classified status is pass.
    3. Uses a first-order cycle-evolution estimate between accepted candidates
       to estimate how far the next jump could be extended.
    4. Applies the available validation evidence as a hard safety cap: once a
       target is reproducibly rejected, the safe jump cannot cross that target.
    5. Reports the maximum safe number of skipped cycles.

Default input:
    ../data/stage16n_boundary_summary.csv

Example:
    python scripts/nesnas_saanouni_jump_model.py
    python scripts/nesnas_saanouni_jump_model.py --source-cycle 250 --global-tol 1 --primary-local-tol 5 --s11-tol 1
"""

import argparse
import csv
import math
from pathlib import Path


TRUE_JUMP_MODES = set([
    "repeat_true_jump",
    "diagnostic_repeat",
    "8core_calibration",
])

CONTROL_MODES = set([
    "exact_native_control",
])


class JumpRecord(object):
    def __init__(self, row):
        self.case = row["case"].strip()
        self.target = int(row["target"])
        self.mode = row["mode"].strip()
        self.status = row["status"].strip().lower()
        self.max_global_error = float(row["max_global_error"])
        self.max_primary_local_error = float(row["max_primary_local_error"])
        self.s11_error = float(row["s11_error"])
        self.meaning = row.get("meaning", "").strip()

    @property
    def is_true_jump(self):
        return self.mode in TRUE_JUMP_MODES

    @property
    def is_control(self):
        return self.mode in CONTROL_MODES

    @property
    def is_pass(self):
        return self.status == "pass"

    @property
    def is_fail(self):
        return self.status == "fail"


def read_records(csv_path):
    if not csv_path.exists():
        raise SystemExit("CSV file not found: {}".format(csv_path))
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [JumpRecord(row) for row in rows]


def group_true_jump_by_target(records):
    grouped = {}
    for record in records:
        if not record.is_true_jump:
            continue
        grouped.setdefault(record.target, []).append(record)
    return grouped


def worst_case_by_target(records):
    grouped = group_true_jump_by_target(records)
    worst = []
    for target in sorted(grouped):
        entries = grouped[target]
        selected = max(entries, key=lambda item: item.max_primary_local_error)
        worst.append(selected)
    return worst


def monitor_ratio(record, global_tol, primary_local_tol, s11_tol):
    ratios = []
    if global_tol > 0:
        ratios.append(record.max_global_error / global_tol)
    if primary_local_tol > 0:
        ratios.append(record.max_primary_local_error / primary_local_tol)
    if s11_tol > 0:
        ratios.append(record.s11_error / s11_tol)
    return max(ratios) if ratios else float("inf")


def is_admissible_target(records_at_target, global_tol, primary_local_tol, s11_tol):
    if not records_at_target:
        return False
    for record in records_at_target:
        ratio = monitor_ratio(record, global_tol, primary_local_tol, s11_tol)
        if (not record.is_pass) or ratio > 1.0:
            return False
    return True


def first_rejected_target_after(grouped, accepted_target, global_tol, primary_local_tol, s11_tol):
    rejected = []
    for target in sorted(grouped):
        if accepted_target is not None and target <= accepted_target:
            continue
        entries = grouped[target]
        has_failed_status = any(item.is_fail for item in entries)
        has_excess_ratio = any(monitor_ratio(item, global_tol, primary_local_tol, s11_tol) > 1.0 for item in entries)
        if has_failed_status or has_excess_ratio:
            rejected.append(target)
    return rejected[0] if rejected else None


def exact_native_status(records, target):
    controls = [item for item in records if item.target == target and item.is_control]
    if not controls:
        return "not_available"
    if all(item.is_pass for item in controls):
        return "pass"
    if any(item.is_fail for item in controls):
        return "fail"
    return "review"


def estimate_next_by_first_order(source_cycle, accepted_worst_records, global_tol, primary_local_tol, s11_tol, growth_safety):
    """Estimate a next target from the slope of the normalized monitor.

    This is the Nesnas-Saanouni-style part: the jump increment is controlled by
    the estimated evolution rate of a monitored quantity per cycle. The estimate
    is intentionally conservative and is later capped by existing rejected
    validation evidence.
    """
    if not accepted_worst_records:
        return None, "no accepted records"
    if len(accepted_worst_records) == 1:
        current = accepted_worst_records[-1]
        return current.target + 1, "only one accepted target; proposing one-cycle extension"

    prev = accepted_worst_records[-2]
    curr = accepted_worst_records[-1]
    prev_r = monitor_ratio(prev, global_tol, primary_local_tol, s11_tol)
    curr_r = monitor_ratio(curr, global_tol, primary_local_tol, s11_tol)
    dcycles = float(curr.target - prev.target)
    if dcycles <= 0:
        return curr.target + 1, "non-positive target spacing; proposing one-cycle extension"

    slope = (curr_r - prev_r) / dcycles
    if slope <= 0:
        return curr.target + 1, "non-increasing monitor; proposing one-cycle extension"

    remaining = max(0.0, 1.0 - curr_r)
    # growth_safety < 1 avoids using the full remaining tolerance budget.
    extra_cycles = int(math.floor(growth_safety * remaining / slope))
    extra_cycles = max(1, extra_cycles)
    proposed = curr.target + extra_cycles
    reason = "first-order monitor slope {:.6g}/cycle, current ratio {:.6g}".format(slope, curr_r)
    return proposed, reason


def build_decision(records, source_cycle, global_tol, primary_local_tol, s11_tol, growth_safety, use_validation_cap):
    grouped = group_true_jump_by_target(records)
    accepted_targets = []
    for target in sorted(grouped):
        if is_admissible_target(grouped[target], global_tol, primary_local_tol, s11_tol):
            accepted_targets.append(target)

    accepted_target = max(accepted_targets) if accepted_targets else None
    if accepted_target is None:
        return {
            "accepted_target": None,
            "accepted_skipped": None,
            "first_rejected_target": None,
            "first_rejected_skipped": None,
            "proposed_target_before_validation_cap": None,
            "final_recommended_target": None,
            "exact_native_status": "not_available",
            "reason": "no admissible candidate found",
        }

    first_rejected = first_rejected_target_after(grouped, accepted_target, global_tol, primary_local_tol, s11_tol)
    control_status = exact_native_status(records, first_rejected) if first_rejected is not None else "not_available"

    worst = worst_case_by_target(records)
    accepted_worst = [item for item in worst if item.target in accepted_targets]
    proposed, proposed_reason = estimate_next_by_first_order(
        source_cycle, accepted_worst, global_tol, primary_local_tol, s11_tol, growth_safety
    )

    final_target = proposed
    cap_reason = ""
    if use_validation_cap and first_rejected is not None and proposed is not None and proposed >= first_rejected:
        final_target = accepted_target
        cap_reason = " validation cap applied because target{} is already rejected".format(first_rejected)
    elif use_validation_cap and first_rejected is not None:
        final_target = min(proposed, accepted_target) if proposed is not None else accepted_target
        cap_reason = " validation cap keeps the final target at the known accepted boundary"

    return {
        "accepted_target": accepted_target,
        "accepted_skipped": accepted_target - source_cycle,
        "first_rejected_target": first_rejected,
        "first_rejected_skipped": (first_rejected - source_cycle) if first_rejected is not None else None,
        "proposed_target_before_validation_cap": proposed,
        "final_recommended_target": final_target,
        "final_recommended_skipped": (final_target - source_cycle) if final_target is not None else None,
        "exact_native_status": control_status,
        "reason": proposed_reason + cap_reason,
    }


def print_table(records, source_cycle, global_tol, primary_local_tol, s11_tol):
    print("Candidate monitor table:")
    print("  target  skip  status  monitor_ratio  global%  local%  s11%")
    for record in worst_case_by_target(records):
        ratio = monitor_ratio(record, global_tol, primary_local_tol, s11_tol)
        print(
            "  {target:>6}  {skip:>4}  {status:<6}  {ratio:>13.6g}  {g:>7.6g}  {l:>7.6g}  {s:>7.6g}".format(
                target=record.target,
                skip=record.target - source_cycle,
                status=record.status,
                ratio=ratio,
                g=record.max_global_error,
                l=record.max_primary_local_error,
                s=record.s11_error,
            )
        )


def parse_args():
    script_dir = Path(__file__).resolve().parent
    default_csv = script_dir.parent / "data" / "stage16n_boundary_summary.csv"
    parser = argparse.ArgumentParser(
        description="Nesnas-Saanouni-style tolerance-based adaptive cycle-jump model."
    )
    parser.add_argument("--csv", type=Path, default=default_csv, help="Classified boundary CSV.")
    parser.add_argument("--source-cycle", type=int, default=250, help="Source cycle before the jump.")
    parser.add_argument("--global-tol", type=float, default=1.0, help="Global error tolerance in percent.")
    parser.add_argument("--primary-local-tol", type=float, default=5.0, help="Primary-local error tolerance in percent.")
    parser.add_argument("--s11-tol", type=float, default=1.0, help="Diagnostic S11 error tolerance in percent.")
    parser.add_argument(
        "--growth-safety",
        type=float,
        default=0.8,
        help="Fraction of remaining monitor margin used by first-order extrapolation.",
    )
    parser.add_argument(
        "--ignore-validation-cap",
        action="store_true",
        help="Show the first-order proposal without capping by already rejected evidence.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    records = read_records(args.csv)
    decision = build_decision(
        records=records,
        source_cycle=args.source_cycle,
        global_tol=args.global_tol,
        primary_local_tol=args.primary_local_tol,
        s11_tol=args.s11_tol,
        growth_safety=args.growth_safety,
        use_validation_cap=(not args.ignore_validation_cap),
    )

    print("Nesnas-Saanouni-style adaptive cycle-jump model")
    print("=" * 54)
    print("Source cycle: {}".format(args.source_cycle))
    print("Tolerances:")
    print("  max global error        <= {} %".format(args.global_tol))
    print("  max primary-local error <= {} %".format(args.primary_local_tol))
    print("  S11 error               <= {} %".format(args.s11_tol))
    print("")
    print_table(records, args.source_cycle, args.global_tol, args.primary_local_tol, args.s11_tol)
    print("")

    if decision["accepted_target"] is None:
        print("Final decision: no safe jump found.")
        return

    print("Accepted jump boundary from validation evidence:")
    print("  target cycle: {}".format(decision["accepted_target"]))
    print("  skipped cycles: {}".format(decision["accepted_skipped"]))
    print("")
    if decision["first_rejected_target"] is not None:
        print("First rejected jump:")
        print("  target cycle: {}".format(decision["first_rejected_target"]))
        print("  skipped cycles: {}".format(decision["first_rejected_skipped"]))
        print("  exact/native restart control: {}".format(decision["exact_native_status"]))
        print("")

    print("Nesnas-Saanouni-style first-order proposal:")
    print("  proposed target before validation cap: {}".format(decision["proposed_target_before_validation_cap"]))
    print("  reason: {}".format(decision["reason"]))
    print("")
    print("Final recommended jump:")
    print("  target cycle: {}".format(decision["final_recommended_target"]))
    print("  skipped cycles: {}".format(decision["final_recommended_skipped"]))
    print("")
    print("Interpretation:")
    print(
        "  Use source{} -> target{}. Do not widen beyond target{} until the extrapolated state predictor is redesigned.".format(
            args.source_cycle,
            decision["final_recommended_target"],
            decision["accepted_target"],
        )
    )


if __name__ == "__main__":
    main()
