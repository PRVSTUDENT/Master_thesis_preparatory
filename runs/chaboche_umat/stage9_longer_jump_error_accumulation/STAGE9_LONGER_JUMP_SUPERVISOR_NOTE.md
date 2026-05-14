# Stage 9 Longer-Jump Error Accumulation Study

## Purpose

This study extends the previously validated Chaboche UMAT cycle-jump workflow to larger skipped-cycle ranges. The goal is to check how the error evolves when the predicted-state FE continuation is applied to later cycles.

The frozen Stage 5B/6D/7B/7C folders were not modified. Stage 9 was performed in an isolated folder.

## Validated Abaqus Continuation Cases

| Case | Route | DeltaN | Skipped intermediate FE cycles | STATEV1 error | S11 error | RF1 error | Outcome |
|---|---|---:|---:|---:|---:|---:|---|
| Stage 7C | cycle 10 -> predicted 27 -> cycle 28 | 17 | 16 | 0.023158% | 2.364947% | 2.364947% | accepted exploratory |
| Stage 9A | cycle 10 -> predicted 39 -> cycle 40 | 29 | 28 | 0.148911% | 2.237540% | 2.237540% | accepted exploratory |
| Stage 9B | cycle 10 -> predicted 49 -> cycle 50 | 39 | 38 | 0.253071% | 0.052229% | 0.052229% | accepted clean success |

## Long-Horizon Prediction Scan

A cheap prediction scan was also performed without additional Abaqus validation. The scan extrapolates the cycle-space trend from the stabilized cycle window and predicts values up to cycle 2000.

Selected predicted values:

| Target cycle | Predicted STATEV1 | Predicted S11 |
|---:|---:|---:|
| 100 | 0.716958650388 | 365.080261231 MPa |
| 500 | 3.59114472661 | 493.802049425 MPa |
| 1000 | 7.18387732189 | 654.704284669 MPa |
| 2000 | 14.3693425125 | 976.508755155 MPa |

These long-horizon values are screening predictions only. They are not yet validated against no-skip Abaqus references at 100, 500, 1000, or 2000 cycles.

## Interpretation

The validated Abaqus continuation results show that the accumulated viscoplastic strain error increases mildly with jump length, but remains below 0.3% up to the cycle-49 to cycle-50 validation.

The axial stress error does not increase monotonically. Stage 9A gives approximately 2.24% S11 error, while Stage 9B gives only approximately 0.052% S11 error. Therefore, the cheap prediction scan is useful for screening possible long jumps, but the final accuracy must be judged using actual Abaqus continuation validation.

## Main Conclusion

The Stage 9 results support the cycle-jump workflow beyond the previously validated Stage 7C case. The method successfully skipped up to 38 intermediate FE cycles in the cycle-49 to cycle-50 validation and still reproduced the no-skip reference with clean stress and acceptable accumulated viscoplastic strain accuracy.

## Remaining Work

For thousands of cycles, a no-skip reference is still required before a true validation error can be computed. The recommended next validation step is:

1. Generate a reduced-output no-skip 100-cycle reference.
2. Validate cycle 10 -> predicted cycle 99 -> cycle 100.
3. If stable, continue with 500-cycle and 1000-cycle references.
