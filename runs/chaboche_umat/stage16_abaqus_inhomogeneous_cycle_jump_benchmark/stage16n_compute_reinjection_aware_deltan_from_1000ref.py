#!/usr/bin/env python3
"""Compute a reinjection-aware Stage 16N adaptive DeltaN table.

This variant keeps SDV8 in the diagnostic text but removes it from the hard
controller list because the B0 initialization audit showed that SDV8 has a
large manual SDVINI/SIGINI initialization error floor before any jump
extrapolation is applied.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REF = ROOT / "stage16n_parallel_max_reference"
METRICS_CSV = REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
LOCAL_CSV = REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"
OUT_CSV = ROOT / "stage16n_adaptive_deltan_table_1000ref_reinjection_aware.csv"
OUT_MD = ROOT / "STAGE16N_ADAPTIVE_DELTAN_FROM_1000_REFERENCE_REINJECTION_AWARE.md"

GLOBAL_TOL = 0.05
LOCAL_STRESS_TOL = 0.05
LOCAL_STATE_TOL = 0.10

HARD_CONTROLLER_VARIABLES = [
    ("RF1_max", "global", GLOBAL_TOL),
    ("RF1_min_abs", "global", GLOBAL_TOL),
    ("loop_area_abs", "global", GLOBAL_TOL),
    ("HOLE_RING_MISES_MAX", "local_stress", LOCAL_STRESS_TOL),
    ("HOLE_RING_S11_MAX_ABS", "local_stress", LOCAL_STRESS_TOL),
    ("HOLE_RING_SDV1_MAX", "local_state", LOCAL_STATE_TOL),
    ("HOLE_RING_SDV11_MAX", "local_state", LOCAL_STATE_TOL),
]

DIAGNOSTIC_VARIABLES = [
    ("HOLE_RING_SDV8_MAX", "diagnostic_state", LOCAL_STATE_TOL),
]


def read_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def rel_change(a, b):
    scale = max(abs(a), abs(b), 1.0e-12)
    return abs(b - a) / scale


def fmt_pct(value):
    return "%.2f" % (100.0 * value)


def value_at(name, cycle, metrics, local):
    if name in metrics[cycle]:
        return metrics[cycle][name]
    return local[cycle][name]


def main():
    metrics_rows = read_rows(METRICS_CSV)
    local_rows = read_rows(LOCAL_CSV)

    metrics = {}
    for row in metrics_rows:
        cycle = int(float(row["cycle"]))
        metrics[cycle] = {
            "RF1_max": float(row["RF1_max"]),
            "RF1_min_abs": abs(float(row["RF1_min"])),
            "loop_area_abs": float(row["loop_area_abs"]),
        }

    local = {}
    for row in local_rows:
        cycle = int(float(row["cycle"]))
        local[cycle] = {key: float(value) for key, value in row.items() if key != "cycle"}

    anchors = sorted(set(metrics).intersection(local))
    table = []

    for i, base in enumerate(anchors[:-1]):
        next_anchor = anchors[i + 1]
        span = next_anchor - base
        controlling_name = ""
        controlling_group = ""
        controlling_change = 0.0
        controlling_allowed = float("inf")
        hard_changes = []
        diagnostic_changes = []

        for name, group, tol in HARD_CONTROLLER_VARIABLES:
            before = value_at(name, base, metrics, local)
            after = value_at(name, next_anchor, metrics, local)
            change = rel_change(before, after)
            per_cycle_change = change / max(span, 1)
            allowed = float("inf") if per_cycle_change <= 0.0 else tol / per_cycle_change
            hard_changes.append("%s=%s%% over %d cycles" % (name, fmt_pct(change), span))
            if allowed < controlling_allowed:
                controlling_allowed = allowed
                controlling_name = name
                controlling_group = group
                controlling_change = change

        for name, _group, _tol in DIAGNOSTIC_VARIABLES:
            before = value_at(name, base, metrics, local)
            after = value_at(name, next_anchor, metrics, local)
            change = rel_change(before, after)
            diagnostic_changes.append("%s=%s%% over %d cycles" % (name, fmt_pct(change), span))

        recommended_delta = max(1, int(controlling_allowed))
        recommended_target = min(1000, base + recommended_delta)
        next_anchor_acceptable = controlling_allowed >= span
        if next_anchor_acceptable:
            decision = "next_selected_anchor_within_tolerance"
        elif recommended_delta <= 1:
            decision = "simulate_next_cycle_without_jump"
        else:
            decision = "adaptive_deltaN_limited_before_next_selected_anchor"

        table.append({
            "base_cycle": base,
            "next_selected_anchor": next_anchor,
            "next_selected_anchor_deltaN": span,
            "recommended_target_cycle": recommended_target,
            "recommended_deltaN": recommended_delta,
            "next_selected_anchor_acceptable": next_anchor_acceptable,
            "decision": decision,
            "controlling_variable": controlling_name,
            "controlling_group": controlling_group,
            "controlling_change_to_next_anchor_pct": fmt_pct(controlling_change),
            "estimated_allowed_deltaN": "%.2f" % controlling_allowed,
            "hard_controller_changes_to_next_anchor": "; ".join(hard_changes),
            "diagnostic_changes_to_next_anchor": "; ".join(diagnostic_changes),
        })

    fields = [
        "base_cycle",
        "next_selected_anchor",
        "next_selected_anchor_deltaN",
        "recommended_target_cycle",
        "recommended_deltaN",
        "next_selected_anchor_acceptable",
        "decision",
        "controlling_variable",
        "controlling_group",
        "controlling_change_to_next_anchor_pct",
        "estimated_allowed_deltaN",
        "hard_controller_changes_to_next_anchor",
        "diagnostic_changes_to_next_anchor",
    ]
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(table)

    lines = [
        "# Stage 16N-A Reinjection-Aware Adaptive DeltaN Table",
        "",
        "This table is derived from the completed 1000-cycle reference, but it applies the B0 initialization-audit conclusion.",
        "",
        "## Key change from the original table",
        "",
        "`HOLE_RING_SDV8_MAX` is reported as diagnostic-only and removed from the hard controller list because it already shows a large error immediately after manual `SDVINI/SIGINI` initialization.",
        "",
        "Hard controller variables:",
        "",
        "```text",
        "RF1_max",
        "RF1_min_abs",
        "loop_area_abs",
        "HOLE_RING_MISES_MAX",
        "HOLE_RING_S11_MAX_ABS",
        "HOLE_RING_SDV1_MAX",
        "HOLE_RING_SDV11_MAX",
        "```",
        "",
        "Diagnostic-only variables:",
        "",
        "```text",
        "HOLE_RING_SDV8_MAX",
        "```",
        "",
        "## Reinjection-aware DeltaN estimate",
        "",
        "| Base cycle | Recommended target | DeltaN | Controlling variable | Change to next anchor | Decision |",
        "| ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in table:
        lines.append(
            "| {base_cycle} | {recommended_target_cycle} | {recommended_deltaN} | "
            "{controlling_variable} | {controlling_change_to_next_anchor_pct}% | {decision} |".format(**row)
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The recommended fixed first case remains `100 -> 125, continue to 250`. This row is controlled by `HOLE_RING_SDV1_MAX`, so the B0 SDV8 limitation does not invalidate the first conservative fixed-jump gate.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines))
    print("Wrote %s" % OUT_CSV)
    print("Wrote %s" % OUT_MD)


if __name__ == "__main__":
    main()
