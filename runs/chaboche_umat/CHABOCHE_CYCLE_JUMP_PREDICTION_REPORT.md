# Chaboche-v1 cycle-jump prediction report

## Purpose

This postprocessing-level cycle-jump demonstration uses the stabilized per-cycle increment of accumulated viscoplastic strain from the explicit 10-cycle Abaqus baseline to estimate long-cycle SDV1 growth without rerunning Abaqus.

Total SDV1 is accumulated viscoplastic strain p, so it is cumulative and should increase monotonically. The correct stabilization metric is Delta_SDV1 per cycle, because that measures whether the cyclic plastic strain rate has settled.

## Reference Window

- Reference cycles: 2-10
- Mean Delta_SDV1: 0.007185465191
- Standard deviation of Delta_SDV1: 3.368213202e-06
- Relative range of Delta_SDV1: 0.001429037192
- Mean stress amplitude: 671.5717095 MPa
- Mean mean-stress: -0.05007595486 MPa
- Mean residual stress at zero strain: 340.8964505 MPa

## Predictions

| target cycle | predicted SDV1 | cycles skipped |
|---:|---:|---:|
| 20 | 0.1421214351 | 10 |
| 50 | 0.3576853909 | 40 |
| 100 | 0.7169586504 | 90 |
| 200 | 1.435505169 | 190 |
| 500 | 3.591144727 | 490 |
| 1000 | 7.183877322 | 990 |

## Scope

This is a postprocessing-level cycle-jump predictor, not yet an Abaqus restart with injected STATEV. The next implementation step would be to use SDVINI or initial solution-dependent variables to start Abaqus from a jumped internal state.

## Generated files

- cycle_jump_predictor_from_10cycles.py
- chaboche_cycle_jump_predictions.csv
- chaboche_cycle_jump_curve_1_to_1000.csv
- chaboche_cycle_jump_sdv1_prediction.svg
- chaboche_cycle_jump_delta_sdv1_reference.svg
- CHABOCHE_CYCLE_JUMP_PREDICTION_REPORT.md
