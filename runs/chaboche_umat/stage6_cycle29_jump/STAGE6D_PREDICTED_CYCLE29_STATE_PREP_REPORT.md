# Stage 6D Predicted Cycle-29 State Preparation Report

## Purpose

Prepare the predicted cycle-29 injection state selected by the Stage 6C multi-target scan.

## Setup

- Base cycle: `10`
- Target injection cycle: `29`
- Continuation/reference cycle: `30`
- DeltaN: `19`
- Skipped intermediate FE cycles: `18`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle29 = value_cycle10 + DeltaN * mean_increment_per_cycle`

No Abaqus run was performed by this preparation script.

## Key Prediction Errors Against Exact Cycle 29

- Predicted STATEV1: `0.206790621858`
- Exact cycle-29 STATEV1: `0.20651113987`
- STATEV1 relative error: `0.135335066339%`
- Predicted S11: `342.232143826 MPa`
- Exact cycle-29 S11: `334.9793396 MPa`
- S11 relative error: `2.16514971786%`

## Cycle-30 Reference

- Reference STATEV1: `0.213670507073`
- Reference S11: `334.919799805 MPa`
- Reference RIGHT_FACE RF1: `1339.67919922`
- Note: these values came from the nearest cycle-history row. The final Stage 6D result report supersedes this for FE comparison by interpolating the explicit 50-cycle ODB at exact time `30.0`, because the nearest history row is at time `29.9902572632`.

## Generated Files

- Predicted STATEV CSV: `stage6_cycle29_jump\cycle29_predicted_statev_for_injection.csv`
- Predicted stress CSV: `stage6_cycle29_jump\cycle29_predicted_stress_for_injection.csv`
- Prediction error CSV: `stage6_cycle29_jump\cycle29_predicted_vs_exact_error.csv`
- Cycle-30 reference CSV: `stage6_cycle29_jump\cycle30_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle29.f`
- Input deck: `chaboche_stage6d_predicted_cycle29_to_cycle30.inp`
- Runner: `run_stage6d_predicted_cycle29_jump.bat`
- Monitor: `monitor_stage6d_predicted_cycle29_jump.py`
- Postprocessor: `postprocess_stage6d_predicted_cycle29_jump.py`
