# Stage 11B Predicted Cycle-499 FE Jump Result Report

## Purpose

Validate the manually selected Stage 11B long-horizon stress test: cycle 10 data -> predicted cycle 499 state -> one computed cycle to cycle 500.

## Route

- Base cycle: `10`
- Predicted injection cycle: `499`
- Continuation/reference cycle: `500`
- DeltaN_test: `489`
- Skipped intermediate FE cycles: `488`

## Abaqus Status

- Datacheck job: `chaboche_stage11b_predicted_cycle499_to_cycle500_check`
- Datacheck status: `completed`
- Full analysis job: `chaboche_stage11b_predicted_cycle499_to_cycle500`
- Full analysis status: `completed`
- Final `.sta` status: `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`

## Key Values

| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |
|---|---:|---:|---:|---:|
| First output frame | 0 | 3.58395934105 | 493.480255127 | 1973.92102051 |
| Final output frame | 1 | 3.59111475945 | 354.311096191 | 1417.24438477 |

## Injection Check

- Expected injected STATEV1: `3.58395926142`
- First-frame STATEV1 absolute error: `7.96278540882e-08`
- Expected injected S11: `493.480244955 MPa`
- First-frame S11 absolute error: `1.0172005716e-05 MPa`

## Reference Handling

- Explicit reference ODB: `../reference_500cycles/chaboche_vp_v1_cyclic_eps005_500cycles.odb`
- Reference time: `500`
- Reference source: `linear_interpolation_between_bracketing_500cycle_ODB_frames`
- Lower bracketing frame: `500`
- Upper bracketing frame: `500`
- Interpolation alpha: `0`

## Final Cycle-500 Comparison

- Reference cycle-500 STATEV1: `3.46304321289`
- Final STATEV1 absolute error: `0.128071546555`
- Final STATEV1 relative error percent: `3.69823703261`
- Reference cycle-500 S11: `351.021270752 MPa`
- Final S11 absolute error: `3.28982543945 MPa`
- Final S11 relative error percent: `0.937215409313`
- Reference cycle-500 RIGHT_FACE RF1: `1404.08508301`
- Final RIGHT_FACE RF1 absolute error: `13.1593017578`
- Final RIGHT_FACE RF1 relative error percent: `0.937215409313`

## Decision

- Final STATEV1 below 1% error: `no`
- Final S11 below 1% error: `yes`
- Final S11 below 3% error: `yes`
- Stage 11B DeltaN_test = 489 accepted: `no`
- Stage 11B outcome: `not_accepted`

## Outputs

- Result CSV: `stage11b_predicted_cycle499_jump_result.csv`
- Reference CSV: `cycle500_reference_statev_stress.csv`
