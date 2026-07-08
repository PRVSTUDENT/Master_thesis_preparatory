# Chaboche-v1 Full STATEV Cycle-History Report

This report extracts cycle-end averages of all 15 solution-dependent state variables from the validated 20-cycle Abaqus ODB. It prepares the transition from scalar SDV1 cycle jumping to vector-valued STATEV cycle-jump analysis.

## Input

- ODB: `chaboche_vp_v1_cyclic_eps005_20cycles.odb`
- Cycles extracted: `1-20`
- Cycle-end target times: `1, 2, ..., 20`
- Field outputs extracted: `SDV1` through `SDV15`
- No UMAT files were modified.
- No Abaqus input files were modified.
- Abaqus was not rerun; only the existing ODB was postprocessed.

## Output Files

- `chaboche_v1_full_statev_cycle_history.csv`
- `chaboche_v1_full_statev_cycle_stability.csv`

## Final Cycle-End State

- `STATEV(1)` `p`: `0.142025694251`
- `STATEV(2)` `X11`: `-85.8880233765`
- `STATEV(3)` `X22`: `42.9440116882`
- `STATEV(4)` `X33`: `42.9440116882`
- `STATEV(5)` `X12`: `1.10302119978e-15`
- `STATEV(6)` `X13`: `2.8931807587e-15`
- `STATEV(7)` `X23`: `-2.30637507344e-15`
- `STATEV(8)` `Evp11`: `-0.0017925434513`
- `STATEV(9)` `Evp22`: `0.000896271725651`
- `STATEV(10)` `Evp33`: `0.000896271725651`
- `STATEV(11)` `Evp12`: `-2.57704357138e-19`
- `STATEV(12)` `Evp13`: `-2.66356443395e-19`
- `STATEV(13)` `Evp23`: `-1.20477652606e-19`
- `STATEV(14)` `RISO`: `1.41522598267`
- `STATEV(15)` `DP`: `0`

## Stability Classification

| STATEV | Symbol | Mean Delta cycles 2-10 | Relative range | Classification |
| ---: | --- | ---: | ---: | --- |
| 1 | `p` | `0.00718546519056` | `0.00142903719858` | stable extrapolation candidate |
| 2 | `X11` | `0.189079284668` | `8.53209861599` | needs caution |
| 3 | `X22` | `-0.094539642334` | `8.53209861599` | needs caution |
| 4 | `X33` | `-0.094539642334` | `8.53209861599` | needs caution |
| 5 | `X12` | `1.85613432165e-16` | `` | small/nearly zero component |
| 6 | `X13` | `2.57878636691e-17` | `` | small/nearly zero component |
| 7 | `X23` | `2.04609238299e-17` | `` | small/nearly zero component |
| 8 | `Evp11` | `-1.53241368632e-06` | `10.4355026589` | needs caution |
| 9 | `Evp22` | `7.66206843158e-07` | `10.4355026589` | needs caution |
| 10 | `Evp33` | `7.66206843158e-07` | `10.4355026589` | needs caution |
| 11 | `Evp12` | `-3.20502158587e-20` | `` | small/nearly zero component |
| 12 | `Evp13` | `-1.88107538284e-20` | `` | small/nearly zero component |
| 13 | `Evp23` | `-1.07239781598e-21` | `` | small/nearly zero component |
| 14 | `RISO` | `0.0717185309364` | `0.00359717077833` | diagnostic/recomputable |
| 15 | `DP` | `0` | `` | diagnostic/recomputable |

## Stable Extrapolation Candidates

- `STATEV(1)` `p`: Accumulated viscoplastic strain

## Small / Nearly Zero Components

- `STATEV(5)` `X12`: Backstress tensor component
- `STATEV(6)` `X13`: Backstress tensor component
- `STATEV(7)` `X23`: Backstress tensor component
- `STATEV(11)` `Evp12`: Viscoplastic strain tensor component
- `STATEV(12)` `Evp13`: Viscoplastic strain tensor component
- `STATEV(13)` `Evp23`: Viscoplastic strain tensor component

## Diagnostic / Recomputable

- `STATEV(14)` `RISO`: Current isotropic hardening stress
- `STATEV(15)` `DP`: Last viscoplastic multiplier increment

## Needs Caution

- `STATEV(2)` `X11`: Backstress tensor component
- `STATEV(3)` `X22`: Backstress tensor component
- `STATEV(4)` `X33`: Backstress tensor component
- `STATEV(8)` `Evp11`: Viscoplastic strain tensor component
- `STATEV(9)` `Evp22`: Viscoplastic strain tensor component
- `STATEV(10)` `Evp33`: Viscoplastic strain tensor component

## Implication for Level-2 Nesnas-Saanouni Cycle Jump

The scalar SDV1 jump has already been validated at postprocessing level. This full STATEV history shows which components can be considered for a vector-valued cycle-jump predictor before any Abaqus restart or injected-state continuation is attempted.

For Level-2 preparation, the independent material state should focus on `STATEV(1-13)`: accumulated viscoplastic strain, backstress tensor components, and viscoplastic strain tensor components. `STATEV(14)` is recomputable from `STATEV(1)` and material constants in this UMAT, while `STATEV(15)` is a last-increment diagnostic.

The next safe step is a vector-valued postprocessing analyzer that extrapolates the stable/nonzero components of `STATEV(1-13)` and computes a conservative jump size from the most restrictive state component.
