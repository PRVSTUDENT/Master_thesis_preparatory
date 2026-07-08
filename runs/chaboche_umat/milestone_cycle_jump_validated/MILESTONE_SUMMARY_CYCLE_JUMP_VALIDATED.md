# Milestone Summary: Cycle-Jump Validated

Milestone folder:

`D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat\milestone_cycle_jump_validated`

## Model

- Model: Chaboche-v1 UMAT with Perzyna-type viscoplastic update
- UMAT: `umat\chaboche_vp_v1_working.f`
- Selected validation amplitude: `+/-0.5%` engineering strain
- Displacement amplitude: `U_amp = +/-0.05 mm`
- Gauge length: `L0 = 10 mm`

## Toolchain

- Abaqus version: Abaqus 2024
- Compiler/toolchain status: working with Visual Studio 2022 Build Tools and Intel oneAPI Fortran `ifx`
- The UMAT compiled, linked, and ran successfully in Abaqus/Standard.

## 10-Cycle Baseline

Job:

`chaboche_vp_v1_cyclic_eps005_10cycles`

Status:

- Datacheck: passed
- Full analysis: completed
- Increments: 507
- Cutbacks: 0
- Warnings: 0
- Errors: 0

Key diagnostic:

- Mean `Delta_SDV1` from cycles 2-10: `0.007185465191`
- Relative range of `Delta_SDV1` from cycles 2-10: about `0.1429%`
- Final stress amplitude at cycle 10: `671.8389282 MPa`
- Final mean stress at cycle 10: about `-0.015 MPa`

Interpretation:

Total `SDV1` is accumulated viscoplastic strain and should increase monotonically. The stable quantity for cycle-jump is the per-cycle increment `Delta_SDV1`.

## Cycle-Jump Prediction

Reference window:

`cycles 2-10`

Prediction formula:

`SDV1_pred(N) = SDV1_cycle10 + (N - 10) * mean_Delta_SDV1_2to10`

Cycle-20 prediction:

- Predicted `SDV1` at cycle 20: `0.1421214351`

## 20-Cycle Explicit Validation

Job:

`chaboche_vp_v1_cyclic_eps005_20cycles`

Status:

- Datacheck: passed
- Full analysis: completed
- Increments: 1007
- Cutbacks: 0
- Warnings: 0
- Errors: 0

Validation result:

- Predicted `SDV1` at cycle 20: `0.1421214351`
- Explicit `SDV1` at cycle 20: `0.1420256943`
- Absolute error: `-9.574084894e-05`
- Relative error: `0.0674%`

## Conclusion

The cycle-jump predictor is validated for this simplified Chaboche-v1 UMAT test case at `+/-0.5%` strain amplitude. The explicit 10-cycle Abaqus simulation identified a stable per-cycle accumulated viscoplastic strain increment, and the postprocessing cycle-jump extrapolation predicted the explicit 20-cycle result with only `0.0674%` relative error.

This is a validated cycle-jump workflow demonstration, not yet a fully calibrated fatigue-life model.

## Included File Groups

UMAT and inputs:

- `umat\chaboche_vp_v1_working.f`
- `chaboche_vp_v1_working.inp`
- `chaboche_vp_v1_cyclic_eps005_10cycles.inp`
- `chaboche_vp_v1_cyclic_eps005_20cycles.inp`

Main CSV files:

- `chaboche_vp_v1_cyclic_eps005_10cycles_summary.csv`
- `chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv`
- `chaboche_vp_v1_cyclic_eps005_20cycles_summary.csv`
- `chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv`
- `chaboche_cycle_jump_predictions.csv`
- `chaboche_cycle_jump_curve_1_to_1000.csv`

Main plots:

- `chaboche_vp_v1_amplitude_sweep_stress_strain.svg`
- `chaboche_vp_v1_cyclic_eps005_10cycles_selected_loops.svg`
- `chaboche_eps005_10cycles_delta_sdv1_per_cycle.svg`
- `chaboche_cycle_jump_sdv1_prediction.svg`
- `chaboche_cycle_jump_vs_explicit_20cycles.svg`

Reports:

- `CHABOCHE_DEBUG_REPORT.md`
- `CHABOCHE_AMPLITUDE_SWEEP_REPORT.md`
- `CHABOCHE_EPS005_10CYCLE_DIAGNOSTICS_REPORT.md`
- `CHABOCHE_CYCLE_JUMP_PREDICTION_REPORT.md`
- `CHABOCHE_CYCLE_JUMP_20CYCLE_VALIDATION_REPORT.md`
