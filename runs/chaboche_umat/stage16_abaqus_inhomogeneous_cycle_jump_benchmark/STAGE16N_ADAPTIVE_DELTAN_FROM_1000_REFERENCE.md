# Stage 16N-A Adaptive DeltaN Table from 1000-Cycle Reference

## Source Data

- Reference metrics: `stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv`
- Local states: `stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv`
- Output table: `stage16n_adaptive_deltan_table_1000ref.csv`

## Production Policy

Stage 16N production jobs are locked to `1 MPI rank x 16 OpenMP threads`.

```text
PBS request   : select=1:ncpus=16:mpiprocs=1:ompthreads=16
Abaqus launch : cpus=16 mp_mode=threads
```

This setting is a resource-efficient production compromise. It is not claimed to perfectly saturate all 16 CPUs.

## Controller Rule

The local-state file contains selected reference anchors, so the first adaptive estimate uses the measured change from each base cycle to the next selected local-state anchor. The controlling variable is the one that permits the smallest `DeltaN` before its tolerance is reached.

| Variable group | Tolerance |
| --- | ---: |
| Global RF and loop-area quantities | 5% |
| Local hole-ring stress quantities | 5% |
| Local hole-ring STATEV quantities | 10% |

The selected `DeltaN` is controlled by the most sensitive monitored variable, not only by global RF.

## Adaptive DeltaN Estimate

| Base cycle | Recommended target | DeltaN | Controlling variable | Change to next anchor | Decision |
| ---: | ---: | ---: | --- | ---: | --- |
| 1 | 2 | 1 | HOLE_RING_SDV8_MAX | 99.17% | simulate_next_cycle_without_jump |
| 2 | 3 | 1 | HOLE_RING_SDV8_MAX | 74.77% | simulate_next_cycle_without_jump |
| 10 | 14 | 4 | HOLE_RING_SDV8_MAX | 87.16% | adaptive_deltaN_limited_before_next_selected_anchor |
| 50 | 61 | 11 | HOLE_RING_SDV1_MAX | 44.89% | adaptive_deltaN_limited_before_next_selected_anchor |
| 100 | 124 | 24 | HOLE_RING_SDV1_MAX | 60.34% | adaptive_deltaN_limited_before_next_selected_anchor |
| 250 | 299 | 49 | HOLE_RING_SDV1_MAX | 50.83% | adaptive_deltaN_limited_before_next_selected_anchor |
| 500 | 575 | 75 | HOLE_RING_SDV1_MAX | 33.29% | adaptive_deltaN_limited_before_next_selected_anchor |
| 750 | 849 | 99 | HOLE_RING_MISES_MAX | 12.61% | adaptive_deltaN_limited_before_next_selected_anchor |

## Fixed Validation Cases

Before the fully adaptive workflow, run deliberate fixed jumps inside the 1000-cycle reference window:

```text
cycle 100 -> cycle 250
cycle 100 -> cycle 500
cycle 250 -> cycle 500
cycle 500 -> cycle 1000
```

These fixed cases are intentionally more aggressive than the conservative adaptive table. Their purpose is to measure error and speed-up against the completed full reference.

## Notes

- Global variables are dense over cycles 1-1000.
- Local hole-ring variables are available at selected cycles `1, 2, 10, 50, 100, 250, 500, 750, 1000`.
- The first table is conservative because local STATEV values remain sensitive even after global RF and loop-area quantities become comparatively stable.
- The next implementation step is to use this table to prepare fixed cycle-jump validation decks with the locked 16-CPU production launcher.
