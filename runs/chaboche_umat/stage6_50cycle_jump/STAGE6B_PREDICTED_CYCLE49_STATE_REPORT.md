# Stage 6B.1 Predicted Cycle-49 State Report

## Purpose

This report prepares the predicted cycle-49 state for a larger 50-cycle FE cycle-jump validation. The intended FE test is: cycle-10 data -> predicted cycle-49 state -> one computed continuation cycle -> comparison with explicit cycle-50 reference.

Exact cycle-49 data from the no-skip 50-cycle reference are used only for validation/error comparison.

## Method

- Base cycle: `10`
- Target cycle: `49`
- DeltaN: `39`
- Actually skipped intermediate FE cycles in the next test: `38`
- Cycle-jump route computed cycles: `10` base cycles + `1` continuation cycle = `11` cycles
- Full no-skip reference cycles: `50`
- Mean increment window: cycles `2-10`
- Prediction formula: `predicted_cycle49 = value_cycle10 + DeltaN * mean_increment_per_cycle`
- STATEV14 policy: recomputed from predicted STATEV1 using `Q*(1-exp(-b*STATEV1))`
- STATEV15 policy: reset to `0` for injection

No Abaqus rerun was performed. No UMAT or Abaqus input deck was modified.

## Key Validation Errors

| Quantity | Predicted cycle-49 | Exact cycle-49 | Absolute error | Relative error |
|---|---:|---:|---:|---:|
| STATEV1 | 0.350499925669 | 0.349483847618 | 0.00101607805134 | 0.290736770316% |
| STATEV2 | -78.5683670043 | -85.7298660278 | 7.16149902346 | 8.35356376404% |
| STATEV3 | 39.2841835022 | 42.8649330139 | 3.58074951173 | 8.35356376403% |
| STATEV4 | 39.2841835022 | 42.8649330139 | 3.58074951173 | 8.35356376403% |
| STATEV8 | -0.0018551691901 | -0.00178434595 | 7.08232400963e-05 | 3.96914287256% |
| STATEV9 | 0.000927584595047 | 0.000892172975 | 3.54116200471e-05 | 3.96914287245% |
| STATEV10 | 0.000927584595047 | 0.000892172975 | 3.54116200471e-05 | 3.96914287245% |
| S11 | 348.668233236 | 333.795471191 | 14.872762045 | 4.45565123814% |

## Cycle-50 Reference for Intended Stage 6B.2 Comparison

- Final explicit cycle-50 STATEV1: `0.356620669365`
- Final explicit cycle-50 S11: `374.653869629 MPa`
- Final explicit cycle-50 RIGHT_FACE RF1: `1498.61547852`

## Interpretation

- Predicted cycle-49 STATEV1 absolute error: `0.00101607805134`
- Predicted cycle-49 STATEV1 relative error: `0.290736770316%`
- Predicted cycle-49 S11 absolute error: `14.872762045 MPa`
- Predicted cycle-49 S11 relative error: `4.45565123814%`
- Active STATEV components predicted directly: `STATEV1, STATEV2-4, STATEV8-10`
- Near-zero shear components were predicted and flagged: `STATEV5-7, STATEV11-13`
- This is the input-state quality check for Stage 6B.2; the FE injection run should only proceed if these errors are acceptable.

## Outputs

- Predicted STATEV CSV: `stage6_50cycle_jump\cycle49_predicted_statev_for_injection.csv`
- Predicted stress CSV: `stage6_50cycle_jump\cycle49_predicted_stress_for_injection.csv`
- Error CSV: `stage6_50cycle_jump\cycle49_predicted_vs_exact_error.csv`
