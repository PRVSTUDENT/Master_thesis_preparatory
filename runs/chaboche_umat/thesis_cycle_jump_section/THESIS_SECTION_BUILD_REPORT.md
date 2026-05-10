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

## Stage 3 Increment-Schedule Sensitivity Integration

**Integration Date:** May 9, 2026

The Stage 3 increment-schedule sensitivity subsection was added to the standalone thesis package immediately after the Level-2 preparation section.

Added and copied into the thesis package:

- `latex/chaboche_increment_sensitivity_section.tex`
- `tables/chaboche_increment_sensitivity_summary.csv`
- `tables/chaboche_eps005_20cycles_dt_original_output_statev_history.csv`
- `tables/chaboche_eps005_20cycles_dtmax_0p01_statev_history.csv`
- `tables/chaboche_eps005_20cycles_dtmax_0p005_inc6000_statev_history.csv`
- `figures/chaboche_increment_sensitivity_statev1_vs_dmax.svg`
- `figures/chaboche_increment_sensitivity_statev1_vs_cycle.svg`

**Content added:**
- Cycle-20 summary table for the three controlled DMAX cases
- LaTeX/PGFPlots rendering of STATEV1 versus DMAX
- LaTeX/PGFPlots rendering of STATEV1 versus cycle for the three completed cases
- Thesis conclusion that increment-size sensitivity is confirmed and Level-3 injection remains deferred

**Updated PDF:**
- New page count: 10 pages
- New size: 1084855 bytes
- Compilation status: successful

**Thesis narrative now covers:**
1. Validated scalar SDV1 cycle-jump demonstration (Level 1)
2. Full-state preparation diagnostics identifying robustness requirements (Level 2)
3. Increment-schedule sensitivity evidence showing the UMAT remains increment-size sensitive (Stage 3)

## Predicted-State FE Cycle-Jump Continuation Integration

**Integration Date:** May 9, 2026

The final predicted-state FE cycle-jump subsection was added to the standalone thesis package after the Stage 3 increment-schedule sensitivity section.

Added and copied into the thesis package:

- `latex/chaboche_predicted_fe_cycle_jump_section.tex`
- `tables/table_predicted_fe_cycle_jump_summary.csv`
- `tables/table_multitarget_jump_scan.csv`

Updated:

- `cycle_jump_chaboche_standalone.tex`
- `cycle_jump_chaboche_standalone.pdf`

**New section name:**

- `Predicted-State FE Cycle-Jump Continuation`

**Content added:**

- Method paragraph covering cycle-space prediction, `SDVINI` STATEV injection, `SIGINI` residual-stress injection, one computed continuation cycle, and comparison against full no-skip Abaqus references.
- Stage 5B clean predicted FE cycle-jump result:
  - Route: cycle 10 -> predicted cycle 19 -> cycle 20
  - Skipped intermediate FE cycles: `8`
  - STATEV1 relative error: `0.049427%`
  - S11 relative error: `0.127013%`
  - Decision: clean success
- Stage 6C multi-target prediction scan:
  - Target 29 -> 30: acceptable exploratory candidate
  - Target 39 -> 40: not headline candidate
  - Target 49 -> 50: not headline candidate
- Stage 6D larger predicted FE cycle-jump result:
  - Route: cycle 10 -> predicted cycle 29 -> cycle 30
  - Skipped intermediate FE cycles: `18`
  - Computed route: `11` cycles instead of `30`
  - Route reduction: `63.33%`
  - STATEV1 relative error: `0.0458269%`
  - S11 relative error: `2.34366%`
  - Outcome: acceptable exploratory success

**Limitation stated in the thesis text:**

The remaining limitation is not Abaqus initialization, `SDVINI`, `SIGINI`, or UMAT continuation. These mechanisms were verified. The remaining limitation is the accuracy of first-order stress/backstress extrapolation for larger cycle jumps.

**Updated PDF:**

- New page count: 11 pages
- New size: 1091019 bytes
- Compilation status: successful
- Compile command: `latexmk -pdf -interaction=nonstopmode -halt-on-error .\cycle_jump_chaboche_standalone.tex`
- Note: MiKTeX again printed user/administrator update warnings, but the PDF was generated successfully.

