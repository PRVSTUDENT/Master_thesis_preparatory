# Stage 9A Predicted Cycle-39 FE Jump Result Report

## Purpose

Validate the Stage 9 grouped adaptive recommendation: cycle 10 data -> predicted cycle 39 state -> one computed cycle to cycle 40.

## Route

- Base cycle: `10`
- Predicted injection cycle: `39`
- Continuation/reference cycle: `40`
- DeltaN_restart: `29`
- Skipped intermediate FE cycles: `28`

## Abaqus Status

- Datacheck job: `chaboche_stage9a_predicted_cycle39_to_cycle40_check`
- Datacheck status: `completed`
- Full analysis job: `chaboche_stage9a_predicted_cycle39_to_cycle40`
- Full analysis status: `completed`
- Final `.sta` status: `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`

## Key Values

| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |
|---|---:|---:|---:|---:|
| First output frame | 0 | 0.278645277023 | 345.450195312 | 1381.80078125 |
| Final output frame | 1 | 0.285667210817 | 374.954284668 | 1499.81713867 |

## Injection Check

- Expected injected STATEV1: `0.278645273764`
- First-frame STATEV1 absolute error: `3.25957538738e-09`
- Expected injected S11: `345.450188531 MPa`
- First-frame S11 absolute error: `6.78138860621e-06 MPa`

## Reference Handling

- Explicit reference ODB: `../../chaboche_vp_v1_cyclic_eps005_50cycles.odb`
- Reference time: `40`
- Reference source: `linear_interpolation_between_bracketing_50cycle_ODB_frames`
- Lower bracketing frame: `39.9902572632`
- Upper bracketing frame: `40.0102577209`
- Interpolation alpha: `0.487125691398`

## Final Cycle-40 Comparison

- Reference cycle-40 STATEV1: `0.285242454471`
- Final STATEV1 absolute error: `0.000424756346462`
- Final STATEV1 relative error percent: `0.148910633675`
- Reference cycle-40 S11: `366.748147263 MPa`
- Final S11 absolute error: `8.20613740451 MPa`
- Final S11 relative error percent: `2.23754024819`
- Reference cycle-40 RIGHT_FACE RF1: `1466.99258905`
- Final RIGHT_FACE RF1 absolute error: `32.8245496181`
- Final RIGHT_FACE RF1 relative error percent: `2.23754024819`

## Decision

- Final STATEV1 below 1% error: `yes`
- Final S11 below 1% error: `no`
- Final S11 below 3% error: `yes`
- Stage 9 DeltaN = 29 accepted: `yes`
- Stage 9A outcome: `accepted_exploratory_success`

## Outputs

- Result CSV: `stage9a_predicted_cycle39_jump_result.csv`
- Reference CSV: `cycle40_reference_statev_stress.csv`
