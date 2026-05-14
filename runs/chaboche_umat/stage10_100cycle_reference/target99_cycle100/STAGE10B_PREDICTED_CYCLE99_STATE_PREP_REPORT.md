# Stage 10B Predicted Cycle-99 State Preparation Report

## Purpose

Prepare the formula-selected Stage 10B adaptive target for direct FE validation.

## Setup

- Route: cycle 10 -> predicted cycle 99 -> cycle 100
- Base cycle: `10`
- Target injection cycle: `99`
- Continuation/reference cycle: `100`
- DeltaN_restart: `89`
- Skipped intermediate FE cycles: `88`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle99 = value_cycle10 + DeltaN * mean_increment_per_cycle`

No validated Stage 5B/6D UMAT, deck, or ODB files are modified. All Stage 10B files are local to this folder.

## Key Prediction Errors Against Exact Cycle 99 History Row

- Predicted STATEV1: `0.709773185197`
- Exact cycle-99 STATEV1: `0.704966962337`
- STATEV1 relative error: `0.681765687914%`
- Predicted S11: `364.75845676 MPa`
- Exact cycle-99 S11: `330.899841309 MPa`
- S11 relative error: `10.2322851886%`

## Cycle-100 History Row Reference

- Reference STATEV1: `0.712048649788`
- Reference S11: `371.760040283 MPa`
- Reference RIGHT_FACE RF1: `1487.04016113`

The final result postprocessor uses exact-time interpolation from the 100-cycle ODB at time 100.0.

## Generated Files

- Predicted STATEV CSV: `cycle99_predicted_statev_for_injection.csv`
- Predicted stress CSV: `cycle99_predicted_stress_for_injection.csv`
- Prediction error CSV: `cycle99_predicted_vs_exact_error.csv`
- Cycle-100 reference CSV: `cycle100_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle99.f`
- Input deck: `chaboche_stage10b_predicted_cycle99_to_cycle100.inp`
- Runner: `run_stage10b_predicted_cycle99_jump.bat`
- Monitor: `monitor_stage10b_predicted_cycle99_jump.py`
- Postprocessor: `postprocess_stage10b_predicted_cycle99_jump.py`
