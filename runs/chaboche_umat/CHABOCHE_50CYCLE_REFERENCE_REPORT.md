# Chaboche-v1 50-Cycle Explicit Reference Report

## Input

- ODB: `chaboche_vp_v1_cyclic_eps005_50cycles.odb`
- Input deck: `chaboche_vp_v1_cyclic_eps005_50cycles.inp`
- UMAT: `umat/chaboche_vp_v1_working.f`
- Cycles: `50`
- DMAX: `0.02`
- INC limit: `6000`

## Final Cycle-50 Values

| Quantity | Value |
|---|---:|
| STATEV1 | 0.356620669365 |
| S11 (MPa) | 374.653869629 |
| RIGHT_FACE average U1 | 0 |
| RIGHT_FACE summed RF1 | 1498.61547852 |
| Final Delta STATEV1 | 0.00713682174683 |
| Final Delta S11 | 40.8583984375 |

## Output Files

- Summary CSV: `chaboche_vp_v1_cyclic_eps005_50cycles_summary.csv`
- Cycle history CSV: `chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv`

This no-skip 50-cycle reference is intended for Stage 6B validation of a predicted jump from cycle 10 to cycle 49 followed by one computed continuation cycle.
