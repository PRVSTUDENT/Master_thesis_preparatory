# Stage 9A Predicted Cycle-39 State Preparation Report

## Purpose

Prepare the formula-selected Stage 9 adaptive target for direct FE validation.

## Setup

- Route: cycle 10 -> predicted cycle 39 -> cycle 40
- Base cycle: `10`
- Target injection cycle: `39`
- Continuation/reference cycle: `40`
- DeltaN_restart: `29`
- Skipped intermediate FE cycles: `28`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle39 = value_cycle10 + DeltaN * mean_increment_per_cycle`

No validated Stage 5B/6D UMAT, deck, or ODB files are modified. All Stage 9A files are local to this folder.

## Key Prediction Errors Against Exact Cycle 27 History Row

- Predicted STATEV1: `0.278645273764`
- Exact cycle-39 STATEV1: `0.278053849936`
- STATEV1 relative error: `0.212701182838%`
- Predicted S11: `345.450188531 MPa`
- Exact cycle-39 S11: `334.385559082 MPa`
- S11 relative error: `3.30894356786%`

## Cycle-40 History Row Reference

- Reference STATEV1: `0.285201907158`
- Reference S11: `334.326385498 MPa`
- Reference RIGHT_FACE RF1: `1337.30554199`

The final result postprocessor uses exact-time interpolation from the 50-cycle ODB at time 28.0.

## Generated Files

- Predicted STATEV CSV: `cycle39_predicted_statev_for_injection.csv`
- Predicted stress CSV: `cycle39_predicted_stress_for_injection.csv`
- Prediction error CSV: `cycle39_predicted_vs_exact_error.csv`
- Cycle-40 reference CSV: `cycle40_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle39.f`
- Input deck: `chaboche_stage9a_predicted_cycle39_to_cycle40.inp`
- Runner: `run_stage9a_predicted_cycle39_jump.bat`
- Monitor: `monitor_stage9a_predicted_cycle39_jump.py`
- Postprocessor: `postprocess_stage9a_predicted_cycle39_jump.py`
