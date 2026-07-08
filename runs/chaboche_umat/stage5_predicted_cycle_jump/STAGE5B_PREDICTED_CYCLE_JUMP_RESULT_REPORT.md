# Stage 5B Predicted FE Cycle-Jump Result Report

## Inputs

- ODB: `chaboche_stage5b_predicted_cycle19_to_cycle20.odb`
- Predicted UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle19.f`
- Predicted input deck: `chaboche_stage5b_predicted_cycle19_to_cycle20.inp`
- Stage 5A state report: `stage5_predicted_cycle_jump/STAGE5A_PREDICTED_CYCLE19_STATE_REPORT.md`

## Key STATEV1 Values

| Frame | Time | STATEV1 | S11 (MPa) |
|---|---:|---:|---:|
| First output frame | 0 | 0.134935975075 | 339.014099121 |
| Final output frame | 1 | 0.141955494881 | 375.95602417 |

## Boundary Output

- RIGHT_FACE node set resolved as: `RIGHT_FACE`
- Final RIGHT_FACE average U1: `0`
- Final RIGHT_FACE summed RF1: `1503.82409668`

Expected injected STATEV1: `0.134935969953`
Expected initial S11: `339.014099121`
Reference cycle-20 STATEV1: `0.142025694251`
Reference cycle-20 S11: `376.434143066`

## Interpretation

- First output STATEV1 matches injected cycle-19 value within `1e-6`: `yes`
- First output S11 matches injected residual stress within `1e-3`: `yes`
- Final output STATEV1 is near explicit cycle-20 reference within `1e-3`: `yes`
- Final STATEV1 is closer than the clean STATEV-only branch: `yes`
- Final output S11 is near explicit cycle-20 reference within `1e-3`: `no`
- Final STATEV1 is within 1% of explicit cycle-20 reference: `yes`
- Final S11 is within 1% of explicit cycle-20 reference: `yes`
- First-frame absolute error from injected STATEV1: `5.12176806522e-09`
- First-frame absolute error from injected S11: `9.37347977015e-11`
- Final-frame absolute error from cycle-20 reference: `7.01993703842e-05`
- Final-frame S11 absolute error from cycle-20 reference: `0.478118896484`
- Final-frame STATEV1 relative error percent: `0.049427232695`
- Final-frame S11 relative error percent: `0.127012627651`
- Difference from exact-state SIGINI final STATEV1: `9.21934846763e-05`
- Difference from exact-state SIGINI final S11: `0.0900268559218`
- Successful first FE cycle-skipping demonstration by 1% criteria: `yes`

Note: This branch injects a predicted cycle-19 state produced from cycle-10 data, then runs one computed cycle to cycle 20.

## Output

- CSV: `stage5_predicted_cycle_jump/stage5b_predicted_cycle_jump_result.csv`
