# Chaboche-v1 Cyclic 1-Cycle Report

Working directory: `D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat`

## Baseline Preservation

- Saved cyclic input deck: `chaboche_vp_v1_cyclic_1cycle_working.inp`
- Saved cyclic UMAT baseline: `umat\chaboche_vp_v1_cyclic_working.f`

## Analysis Status

- Compiler/toolchain status: Visual Studio 2022 Build Tools and Intel oneAPI initialized successfully.
- Datacheck: successful.
- Full cyclic analysis: successful.
- Number of increments: 57.
- Cutbacks: 0.
- Warnings: 0.
- Errors: 0.

## Generated Outputs

- CSV summary: `chaboche_vp_v1_cyclic_1cycle_summary.csv`
- Plot: `chaboche_vp_v1_cyclic_stress_strain.svg`
- Plot: `chaboche_vp_v1_cyclic_force_displacement.svg`
- Plot: `chaboche_vp_v1_cyclic_sdv1_time.svg`
- Plot: `chaboche_vp_v1_cyclic_sdv1_strain.svg`

## CSV Summary Values

- Max U1: `0.49948436 mm`
- Min U1: `-0.49948436 mm`
- Max RF1: `30816.94140625 N`
- Min RF1: `-43856.43359375 N`
- Max S11: `7704.2353515625 MPa`
- Min S11: `-10964.1083984375 MPa`
- Final SDV1: `0.047275204211473465`
- Max SDV1: `0.047275204211473465`

## Interpretation

The Chaboche-v1 UMAT now produces nonzero stress, nonzero reaction force, and accumulated viscoplastic strain during cyclic loading. This confirms that the Abaqus input deck, UMAT interface, compiler toolchain, and field/state-variable output pipeline are working.
