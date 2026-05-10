# Stage 7C Predicted Cycle-27 State Preparation Report

## Purpose

Prepare the formula-selected Stage 7B adaptive target for direct FE validation.

## Setup

- Route: cycle 10 -> predicted cycle 27 -> cycle 28
- Base cycle: `10`
- Target injection cycle: `27`
- Continuation/reference cycle: `28`
- DeltaN_restart: `17`
- Skipped intermediate FE cycles: `16`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle27 = value_cycle10 + DeltaN * mean_increment_per_cycle`

No validated Stage 5B/6D UMAT, deck, or ODB files are modified. All Stage 7C files are local to this folder.

## Key Prediction Errors Against Exact Cycle 27 History Row

- Predicted STATEV1: `0.192419691477`
- Exact cycle-27 STATEV1: `0.192188993096`
- STATEV1 relative error: `0.12003724943%`
- Predicted S11: `341.588534885 MPa`
- Exact cycle-27 S11: `335.09854126 MPa`
- S11 relative error: `1.93674183148%`

## Cycle-28 History Row Reference

- Reference STATEV1: `0.199350625277`
- Reference S11: `335.038909912 MPa`
- Reference RIGHT_FACE RF1: `1340.15563965`

The final result postprocessor uses exact-time interpolation from the 50-cycle ODB at time 28.0.

## Generated Files

- Predicted STATEV CSV: `cycle27_predicted_statev_for_injection.csv`
- Predicted stress CSV: `cycle27_predicted_stress_for_injection.csv`
- Prediction error CSV: `cycle27_predicted_vs_exact_error.csv`
- Cycle-28 reference CSV: `cycle28_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle27.f`
- Input deck: `chaboche_stage7c_predicted_cycle27_to_cycle28.inp`
- Runner: `run_stage7c_predicted_cycle27_jump.bat`
- Monitor: `monitor_stage7c_predicted_cycle27_jump.py`
- Postprocessor: `postprocess_stage7c_predicted_cycle27_jump.py`
