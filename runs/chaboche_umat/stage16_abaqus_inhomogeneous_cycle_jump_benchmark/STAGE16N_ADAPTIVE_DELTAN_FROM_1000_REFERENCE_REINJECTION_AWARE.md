# Stage 16N-A Reinjection-Aware Adaptive DeltaN Table

This table is derived from the completed 1000-cycle reference, but it applies the B0 initialization-audit conclusion.

## Key change from the original table

`HOLE_RING_SDV8_MAX` is reported as diagnostic-only and removed from the hard controller list because it already shows a large error immediately after manual `SDVINI/SIGINI` initialization.

Hard controller variables:

```text
RF1_max
RF1_min_abs
loop_area_abs
HOLE_RING_MISES_MAX
HOLE_RING_S11_MAX_ABS
HOLE_RING_SDV1_MAX
HOLE_RING_SDV11_MAX
```

Diagnostic-only variables:

```text
HOLE_RING_SDV8_MAX
```

## Reinjection-aware DeltaN estimate

| Base cycle | Recommended target | DeltaN | Controlling variable | Change to next anchor | Decision |
| ---: | ---: | ---: | --- | ---: | --- |
| 1 | 2 | 1 | HOLE_RING_SDV11_MAX | 66.10% | simulate_next_cycle_without_jump |
| 2 | 3 | 1 | HOLE_RING_SDV1_MAX | 73.87% | simulate_next_cycle_without_jump |
| 10 | 15 | 5 | HOLE_RING_SDV1_MAX | 76.71% | adaptive_deltaN_limited_before_next_selected_anchor |
| 50 | 61 | 11 | HOLE_RING_SDV1_MAX | 44.89% | adaptive_deltaN_limited_before_next_selected_anchor |
| 100 | 124 | 24 | HOLE_RING_SDV1_MAX | 60.34% | adaptive_deltaN_limited_before_next_selected_anchor |
| 250 | 299 | 49 | HOLE_RING_SDV1_MAX | 50.83% | adaptive_deltaN_limited_before_next_selected_anchor |
| 500 | 575 | 75 | HOLE_RING_SDV1_MAX | 33.29% | adaptive_deltaN_limited_before_next_selected_anchor |
| 750 | 849 | 99 | HOLE_RING_MISES_MAX | 12.61% | adaptive_deltaN_limited_before_next_selected_anchor |

## Interpretation

The recommended fixed first case remains `100 -> 125, continue to 250`. This row is controlled by `HOLE_RING_SDV1_MAX`, so the B0 SDV8 limitation does not invalidate the first conservative fixed-jump gate.
