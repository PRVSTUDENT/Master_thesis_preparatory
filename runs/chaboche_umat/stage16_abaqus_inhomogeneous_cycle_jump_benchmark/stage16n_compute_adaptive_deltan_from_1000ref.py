#!/usr/bin/env python3
"""Compute a conservative Stage 16N adaptive DeltaN table.

The table is derived from the completed 1000-cycle non-jump reference. Global
quantities are available at every cycle, while local hole-ring state variables
are available at selected reference cycles. For the first validation stage we
therefore choose jump anchors only from the selected local-state cycles.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REF = ROOT / "stage16n_parallel_max_reference"
METRICS_CSV = REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
LOCAL_CSV = REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"
OUT_CSV = ROOT / "stage16n_adaptive_deltan_table_1000ref.csv"
OUT_MD = ROOT / "STAGE16N_ADAPTIVE_DELTAN_FROM_1000_REFERENCE.md"

GLOBAL_TOL = 0.05
LOCAL_STRESS_TOL = 0.05
LOCAL_STATE_TOL = 0.10

VARIABLES = [
    ("RF1_max", "global", GLOBAL_TOL),
    ("RF1_min_abs", "global", GLOBAL_TOL),
    ("loop_area_abs", "global", GLOBAL_TOL),
    ("HOLE_RING_MISES_MAX", "local_stress", LOCAL_STRESS_TOL),
    ("HOLE_RING_S11_MAX_ABS", "local_stress", LOCAL_STRESS_TOL),
    ("HOLE_RING_SDV1_MAX", "local_state", LOCAL_STATE_TOL),
    ("HOLE_RING_SDV8_MAX", "local_state", LOCAL_STATE_TOL),
    ("HOLE_RING_SDV11_MAX", "local_state", LOCAL_STATE_TOL),
]


def read_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def rel_change(a, b):
    scale = max(abs(a), abs(b), 1.0e-12)
    return abs(b - a) / scale


def fmt_pct(value):
    return f"{100.0 * value:.2f}"


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
        next_anchor_delta = next_anchor - base

        controlling_name = ""
        controlling_group = ""
        controlling_change = 0.0
        controlling_allowed = float("inf")
        variable_changes = []

        for name, group, tol in VARIABLES:
            if name in metrics[base]:
                before = metrics[base][name]
                after = metrics[next_anchor][name]
            else:
                before = local[base][name]
                after = local[next_anchor][name]

            change = rel_change(before, after)
            per_cycle_change = change / max(next_anchor_delta, 1)
            allowed = float("inf") if per_cycle_change <= 0.0 else tol / per_cycle_change
            variable_changes.append(
                f"{name}={fmt_pct(change)}% over {next_anchor_delta} cycles"
            )

            if allowed < controlling_allowed:
                controlling_allowed = allowed
                controlling_name = name
                controlling_group = group
                controlling_change = change

        recommended_delta = max(1, int(controlling_allowed))
        recommended_target = min(1000, base + recommended_delta)
        next_anchor_acceptable = controlling_allowed >= next_anchor_delta

        if next_anchor_acceptable:
            decision = "next_selected_anchor_within_tolerance"
        elif recommended_delta <= 1:
            decision = "simulate_next_cycle_without_jump"
        else:
            decision = "adaptive_deltaN_limited_before_next_selected_anchor"

        table.append(
            {
                "base_cycle": base,
                "next_selected_anchor": next_anchor,
                "next_selected_anchor_deltaN": next_anchor_delta,
                "recommended_target_cycle": recommended_target,
                "recommended_deltaN": recommended_delta,
                "next_selected_anchor_acceptable": next_anchor_acceptable,
                "decision": decision,
                "controlling_variable": controlling_name,
                "controlling_group": controlling_group,
                "controlling_change_to_next_anchor_pct": fmt_pct(controlling_change),
                "estimated_allowed_deltaN": f"{controlling_allowed:.2f}",
                "variable_changes_to_next_anchor": "; ".join(variable_changes),
            }
        )

    with OUT_CSV.open("w", newline="") as handle:
        fieldnames = [
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
            "variable_changes_to_next_anchor",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)

    md_lines = [
        "# Stage 16N-A Adaptive DeltaN Table from 1000-Cycle Reference",
        "",
        "## Source Data",
        "",
        "- Reference metrics: `stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv`",
        "- Local states: `stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv`",
        "- Output table: `stage16n_adaptive_deltan_table_1000ref.csv`",
        "",
        "## Production Policy",
        "",
        "Stage 16N production jobs are locked to `1 MPI rank x 16 OpenMP threads`.",
        "",
        "```text",
        "PBS request   : select=1:ncpus=16:mpiprocs=1:ompthreads=16",
        "Abaqus launch : cpus=16 mp_mode=threads",
        "```",
        "",
        "This setting is a resource-efficient production compromise. It is not claimed to perfectly saturate all 16 CPUs.",
        "",
        "## Controller Rule",
        "",
        "The local-state file contains selected reference anchors, so the first adaptive estimate uses the measured change from each base cycle to the next selected local-state anchor. The controlling variable is the one that permits the smallest `DeltaN` before its tolerance is reached.",
        "",
        "| Variable group | Tolerance |",
        "| --- | ---: |",
        "| Global RF and loop-area quantities | 5% |",
        "| Local hole-ring stress quantities | 5% |",
        "| Local hole-ring STATEV quantities | 10% |",
        "",
        "The selected `DeltaN` is controlled by the most sensitive monitored variable, not only by global RF.",
        "",
        "## Adaptive DeltaN Estimate",
        "",
        "| Base cycle | Recommended target | DeltaN | Controlling variable | Change to next anchor | Decision |",
        "| ---: | ---: | ---: | --- | ---: | --- |",
    ]

    for row in table:
        md_lines.append(
            f"| {row['base_cycle']} | {row['recommended_target_cycle']} | "
            f"{row['recommended_deltaN']} | {row['controlling_variable']} | "
            f"{row['controlling_change_to_next_anchor_pct']}% | {row['decision']} |"
        )

    md_lines.extend([
        "",
        "## Fixed Validation Cases",
        "",
        "Before the fully adaptive workflow, run deliberate fixed jumps inside the 1000-cycle reference window:",
        "",
        "```text",
        "cycle 100 -> cycle 250",
        "cycle 100 -> cycle 500",
        "cycle 250 -> cycle 500",
        "cycle 500 -> cycle 1000",
        "```",
        "",
        "These fixed cases are intentionally more aggressive than the conservative adaptive table. Their purpose is to measure error and speed-up against the completed full reference.",
    ])

    md_lines.extend([
        "",
        "## Notes",
        "",
        "- Global variables are dense over cycles 1-1000.",
        "- Local hole-ring variables are available at selected cycles `1, 2, 10, 50, 100, 250, 500, 750, 1000`.",
        "- The first table is conservative because local STATEV values remain sensitive even after global RF and loop-area quantities become comparatively stable.",
        "- The next implementation step is to use this table to prepare fixed cycle-jump validation decks with the locked 16-CPU production launcher.",
        "",
    ])

    OUT_MD.write_text("\n".join(md_lines))

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
