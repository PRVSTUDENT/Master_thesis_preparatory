# Stage 16N-R4J Non-Monotonic Audit

Date: 2026-06-15

## Reason for audit

The R4J7/R4J8 true-skip refinement results are scientifically important but non-monotonic:

| Case | True skip | Endpoint | Max primary local error | Controlling primary metric |
|---|---:|---:|---:|---|
| R4J5 | +35 | 500 | 6.9643175% | `HOLE_RING_SDV1_MAX` |
| R4J7 | +30 | 500 | 11.829104% | `HOLE_RING_SDV8_MAX` |
| R4J6 | +10 | 750 | 7.2880782% | `HOLE_RING_SDV8_MAX` |
| R4J8 | +5 | 750 | 13.598377% | `HOLE_RING_MISES_MAX` |

A smaller nominal skipped increment produced a larger local maximum error on both branches. This can happen with max-over-location hole-ring metrics, but it means the bracket should be treated as provisional until an exact-target true-skip diagnostic separates extrapolation error from setup/comparison error.

## Worst-row details

R4J7 compared at cycle 500:

| Metric | Jump value | Reference value | Error |
|---|---:|---:|---:|
| `HOLE_RING_MISES_MAX` | 489.778869594 | 493.082414121 | 0.66997817% |
| `HOLE_RING_SDV1_MAX` | 12.2703037262 | 13.0502681732 | 5.9766162% |
| `HOLE_RING_SDV8_MAX` | 80.6564712524 | 91.477432251 | 11.829104% |
| `HOLE_RING_SDV11_MAX` | 54.3771820068 | 60.1659240723 | 9.6212967% |
| `HOLE_RING_S11_MAX_ABS` | 541.111328125 | 536.128723145 | 0.92936729% |

R4J8 compared at cycle 750:

| Metric | Jump value | Reference value | Error |
|---|---:|---:|---:|
| `HOLE_RING_MISES_MAX` | 489.269004328 | 430.700698148 | 13.598377% |
| `HOLE_RING_SDV1_MAX` | 19.4337921143 | 19.5627155304 | 0.65902618% |
| `HOLE_RING_SDV8_MAX` | 79.1257629395 | 84.4680480957 | 6.3246225% |
| `HOLE_RING_SDV11_MAX` | 54.0707015991 | 57.0726051331 | 5.2597976% |
| `HOLE_RING_S11_MAX_ABS` | 541.593200684 | 479.236755371 | 13.011616% |

## Setup checks

- R4J7 first solved deck step: `*STEP, NAME=CYCLE_0281`.
- R4J8 first solved deck step: `*STEP, NAME=CYCLE_0506`.
- R4J7 overwrite hook fired at `JSTEP(1)=251`, `KINC=0`, corresponding to the cycle-250 native restart continuation hook.
- R4J8 overwrite hook fired at `JSTEP(1)=501`, `KINC=0`, corresponding to the cycle-500 native restart continuation hook.
- R4J7 endpoint comparison is cycle 500.
- R4J8 endpoint comparison is cycle 750.
- The current exported comparison CSVs report global and hole-ring scalar maxima, but they do not include the element or integration-point identity of each maximum. A deeper location-level audit requires extending the extractor or reading the ODB fields directly.

## Prepared diagnostic controls

Exact-target true-skip controls were prepared but not submitted:

| Case | Restart | Exact overwrite target | Solved cycles | Purpose |
|---|---:|---:|---:|---|
| `R4E1_250_to_280_exact_solve_281_to_500` | 250 | 280 | 281--500 | Check whether the R4J7 deck phase and comparison pass when extrapolation error is removed. |
| `R4E2_500_to_505_exact_solve_506_to_750` | 500 | 505 | 506--750 | Check whether the R4J8 deck phase and comparison pass when extrapolation error is removed. |

Expected first solved steps:

```text
R4E1: *STEP, NAME=CYCLE_0281
R4E2: *STEP, NAME=CYCLE_0506
```

## Current conclusion

The R4J true-skip refinement shows that the admissible jump size is strongly branch dependent and controlled by local hole-ring state variables. The cycle-250 branch has at least one accepted true skip at +20, while the cycle-500 branch failed even at +5 using the current linear extrapolation. Because the +30 and +5 tests produced larger local errors than some larger previous jumps, exact-target true-skip diagnostics are required before finalising the practical safe-jump bracket.
