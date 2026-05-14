# Stage 11B Predicted Cycle-499 State Preparation Report

## Purpose

Prepare a manually selected long-horizon Stage 11B target for direct FE validation.

## Setup

- Route: cycle 10 -> predicted cycle 499 -> cycle 500
- Base cycle: `10`
- Target injection cycle: `499`
- Continuation/reference cycle: `500`
- DeltaN_test: `489`
- Skipped intermediate FE cycles: `488`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle499 = value_cycle10 + DeltaN * mean_increment_per_cycle`

No validated Stage 5B/6D UMAT, deck, or ODB files are modified. All Stage 11B files are local to this folder.

## Key Prediction Errors Against Exact Cycle 499 History Row

- Predicted STATEV1: `3.58395926142`
- Exact cycle-499 STATEV1: `3.45635652542`
- STATEV1 relative error: `3.6918279426%`
- Predicted S11: `493.480244955 MPa`
- Exact cycle-499 S11: `310.150787354 MPa`
- S11 relative error: `59.109783072%`

## Cycle-500 History Row Reference

- Reference STATEV1: `3.46304321289`
- Reference S11: `351.021270752 MPa`
- Reference RIGHT_FACE RF1: `1404.08508301`

The final result postprocessor uses exact-time interpolation from the 500-cycle ODB at time 500.0.

## Generated Files

- Predicted STATEV CSV: `cycle499_predicted_statev_for_injection.csv`
- Predicted stress CSV: `cycle499_predicted_stress_for_injection.csv`
- Prediction error CSV: `cycle499_predicted_vs_exact_error.csv`
- Cycle-500 reference CSV: `cycle500_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle499.f`
- Input deck: `chaboche_stage11b_predicted_cycle499_to_cycle500.inp`
- Runner: `run_stage11b_predicted_cycle499_jump.bat`
- Monitor: `monitor_stage11b_predicted_cycle499_jump.py`
- Postprocessor: `postprocess_stage11b_predicted_cycle499_jump.py`

