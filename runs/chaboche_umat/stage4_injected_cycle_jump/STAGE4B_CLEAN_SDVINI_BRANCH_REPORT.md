# Stage 4B Clean SDVINI Branch Report

## Inputs

- ODB: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean.odb`
- Clean UMAT: `umat_chaboche_v1_with_sdvini_clean.f`
- Clean input deck: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean.inp`

## Key STATEV1 Values

| Frame | Time | STATEV1 | S11 (MPa) |
|---|---:|---:|---:|
| First output frame | 0 | 0.13485494256 | 0 |
| Final output frame | 1 | 0.14071752131 | 368.581756592 |

Expected injected STATEV1: `0.13485494256`
Reference cycle-20 STATEV1: `0.142025694251`

## Interpretation

- First output STATEV1 matches injected cycle-19 value within `1e-6`: `yes`
- Final output STATEV1 is near explicit cycle-20 reference within `1e-3`: `no`
- First-frame absolute error from injected STATEV1: `0`
- Final-frame absolute error from cycle-20 reference: `0.00130817294121`

Note: This clean branch removes debug instrumentation while preserving the proven standard SDVINI signature and `*INITIAL CONDITIONS, TYPE=SOLUTION, USER` activation.

## Output

- CSV: `stage4_injected_cycle_jump/stage4b_clean_sdvini_first_final.csv`
