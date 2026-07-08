# Chaboche-v1 STATEV Inventory Report

This report inventories the solution-dependent state variables used by the active Chaboche-v1 UMAT. It is a preparation step for a future Level-2 restart/state-variable injection workflow.

## Source Files

- Active UMAT inspected: `umat\chaboche_vp_v1_working.f`
- Representative input deck checked for DEPVAR count: `chaboche_vp_v1_cyclic_eps005_20cycles.inp`
- DEPVAR count in input deck: `15`

No UMAT files were modified, no Abaqus input files were modified, and Abaqus was not rerun.

## STATEV Layout

| STATEV index | Symbol/name | Inferred meaning | Access | Cycle-jump candidate | Classification |
| ---: | --- | --- | --- | --- | --- |
| 1 | `p` | Accumulated viscoplastic strain | read/write | yes | required for restart/injection |
| 2 | `X11` | Backstress tensor components | read/write | yes | required for restart/injection |
| 3 | `X22` | Backstress tensor components | read/write | yes | required for restart/injection |
| 4 | `X33` | Backstress tensor components | read/write | yes | required for restart/injection |
| 5 | `X12` | Backstress tensor components | read/write | yes | required for restart/injection |
| 6 | `X13` | Backstress tensor components | read/write | yes | required for restart/injection |
| 7 | `X23` | Backstress tensor components | read/write | yes | required for restart/injection |
| 8 | `Evp11` | Viscoplastic strain tensor components | read/write | yes | required for restart/injection |
| 9 | `Evp22` | Viscoplastic strain tensor components | read/write | yes | required for restart/injection |
| 10 | `Evp33` | Viscoplastic strain tensor components | read/write | yes | required for restart/injection |
| 11 | `Evp12` | Viscoplastic strain tensor components | read/write | yes | required for restart/injection |
| 12 | `Evp13` | Viscoplastic strain tensor components | read/write | yes | required for restart/injection |
| 13 | `Evp23` | Viscoplastic strain tensor components | read/write | yes | required for restart/injection |
| 14 | `RISO` | Current isotropic hardening stress | write | conditional/recomputable | diagnostic or recomputable |
| 15 | `DP` | Last viscoplastic multiplier increment | write | no | diagnostic only |

## Required for Restart/Injection

- `STATEV(1)` `p`: Accumulated viscoplastic strain
- `STATEV(2)` `X11`: Backstress tensor components
- `STATEV(3)` `X22`: Backstress tensor components
- `STATEV(4)` `X33`: Backstress tensor components
- `STATEV(5)` `X12`: Backstress tensor components
- `STATEV(6)` `X13`: Backstress tensor components
- `STATEV(7)` `X23`: Backstress tensor components
- `STATEV(8)` `Evp11`: Viscoplastic strain tensor components
- `STATEV(9)` `Evp22`: Viscoplastic strain tensor components
- `STATEV(10)` `Evp33`: Viscoplastic strain tensor components
- `STATEV(11)` `Evp12`: Viscoplastic strain tensor components
- `STATEV(12)` `Evp13`: Viscoplastic strain tensor components
- `STATEV(13)` `Evp23`: Viscoplastic strain tensor components

## Diagnostic or Recomputable

- `STATEV(14)` `RISO`: Current isotropic hardening stress
- `STATEV(15)` `DP`: Last viscoplastic multiplier increment

## Unclear / Needs Manual Confirmation

- None identified from the active UMAT source.

## Implication for Nesnas-Saanouni Cycle Jump

The current Level-1 predictor jumps only `STATEV(1)`, the accumulated viscoplastic strain. That is sufficient for a postprocessing validation of cycle-space extrapolation, but it is not sufficient for a restart or injected-state Abaqus continuation.

For a Level-2 restart/state-variable injection test, the independent UMAT memory should include at least:

- `STATEV(1)`: accumulated viscoplastic strain `p`
- `STATEV(2-7)`: backstress tensor components
- `STATEV(8-13)`: viscoplastic strain tensor components

`STATEV(14)` can be recomputed from `STATEV(1)` and the material constants in this UMAT, while `STATEV(15)` is a last-increment diagnostic. A conservative injection workflow may still initialize all 15 values for output consistency, but the physically independent state is concentrated in `STATEV(1-13)`.

The next implementation stage should therefore extrapolate a consistent vector of state variables, not only SDV1. The smallest safe adaptive jump over the selected state components should control the full material-state jump.

## Generated File

- `chaboche_v1_statev_inventory.csv`
