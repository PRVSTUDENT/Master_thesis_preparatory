# Chaboche-v1 Full STATEV Cycle-History Report (Exact-Output)

This report extracts cycle-end averages of all 15 solution-dependent state variables from the exact-output Abaqus ODB. It is an exact-output counterpart to the original nearest-frame extractor, producing a separate set of outputs for comparison.

## Input

- ODB: `chaboche_vp_v1_cyclic_eps005_20cycles_exact.odb`
- Cycles extracted: `1-20`
- Cycle-end target times: `1, 2, ..., 20`
- Field outputs extracted: `SDV1` through `SDV15`
- No UMAT files were modified.
- No Abaqus input files were modified.
- Abaqus was not rerun by this script; only the existing exact-output ODB was postprocessed.
- STATEV injection was not attempted.

## Output Files

- `chaboche_v1_full_statev_cycle_history_exact.csv`
- `chaboche_v1_full_statev_cycle_stability_exact.csv`
- `CHABOCHE_V1_FULL_STATEV_CYCLE_HISTORY_EXACT_REPORT.md`

## Final Cycle-End State

- `STATEV(1)` `p`: `0.134750679135`
- `STATEV(2)` `X11`: `-84.0683364868`
- `STATEV(3)` `X22`: `42.0341682434`
- `STATEV(4)` `X33`: `42.0341682434`
- `STATEV(5)` `X12`: `2.59622486266e-15`
- `STATEV(6)` `X13`: `2.32337086232e-15`
- `STATEV(7)` `X23`: `-1.46446134806e-15`
- `STATEV(8)` `Evp11`: `-0.00169579673093`
- `STATEV(9)` `Evp22`: `0.000847898365464`
- `STATEV(10)` `Evp33`: `0.000847898365464`
- `STATEV(11)` `Evp12`: `3.87074149631e-19`
- `STATEV(12)` `Evp13`: `4.89405238359e-20`
- `STATEV(13)` `Evp23`: `-6.3408275474e-20`
- `STATEV(14)` `RISO`: `1.3429775238`
- `STATEV(15)` `DP`: `0`

## Exact-Phase Check

- Maximum absolute cycle-end time_error: `0`
- All time_error values approximately zero: `yes`
- Previous nearest-frame max absolute time_error: `0.00974273681641`

- Result: max absolute time_error is smaller than or equal to the previous nearest-frame max time error.

## Stability Classification

| STATEV | Symbol | Mean Delta cycles 2-10 | Relative range | Classification |
| ---: | --- | ---: | ---: | --- |
| 1 | `p` | `0.00680734574174` | `0.0119928198635` | stable extrapolation candidate |
| 2 | `X11` | `0.391053941515` | `9.28558483956` | needs caution |
| 3 | `X22` | `-0.195526970757` | `9.28558483956` | needs caution |
| 4 | `X33` | `-0.195526970757` | `9.28558483956` | needs caution |
| 5 | `X12` | `-1.52442305676e-16` | `` | small/nearly zero component |
| 6 | `X13` | `-6.12567277299e-17` | `` | small/nearly zero component |
| 7 | `X23` | `-4.63150082701e-17` | `` | small/nearly zero component |
| 8 | `Evp11` | `9.22874702762e-06` | `8.65716520269` | needs caution |
| 9 | `Evp22` | `-4.61437351381e-06` | `8.65716520269` | needs caution |
| 10 | `Evp33` | `-4.61437351381e-06` | `8.65716520269` | needs caution |
| 11 | `Evp12` | `3.1562331241e-20` | `` | small/nearly zero component |
| 12 | `Evp13` | `-1.27859488774e-21` | `` | small/nearly zero component |
| 13 | `Evp23` | `9.04735100257e-22` | `` | small/nearly zero component |
| 14 | `RISO` | `0.0679502723118` | `0.0147264877605` | diagnostic/recomputable |
| 15 | `DP` | `0` | `` | diagnostic/recomputable |

## Notes

- Abaqus was not rerun by this script.
- UMAT was not modified.
- Input files were not modified.
- STATEV injection was not attempted.
