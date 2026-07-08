# Stage 4B SIGINI Result Report

## Inputs

- ODB: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini.odb`
- SIGINI UMAT: `umat_chaboche_v1_with_sdvini_sigini.f`
- SIGINI input deck: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini.inp`

## Key STATEV1 Values

| Frame | Time | STATEV1 | S11 (MPa) |
|---|---:|---:|---:|
| First output frame | 0 | 0.13485494256 | 335.576873779 |
| Final output frame | 1 | 0.141863301396 | 375.865997314 |

## Boundary Output

- RIGHT_FACE node set resolved as: `RIGHT_FACE`
- Final RIGHT_FACE average U1: `0`
- Final RIGHT_FACE summed RF1: `1503.46398926`

Expected injected STATEV1: `0.13485494256`
Expected initial S11: `335.576873779`
Reference cycle-20 STATEV1: `0.142025694251`
Reference cycle-20 S11: `376.434143066`

## Interpretation

- First output STATEV1 matches injected cycle-19 value within `1e-6`: `yes`
- First output S11 matches injected residual stress within `1e-3`: `yes`
- Final output STATEV1 is near explicit cycle-20 reference within `1e-3`: `yes`
- Final STATEV1 is closer than the clean STATEV-only branch: `yes`
- Final output S11 is near explicit cycle-20 reference within `1e-3`: `no`
- First-frame absolute error from injected STATEV1: `0`
- First-frame absolute error from injected S11: `0`
- Final-frame absolute error from cycle-20 reference: `0.000162392854691`
- Final-frame S11 absolute error from cycle-20 reference: `0.568145751953`

Note: This branch activates both `*INITIAL CONDITIONS, TYPE=SOLUTION, USER` and `*INITIAL CONDITIONS, TYPE=STRESS, USER`.

## Output

- CSV: `stage4_injected_cycle_jump/stage4b_sigini_result.csv`
