# Stage 5A Predicted Cycle-19 State Report

## Purpose

This report prepares the first predicted cycle-jump state for Abaqus FE cycle skipping. It predicts cycle-19 STATEV and residual stress from cycle-10 data using a cycle-level first-order extrapolation.

Exact cycle-19 data are used only for validation/error comparison, not for prediction.

## Method

- Base cycle: `10`
- Target cycle: `19`
- DeltaN: `9`
- Mean increment window: cycles `2-10`
- Prediction formula: `predicted_cycle19 = value_cycle10 + DeltaN * mean_increment_per_cycle`
- STATEV14 policy: recomputed from predicted STATEV1 using `Q*(1-exp(-b*STATEV1))`
- STATEV15 policy: reset to `0` for injection

No Abaqus rerun was performed. No UMAT was modified.

## Key Validation Errors

| Quantity | Predicted cycle-19 | Exact cycle-19 | Absolute error | Relative error |
|---|---:|---:|---:|---:|
| STATEV1 | 0.134935969953 | 0.13485494256 | 8.10273923441e-05 | 0.0600848517717% |
| STATEV2 | -84.2407455444 | -85.8934707642 | 1.65272521977 | 1.9241569878% |
| STATEV3 | 42.1203727722 | 42.9467353821 | 0.826362609886 | 1.9241569878% |
| STATEV4 | 42.1203727722 | 42.9467353821 | 0.826362609886 | 1.9241569878% |
| STATEV8 | -0.00180919677951 | -0.00179282890167 | 1.6367877836e-05 | 0.912963742425% |
| STATEV9 | 0.000904598389752 | 0.000896414450835 | 8.18393891698e-06 | 0.912963742313% |
| STATEV10 | 0.000904598389752 | 0.000896414450835 | 8.18393891698e-06 | 0.912963742313% |
| S11 | 339.014099121 | 335.576873779 | 3.4372253418 | 1.02427360476% |

## Interpretation

- Predicted STATEV1 absolute error: `8.10273923441e-05`
- Predicted STATEV1 relative error: `0.0600848517717%`
- Predicted S11 absolute error: `3.4372253418 MPa`
- Predicted S11 relative error: `1.02427360476%`
- Active STATEV components predicted directly: `STATEV1, STATEV2-4, STATEV8-10`
- Near-zero shear components were predicted and flagged: `STATEV5-7, STATEV11-13`
- This predicted state is the candidate input for the next FE skipped-cycle continuation test.

## Outputs

- Predicted STATEV CSV: `stage5_predicted_cycle_jump\cycle19_predicted_statev_for_injection.csv`
- Predicted stress CSV: `stage5_predicted_cycle_jump\cycle19_predicted_stress_for_injection.csv`
- Error CSV: `stage5_predicted_cycle_jump\cycle19_predicted_vs_exact_error.csv`
