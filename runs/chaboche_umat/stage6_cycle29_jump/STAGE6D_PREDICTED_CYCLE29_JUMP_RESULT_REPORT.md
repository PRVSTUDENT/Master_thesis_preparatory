# Stage 6D Predicted Cycle-29 FE Jump Result Report

## Purpose

Validate the larger predicted FE cycle jump selected by Stage 6C: cycle 10 data -> predicted cycle 29 state -> one computed cycle to cycle 30.

## Key Values

| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |
|---|---:|---:|---:|---:|
| First output frame | 0 | 0.206790626049 | 342.232147217 | 1368.92858887 |
| Final output frame | 1 | 0.213811308146 | 375.453552246 | 1501.81420898 |

## Injection Check

- Expected injected STATEV1: `0.206790621858`
- First-frame STATEV1 absolute error: `4.19090173676e-09`
- Expected injected S11: `342.232143826 MPa`
- First-frame S11 absolute error: `3.3905514556e-06 MPa`

## Reference Handling

- Explicit reference ODB: `chaboche_vp_v1_cyclic_eps005_50cycles.odb`
- Reference time: `30`
- Reference source: `linear_interpolation_between_bracketing_50cycle_ODB_frames`
- Lower bracketing frame: `29.9902572632`
- Upper bracketing frame: `30.0102577209`
- Interpolation alpha: `0.487125691398`
- Note: the original 50-cycle history row for cycle 30 is a pre-end frame, not exact time 30.0.

## Final Cycle-30 Comparison

- Reference cycle-30 STATEV1: `0.213713369924`
- Final STATEV1 absolute error: `9.79382215782e-05`
- Final STATEV1 relative error percent: `0.0458269043313`
- Reference cycle-30 S11: `366.855714346 MPa`
- Final S11 absolute error: `8.59783790031 MPa`
- Final S11 relative error percent: `2.34365652874`
- Reference cycle-30 RIGHT_FACE RF1: `1467.42285738`
- Final RIGHT_FACE RF1 absolute error: `34.3913516012`
- Final RIGHT_FACE RF1 relative error percent: `2.34365652874`

## Decision

- Final STATEV1 below 1% error: `yes`
- Final S11 below 1% error: `no`
- Final S11 below 3% error: `yes`
- Stage 6D outcome: `acceptable_exploratory_success`

This run skips cycles 11-28, i.e. 18 intermediate FE cycles, and replaces a 30-cycle route with 10 base cycles plus one continuation cycle.

## Output

- CSV: `stage6_cycle29_jump/stage6d_predicted_cycle29_jump_result.csv`
- Reference CSV: `stage6_cycle29_jump/cycle30_reference_statev_stress.csv`
