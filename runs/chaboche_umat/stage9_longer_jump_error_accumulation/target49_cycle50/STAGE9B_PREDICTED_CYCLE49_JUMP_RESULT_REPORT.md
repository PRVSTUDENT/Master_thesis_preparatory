# Stage 9B Predicted Cycle-49 FE Jump Result Report

## Purpose

Validate the Stage 9 grouped adaptive recommendation: cycle 10 data -> predicted cycle 49 state -> one computed cycle to cycle 50.

## Route

- Base cycle: `10`
- Predicted injection cycle: `49`
- Continuation/reference cycle: `50`
- DeltaN_restart: `39`
- Skipped intermediate FE cycles: `38`

## Abaqus Status

- Datacheck job: `chaboche_stage9b_predicted_cycle49_to_cycle50_check`
- Datacheck status: `completed`
- Full analysis job: `chaboche_stage9b_predicted_cycle49_to_cycle50`
- Full analysis status: `completed`
- Final `.sta` status: `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`

## Key Values

| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |
|---|---:|---:|---:|---:|
| First output frame | 0 | 0.350499927998 | 348.668243408 | 1394.67297363 |
| Final output frame | 1 | 0.357523173094 | 374.458190918 | 1497.83276367 |

## Injection Check

- Expected injected STATEV1: `0.350499925669`
- First-frame STATEV1 absolute error: `2.32824909352e-09`
- Expected injected S11: `348.668233236 MPa`
- First-frame S11 absolute error: `1.01722257e-05 MPa`

## Reference Handling

- Explicit reference ODB: `../../chaboche_vp_v1_cyclic_eps005_50cycles.odb`
- Reference time: `50`
- Reference source: `linear_interpolation_between_bracketing_50cycle_ODB_frames`
- Lower bracketing frame: `50`
- Upper bracketing frame: `50`
- Interpolation alpha: `0`

## Final Cycle-50 Comparison

- Reference cycle-50 STATEV1: `0.356620669365`
- Final STATEV1 absolute error: `0.000902503728867`
- Final STATEV1 relative error percent: `0.253071065812`
- Reference cycle-50 S11: `374.653869629 MPa`
- Final S11 absolute error: `0.195678710938 MPa`
- Final S11 relative error percent: `0.0522291978811`
- Reference cycle-50 RIGHT_FACE RF1: `1498.61547852`
- Final RIGHT_FACE RF1 absolute error: `0.78271484375`
- Final RIGHT_FACE RF1 relative error percent: `0.0522291978811`

## Decision

- Final STATEV1 below 1% error: `yes`
- Final S11 below 1% error: `yes`
- Final S11 below 3% error: `yes`
- Stage 9 DeltaN = 39 accepted: `yes`
- Stage 9B outcome: `accepted_clean_success`

## Outputs

- Result CSV: `stage9b_predicted_cycle49_jump_result.csv`
- Reference CSV: `cycle50_reference_statev_stress.csv`