**Thesis narrative now covers:**

1. Validated scalar SDV1 cycle-jump demonstration (Level 1)
2. Full-state preparation diagnostics identifying robustness requirements (Level 2)
3. Increment-schedule sensitivity evidence for the Chaboche-v1 UMAT (Stage 3)
4. Predicted-state FE cycle-jump continuation through `SDVINI`/`SIGINI`, including clean Stage 5B and larger exploratory Stage 6D validation

## Stage 7B Adaptive Jump-Size Selection Integration

**Integration Date:** May 10, 2026

A short subsection was added after the predicted FE cycle-jump continuation results:

- `Adaptive Jump-Size Selection Inspired by Nesnas--Saanouni`

Updated:

- `latex/chaboche_predicted_fe_cycle_jump_section.tex`
- `cycle_jump_chaboche_standalone.pdf`
- `THESIS_SECTION_BUILD_REPORT.md`

**Content added:**

- The paper damage variable `D` is not used directly because the present model is a Chaboche viscoplastic UMAT without damage.
- `D` is replaced by a generalized Chaboche cycle-control quantity `Y_i`.
- The paper-style jump budget is written as an admissible state change `A_i = tau_i S_i`.
- The per-variable jump estimate is documented as `DeltaN_i = floor(eta A_i / (abs(mean DeltaY_i) + eps))`.
- Accumulated viscoplastic strain `p` is treated as an accuracy monitor rather than the global restart limiter.
- Backstress, viscoplastic strain tensor, and residual stress consistency control the grouped restart recommendation.
- The grouped Stage 7B recommendation `DeltaN_restart = 17` is stated as close to the validated Stage 6D exploratory FE jump with `DeltaN = 19`.

**Updated PDF:**

- New page count: 12 pages
- New size: 1105468 bytes
- Compilation status: successful
- Compile command: `latexmk -pdf -interaction=nonstopmode -halt-on-error .\cycle_jump_chaboche_standalone.tex`
- Note: MiKTeX printed user/administrator update warnings, but the PDF was generated successfully.

**Thesis narrative now covers:**

1. Validated scalar SDV1 cycle-jump demonstration (Level 1)
2. Full-state preparation diagnostics identifying robustness requirements (Level 2)
3. Increment-schedule sensitivity evidence for the Chaboche-v1 UMAT (Stage 3)
4. Predicted-state FE cycle-jump continuation through `SDVINI`/`SIGINI`, including clean Stage 5B and larger exploratory Stage 6D validation
5. Paper-inspired grouped adaptive `DeltaN` selection with Stage 7B recommendation `DeltaN_restart = 17`

## Stage 7C Adaptive Target Abaqus Validation Integration

**Integration Date:** May 10, 2026

The Stage 7C direct Abaqus validation was added to the adaptive jump-size subsection.

Updated:

- `latex/chaboche_predicted_fe_cycle_jump_section.tex`
- `cycle_jump_chaboche_standalone.pdf`
- `THESIS_SECTION_BUILD_REPORT.md`

**Content added:**

- Stage 7B formula-selected recommendation: `DeltaN_restart = 17`.
- Direct validation route: cycle 10 -> predicted cycle 27 -> cycle 28.
- Skipped intermediate FE cycles: `16`.
- First-frame injection check:
  - STATEV1 absolute error: `1.39693476231e-09`
  - S11 absolute error: `3.39113159953e-06 MPa`
- Final cycle-28 comparison against the interpolated 50-cycle Abaqus reference:
  - STATEV1 relative error: `0.0231584782019%`
  - S11 relative error: `2.36494669088%`
- Stage 7C outcome: `accepted_exploratory_success`.

**Thesis interpretation:**

Stage 7C confirms that the grouped adaptive controller is not only close to the manually validated Stage 6D jump, but also produces an Abaqus-validated formula-selected exploratory cycle jump.

**Updated PDF:**

- New page count: 12 pages
- New size: 1106447 bytes
- Compilation status: successful
- Compile command: `latexmk -pdf -interaction=nonstopmode -halt-on-error .\cycle_jump_chaboche_standalone.tex`
- Note: MiKTeX printed user/administrator update warnings, but the PDF was generated successfully.

