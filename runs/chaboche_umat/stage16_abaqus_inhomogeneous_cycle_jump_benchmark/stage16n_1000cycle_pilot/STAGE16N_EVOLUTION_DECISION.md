# Stage 16N Gate 1 Evolution Decision

## Status

Stage 16N Gate 1 did not complete the planned 1000-cycle pilot. The production-size run was killed by the PBS walltime limit after 22 hours:

- Job name: `stage16n_1000pilot`
- Completed solver evidence: cycles 1-592
- Partial/incomplete evidence: cycle 593
- Planned target: 1000 cycles
- Stop reason: `PBS: job killed: walltime 79301 exceeded limit 79200`

The CSV files in this folder are therefore valid as partial 592-cycle evidence, not as a completed 1000-cycle gate.

## Extracted Files

- `stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv`
- `stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_loops.csv`
- `stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv`

## Partial Evolution Evidence

Using cycle 1 as the baseline and cycle 592 as the last completed cycle:

- `RF1_max` changed from `2356.83407974` to `2913.7008667`, a `+23.63%` change.
- `RF1_min` magnitude changed from `-2509.71160126` to `-3071.62664795`, a `+22.39%` change.
- `loop_area_abs` changed from `433.821593417` to `550.369677898`, a `+26.87%` change.

The selected local-state output currently reaches cycle 500. Using cycle 1 to cycle 500:

- `HOLE_RING_SDV1_MAX` changed from `0.0560648106039` to `13.0502681732`.
- `HOLE_RING_SDV11_MAX` changed from `7.90187931061` to `60.1659240723`.
- `HOLE_RING_MISES_MAX` changed from `398.503352332` to `493.082414121`, a `+23.73%` change.

These partial results show strong global and local cyclic evolution before the run stopped.

## Gate Decision

The strict 1000-cycle Gate 1 remains incomplete because the run stopped before cycle 1000.

However, the partial 592-cycle evidence already exceeds the planned evolution thresholds:

- RF peak change threshold: `> 5%`
- Loop-area change threshold: `> 5%`
- Local plastic/STATEV evolution threshold: `> 10%`

Recommendation: proceed with Stage 16N follow-up planning, but document that this decision is based on partial 592-cycle evidence. If a formal 1000-cycle gate is required, rerun from restart or reduce output cost so the pilot can finish within the available walltime.
