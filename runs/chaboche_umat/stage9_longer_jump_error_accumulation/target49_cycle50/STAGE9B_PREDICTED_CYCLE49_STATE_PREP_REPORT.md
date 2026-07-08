# Stage 9B Predicted Cycle-49 State Preparation Report

## Purpose

Prepare the formula-selected Stage 9 adaptive target for direct FE validation.

## Setup

- Route: cycle 10 -> predicted cycle 49 -> cycle 50
- Base cycle: `10`
- Target injection cycle: `49`
- Continuation/reference cycle: `50`
- DeltaN_restart: `39`
- Skipped intermediate FE cycles: `38`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle49 = value_cycle10 + DeltaN * mean_increment_per_cycle`

No validated Stage 5B/6D UMAT, deck, or ODB files are modified. All Stage 9B files are local to this folder.

## Key Prediction Errors Against Exact Cycle 27 History Row

- Predicted STATEV1: `0.350499925669`
- Exact cycle-49 STATEV1: `0.349483847618`
- STATEV1 relative error: `0.290736770316%`
- Predicted S11: `348.668233236 MPa`
- Exact cycle-49 S11: `333.795471191 MPa`
- S11 relative error: `4.45565123814%`

## Cycle-50 History Row Reference

- Reference STATEV1: `0.356620669365`
- Reference S11: `374.653869629 MPa`
- Reference RIGHT_FACE RF1: `1498.61547852`

The final result postprocessor uses exact-time interpolation from the 50-cycle ODB at time 28.0.

## Generated Files

- Predicted STATEV CSV: `cycle49_predicted_statev_for_injection.csv`
- Predicted stress CSV: `cycle49_predicted_stress_for_injection.csv`
- Prediction error CSV: `cycle49_predicted_vs_exact_error.csv`
- Cycle-50 reference CSV: `cycle50_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle49.f`
- Input deck: `chaboche_stage9b_predicted_cycle49_to_cycle50.inp`
- Runner: `run_stage9b_predicted_cycle49_jump.bat`
- Monitor: `monitor_stage9b_predicted_cycle49_jump.py`
- Postprocessor: `postprocess_stage9b_predicted_cycle49_jump.py`
