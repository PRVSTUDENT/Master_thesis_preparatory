# Stage 7C Predicted Cycle-27 FE Jump Result Report

## Purpose

Validate the Stage 7B grouped adaptive recommendation: cycle 10 data -> predicted cycle 27 state -> one computed cycle to cycle 28.

## Route

- Base cycle: `10`
- Predicted injection cycle: `27`
- Continuation/reference cycle: `28`
- DeltaN_restart: `17`
- Skipped intermediate FE cycles: `16`

## Abaqus Status

- Datacheck job: `chaboche_stage7c_predicted_cycle27_to_cycle28_check`
- Datacheck status: `completed`
- Full analysis job: `chaboche_stage7c_predicted_cycle27_to_cycle28`
- Full analysis status: `completed`
- Final `.sta` status: `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`

## Key Values

| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |
|---|---:|---:|---:|---:|
| First output frame | 0 | 0.192419692874 | 341.588531494 | 1366.35412598 |
| Final output frame | 1 | 0.199440136552 | 375.55380249 | 1502.21520996 |

## Injection Check

- Expected injected STATEV1: `0.192419691477`
- First-frame STATEV1 absolute error: `1.39693476231e-09`
- Expected injected S11: `341.588534885 MPa`
- First-frame S11 absolute error: `3.39113159953e-06 MPa`

## Reference Handling

- Explicit reference ODB: `../chaboche_vp_v1_cyclic_eps005_50cycles.odb`
- Reference time: `28`
- Reference source: `linear_interpolation_between_bracketing_50cycle_ODB_frames`
- Lower bracketing frame: `27.9902572632`
- Upper bracketing frame: `28.0102577209`
- Interpolation alpha: `0.487125691398`

## Final Cycle-28 Comparison

- Reference cycle-28 STATEV1: `0.199393959945`
- Final STATEV1 absolute error: `4.61766067498e-05`
- Final STATEV1 relative error percent: `0.0231584782019`
- Reference cycle-28 S11: `366.877348771 MPa`
- Final S11 absolute error: `8.67645371936 MPa`
- Final S11 relative error percent: `2.36494669088`
- Reference cycle-28 RIGHT_FACE RF1: `1467.50939508`
- Final RIGHT_FACE RF1 absolute error: `34.7058148774`
- Final RIGHT_FACE RF1 relative error percent: `2.36494669088`

## Decision

- Final STATEV1 below 1% error: `yes`
- Final S11 below 1% error: `no`
- Final S11 below 3% error: `yes`
- Stage 7B DeltaN = 17 accepted: `yes`
- Stage 7C outcome: `accepted_exploratory_success`

## Outputs

- Result CSV: `stage7c_predicted_cycle27_jump_result.csv`
- Reference CSV: `cycle28_reference_statev_stress.csv`
