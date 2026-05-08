# Thesis Section Build Report

Output folder: `D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat\thesis_cycle_jump_section`

## Copied files

- `tables\chaboche_vp_v1_amplitude_sweep_summary.csv`
- `tables\chaboche_vp_v1_cyclic_eps005_10cycles_summary.csv`
- `tables\chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv`
- `tables\chaboche_cycle_jump_predictions.csv`
- `tables\chaboche_cycle_jump_curve_1_to_1000.csv`
- `tables\chaboche_vp_v1_cyclic_eps005_20cycles_summary.csv`
- `tables\chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv`
- `figures\source_chaboche_vp_v1_amplitude_sweep_stress_strain.svg`
- `figures\source_chaboche_vp_v1_cyclic_eps005_10cycles_selected_loops.svg`
- `figures\source_chaboche_eps005_10cycles_delta_sdv1_per_cycle.svg`
- `figures\source_chaboche_cycle_jump_sdv1_prediction.svg`
- `figures\source_chaboche_cycle_jump_vs_explicit_20cycles.svg`

## Generated figures

- `figures/fig00_geometry_material_model.svg`
- `figures/fig00_geometry_material_model.png`
- `figures/fig01_amplitude_sweep_stress_strain.svg`
- `figures/fig01_amplitude_sweep_stress_strain.png`
- `figures/fig02_10cycle_selected_hysteresis_loops.svg`
- `figures/fig02_10cycle_selected_hysteresis_loops.png`
- `figures/fig03_delta_sdv1_per_cycle.svg`
- `figures/fig03_delta_sdv1_per_cycle.png`
- `figures/fig04_cycle_jump_sdv1_prediction.svg`
- `figures/fig04_cycle_jump_sdv1_prediction.png`
- `figures/fig05_cycle_jump_vs_explicit_20cycles.svg`
- `figures/fig05_cycle_jump_vs_explicit_20cycles.png`

Additional model figure:

- `figures/fig00_geometry_material_model.svg/png` shows the single C3D8 block geometry, displacement boundary conditions, and Chaboche-v1 material/state-variable workflow.
- `scripts/make_geometry_material_model_figure.py` regenerates the geometry/material-model figure.
- `figures/fig00b_actual_abaqus_geometry.svg/png` is reconstructed directly from the Abaqus input deck node coordinates and C3D8 element connectivity.
- `scripts/make_actual_abaqus_geometry_figure.py` regenerates the actual Abaqus geometry figure from `chaboche_vp_v1_cyclic_eps005_20cycles.inp`.

## Generated tables

- `tables/table01_amplitude_sweep_summary.csv`
- `tables/table02_cycle_jump_validation_summary.csv`

## LaTeX files

- `latex/cycle_jump_chaboche_section.tex`
- `latex/cycle_jump_chaboche_figures_only.tex`

## Missing source files

- None

## PNG conversion

- PNG generation succeeded: yes

## Final validation result

- Predicted SDV1 at cycle 20: `0.1421214351`
- Explicit SDV1 at cycle 20: `0.1420256943`
- Relative error: `0.0674%`

## Material-model scope

The Chaboche unified viscoplastic UMAT has been successfully implemented and validated at the computational workflow level. It reproduces nonzero stress, reaction force, viscoplastic strain accumulation, cyclic hysteresis, and a stable per-cycle internal-variable increment suitable for cycle-jump prediction. The current Chaboche-v1 parameter set is a demonstration/validation set, not yet a fully calibrated 316 stainless steel material model.

## Standalone PDF Compilation

- Wrapper file: `cycle_jump_chaboche_standalone.tex`
- PDF file: `cycle_jump_chaboche_standalone.pdf`
- Compile command: `latexmk -pdf -interaction=nonstopmode -halt-on-error .\cycle_jump_chaboche_standalone.tex`
- Compile status: succeeded
- PDF pages after adding actual Abaqus geometry figure: 6
- PDF size after adding actual Abaqus geometry figure: 964447 bytes
- Note: MiKTeX printed a maintenance warning that user/administrator updates are out-of-sync, but the PDF was generated successfully.

## Level-2 Cycle-Jump Preparation Integration

**Integration Date:** May 8, 2026

The Level-2 preparation subsection was added to the standalone thesis package:

- New LaTeX file: `latex/chaboche_level2_cycle_jump_preparation_section.tex` (includable section format)
- Original Level-2 document: `../CHABOCHE_V1_LEVEL2_CYCLE_JUMP_PREPARATION_SUMMARY.md`
- Standalone wrapper updated: `cycle_jump_chaboche_standalone.tex` now includes both Level-1 scalar SDV1 section and Level-2 full-STATEV preparation section

**Content added:**
- STATEV inventory table (15 state variables with symbols, meanings, and categories)
- Full-state cycle-history extraction findings and stability classification
- Vector-valued STATEV cycle-jump control analysis (original DeltaN=2, target cycle 12)
- Exact-output diagnostic branch findings (increment-schedule sensitivity, 5.12% cycle-20 difference)
- Decision rationale for deferring STATEV injection to Level-3
- Method level distinctions (Level 1: postprocessing only, Level 2: preparation diagnostics, Level 3: full integration)

**Updated PDF:**
- New page count: 8 pages (previously 6)
- New size: 1070847 bytes
- Compilation status: successful with booktabs package support

**Thesis narrative now covers:**
1. Validated scalar SDV1 cycle-jump demonstration (Level 1)
2. Full-state preparation diagnostics identifying robustness requirements (Level 2)
3. Clear identification of why Level-3 injection is deferred pending UMAT robustness improvements

