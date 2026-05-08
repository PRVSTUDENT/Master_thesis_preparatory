# Chaboche UMAT Debug Report

Working directory: `D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat`

## Goal

Build up the UMAT in controlled diagnostic steps until the Abaqus output shows nonzero stress, nonzero reaction force, and reasonable state-variable evolution.

Current target:

- `S11` nonzero
- `RF1` nonzero
- `SDV1` physically reasonable

## Diagnostic History

### 1. Hysteresis Extraction Fix

The hysteresis extraction script was patched to use the assembly-level `RIGHT_FACE` node set instead of an instance-level lookup.

Result:

- Assembly node set `RIGHT_FACE` was found with node labels `[2, 3, 6, 7]`.
- Displacement `U1` was extracted correctly.
- `RF1` remained zero.
- Average `S11` remained zero.

Conclusion:

The extraction path was corrected, but the underlying ODB still contained zero stress and therefore zero reaction force.

### 2. Raw ODB Stress and SDV Inspection

The raw ODB fields were inspected at several frames.

Observed:

- `S = [0, 0, 0, 0, 0, 0]` at all integration points.
- `SDV1` evolved from `0` to about `9.9246`.

Conclusion:

The UMAT was being called and `STATEV` was being written, but `STRESS` returned by the UMAT stayed zero.

### 3. Elastic-Only UMAT Smoke Test

The active UMAT was temporarily replaced by a minimal elastic stress update while keeping the same input file, geometry, boundary conditions, compiler setup, and Abaqus workflow.

Result at the final frame:

- `S11 = 10500 MPa` at all 8 integration points.
- `SDV1 = 0.05000000074505806` at all 8 integration points.

Conclusion:

The Abaqus/Fortran plumbing is correct. Abaqus can compile, link, call the UMAT, receive nonzero stress, and output state variables.

## Current Change

The elastic smoke-test UMAT was backed up as:

`umat\chaboche_umat_template_elastic_smoke_backup.f`

The earlier Chaboche UMAT backup remains:

`umat\chaboche_umat_template_chaboche_backup.f`

The active UMAT has now been replaced by a minimal working Chaboche/Perzyna v1 update. This version is meant as a debugging bridge, not as the final implicit thesis-grade material algorithm.

The material viscosity parameter in `chaboche_umat_1cycle.inp` was changed from:

`800.0, 0.001, 5.0`

to:

`800.0, 1000.0, 5.0`

This reduces the explosiveness of the Perzyna overstress term for the first Chaboche smoke test.

## Next Check

Run `chaboche_vp_v1` and inspect the final-frame averages:

- `Avg S11`
- `Min S11`
- `Max S11`
- `Avg SDV1`
- `Max SDV1`
- `Avg SDV15 last dp`

## Chaboche v1 Smoke-Test Result

Job:

`abaqus job=chaboche_vp_v1 input=chaboche_umat_1cycle.inp user=umat\chaboche_umat_template.f interactive`

Result:

- The job compiled, linked, and completed successfully.
- `Avg S11 = 6310.2978515625 MPa`
- `Min S11 = 6310.298 MPa`
- `Max S11 = 6310.298 MPa`
- `Avg SDV1 = 0.01995096355676651`
- `Max SDV1 = 0.01995096355676651`
- `Avg SDV15 last dp = 0.0010000000474974513`
- `RIGHT_FACE U1 = 0.5 mm`
- `RIGHT_FACE RF1 sum = 25241.19140625 N`

Conclusion:

The minimal Chaboche/Perzyna v1 update returns nonzero stress, produces nonzero reaction force, and keeps the accumulated plastic strain in a much more reasonable range for this smoke test.

## Cyclic Chaboche-v1 Baseline

The fully reversed 1-cycle Chaboche-v1 run completed successfully as:

`chaboche_vp_v1_cyclic_1cycle`

Status:

- 57 increments
- 0 cutbacks
- 0 warnings
- 0 errors
- ODB produced

The original displacement amplitude was `Umax = +/-0.5 mm` over `L0 = 10 mm`, i.e. `+/-5%` strain. This proved the pipeline but was too aggressive for first physical validation:

- `Max S11 = 7704.235352 MPa`
- `Min S11 = -10964.1084 MPa`
- `Final SDV1 = 0.04727520421`

Force/stress consistency was confirmed using the 4 mm2 cross-section.

## Strain-Amplitude Sweep

A non-overwriting sweep was run using `umat\chaboche_vp_v1_working.f`:

| eps_amp | U_amp mm | max S11 MPa | min S11 MPa | final SDV1 | status |
|---:|---:|---:|---:|---:|---|
| 0.001 | 0.01 | 209.783432 | -209.783432 | 0 | completed |
| 0.002 | 0.02 | 419.566864 | -419.566864 | 0 | completed |
| 0.005 | 0.05 | 648.2124634 | -674.749939 | 0.005597596522 | completed |
| 0.010 | 0.10 | 727.869751 | -733.9141235 | 0.02290419675 | completed |

Conclusion:

- `+/-0.1%` and `+/-0.2%` validate the small-strain elastic response.
- `+/-0.5%` is the best first cyclic validation amplitude because it activates plasticity at reasonable stress levels.
- `+/-1.0%` gives stronger plastic cycling and can be used later after the first loop is accepted.

Selected baseline:

`chaboche_vp_v1_cyclic_eps005`

## Ten-Cycle eps005 Validation

A 10-cycle validation run was created as:

`chaboche_vp_v1_cyclic_eps005_10cycles`

The first full-analysis attempt hit Abaqus' default 100-increment step cap. The failed logs were preserved as `*_failed_maxinc100.*`, then the new 10-cycle input was updated to `INC=1000`.

Final status:

- Datacheck passed
- Full analysis completed
- 507 increments
- 0 cutbacks
- 0 warnings
- 0 errors

Final summary:

- `Max S11 = 671.8238525 MPa`
- `Min S11 = -674.749939 MPa`
- `Max RF1 = 2687.29541 N`
- `Min RF1 = -2698.999756 N`
- `Final SDV1 = 0.07026678324`

Important interpretation:

`SDV1` is accumulated viscoplastic strain `p`, so total `SDV1` is cumulative and should not decrease. The correct cyclic stability metric is the per-cycle increment `Delta_SDV1`.

## Ten-Cycle Diagnostics

The diagnostics script:

`postprocess_chaboche_10cycle_diagnostics.py`

produced:

- `chaboche_vp_v1_cyclic_eps005_10cycles_diagnostics_full.csv`
- `chaboche_vp_v1_cyclic_eps005_10cycles_quarter_points.csv`
- `chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv`
- `CHABOCHE_EPS005_10CYCLE_DIAGNOSTICS_REPORT.md`

Key diagnostics:

- Total SDV1 monotonic: yes
- Average `Delta_SDV1` over cycles 2-10: `0.007185465191`
- `Delta_SDV1` relative range over cycles 2-10: `0.001429037192` = about `0.1429%`
- Final residual stress at zero strain: `377.0350647 MPa`
- Final stress amplitude: `671.8389282 MPa`
- Final mean stress: `-0.01507568359 MPa`

Conclusion:

The eps005 model is stable in rate form after the first-cycle transient and is suitable as a baseline for a postprocessing-level cycle-jump demonstration.

## Postprocessing Cycle-Jump Predictor

The script:

`cycle_jump_predictor_from_10cycles.py`

used cycles 2-10 as the stabilized reference window and generated:

- `chaboche_cycle_jump_predictions.csv`
- `chaboche_cycle_jump_curve_1_to_1000.csv`
- `chaboche_cycle_jump_sdv1_prediction.svg`
- `chaboche_cycle_jump_delta_sdv1_reference.svg`
- `CHABOCHE_CYCLE_JUMP_PREDICTION_REPORT.md`

Reference statistics:

- Mean `Delta_SDV1 = 0.007185465191`
- Standard deviation `Delta_SDV1 = 3.368213202e-06`
- Relative range `Delta_SDV1 = 0.001429037192`
- Mean stress amplitude `= 671.5717095 MPa`
- Mean mean-stress `= -0.05007595486 MPa`
- Mean residual stress `= 340.8964505 MPa`

Predicted accumulated SDV1:

| cycle | predicted SDV1 |
|---:|---:|
| 20 | 0.1421214351 |
| 50 | 0.3576853909 |
| 100 | 0.7169586504 |
| 200 | 1.435505169 |
| 500 | 3.591144727 |
| 1000 | 7.183877322 |

Important thesis caveat:

The prediction is a postprocessing-level cycle-jump demonstration, not yet a fully calibrated fatigue-life model or an Abaqus restart with injected `STATEV`. The large predicted `SDV1` at 1000 cycles reflects indefinite accumulation in the simplified Chaboche-v1 setup.

## Current Next Step

Validate the cycle-jump prediction with one explicit 20-cycle Abaqus run:

- Job: `chaboche_vp_v1_cyclic_eps005_20cycles`
- Predicted SDV1 at cycle 20: `0.1421214351`
- Goal: compare explicit cycle-20 SDV1 against the postprocessing cycle-jump prediction.

## Explicit 20-Cycle Cycle-Jump Validation

A new 20-cycle input was created:

`chaboche_vp_v1_cyclic_eps005_20cycles.inp`

The input uses the same geometry, material, boundary conditions, output requests, and UMAT as the validated 10-cycle eps005 case, with:

- `RIGHT_FACE, 1, 1, 0.05`
- `*STEP, NAME=CYCLIC_20, NLGEOM=NO, INC=2500`
- total step time `20.0`
- 20 fully reversed cycles

Status:

- Datacheck passed
- Full analysis completed
- 1007 increments
- 0 cutbacks
- 0 warnings
- 0 errors

Postprocessing script:

`postprocess_chaboche_20cycle_validation.py`

Generated:

- `chaboche_vp_v1_cyclic_eps005_20cycles_summary.csv`
- `chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv`
- `chaboche_eps005_20cycles_stress_strain.svg`
- `chaboche_eps005_20cycles_sdv1_time.svg`
- `chaboche_eps005_20cycles_delta_sdv1_per_cycle.svg`
- `chaboche_cycle_jump_vs_explicit_20cycles.svg`
- `CHABOCHE_CYCLE_JUMP_20CYCLE_VALIDATION_REPORT.md`

Cycle-jump validation:

- Predicted SDV1 at cycle 20: `0.1421214351`
- Explicit SDV1 at cycle 20: `0.1420256943`
- Absolute error, actual - predicted: `-9.574084894e-05`
- Relative error: `0.06741093536%`

Cycle-20 final frame:

- `Time_s = 20`
- `U1 = 0`
- `Avg_S11 = 376.4341431 MPa`
- `RF1 = 1505.736572 N`
- `Avg_SDV1 = 0.1420256943`
- `Avg_SDV15 = 0`

Conclusion:

The explicit 20-cycle Abaqus run validates the 10-cycle postprocessing cycle-jump predictor for this simplified Chaboche-v1 case. The error at cycle 20 is well below 1%, and `Delta_SDV1` remains stable over cycles 11-20. This supports using the result as a thesis demonstration of identifying a stabilized per-cycle internal-variable increment from explicit cycles and extrapolating it with a cycle-jump predictor.

## Milestone Freeze: Cycle-Jump Validated

A clean milestone folder was created:

`D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat\milestone_cycle_jump_validated`

This folder contains copied, not moved, milestone artifacts:

- working UMAT and key input decks
- 10-cycle and 20-cycle summary/increment CSV files
- cycle-jump prediction CSV files
- main SVG plots
- main markdown reports
- `MILESTONE_SUMMARY_CYCLE_JUMP_VALIDATED.md`

Milestone conclusion:

The simplified Chaboche-v1 UMAT cycle-jump workflow is validated for the selected `+/-0.5%` strain-amplitude test case. The 10-cycle reference window predicted cycle-20 accumulated viscoplastic strain with `0.0674%` relative error against an explicit 20-cycle Abaqus validation run.

## Thesis Section Package

A thesis/report-ready section package was created:

`D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat\thesis_cycle_jump_section`

Subfolders:

- `figures`
- `tables`
- `latex`
- `scripts`

Build script:

`thesis_cycle_jump_section\scripts\make_thesis_cycle_jump_figures.py`

The script copies source CSV/SVG files, regenerates clean thesis-style figures, converts PNG files using ImageMagick, creates summary tables, and writes LaTeX section files.

Generated figure order:

1. `fig01_amplitude_sweep_stress_strain.svg/png`
2. `fig02_10cycle_selected_hysteresis_loops.svg/png`
3. `fig03_delta_sdv1_per_cycle.svg/png`
4. `fig04_cycle_jump_sdv1_prediction.svg/png`
5. `fig05_cycle_jump_vs_explicit_20cycles.svg/png`

Generated LaTeX files:

- `latex\cycle_jump_chaboche_section.tex`
- `latex\cycle_jump_chaboche_figures_only.tex`

Generated tables:

- `tables\table01_amplitude_sweep_summary.csv`
- `tables\table02_cycle_jump_validation_summary.csv`

Build report:

`thesis_cycle_jump_section\THESIS_SECTION_BUILD_REPORT.md`

Status:

- Missing source files: none
- PNG generation: succeeded
- Final validation result recorded: relative error `0.0674%`

Standalone PDF compilation:

- Wrapper file: `thesis_cycle_jump_section\cycle_jump_chaboche_standalone.tex`
- PDF file: `thesis_cycle_jump_section\cycle_jump_chaboche_standalone.pdf`
- Compile command: `latexmk -pdf -interaction=nonstopmode -halt-on-error .\cycle_jump_chaboche_standalone.tex`
- Compile status: succeeded
- PDF pages: 5
- MiKTeX note: user/administrator updates are out-of-sync, but the PDF was generated successfully.

Geometry/material-model figure update:

- Added `thesis_cycle_jump_section\figures\fig00_geometry_material_model.svg`
- Added `thesis_cycle_jump_section\figures\fig00_geometry_material_model.png`
- Added generator script `thesis_cycle_jump_section\scripts\make_geometry_material_model_figure.py`
- Inserted the figure into `latex\cycle_jump_chaboche_section.tex` after the Abaqus--UMAT model description.
- Recompiled `cycle_jump_chaboche_standalone.pdf`; updated PDF size is `877036` bytes.

Actual Abaqus geometry extraction update:

- Added `thesis_cycle_jump_section\scripts\make_actual_abaqus_geometry_figure.py`
- Parsed node coordinates and C3D8 element connectivity from `chaboche_vp_v1_cyclic_eps005_20cycles.inp`
- Added `thesis_cycle_jump_section\figures\fig00b_actual_abaqus_geometry.svg`
- Added `thesis_cycle_jump_section\figures\fig00b_actual_abaqus_geometry.png`
- Inserted this extracted-geometry figure into the Abaqus--UMAT model subsection.
- Recompiled `cycle_jump_chaboche_standalone.pdf`; updated PDF has 6 pages and size `964447` bytes.

## Final Scope Statement

Confirmed:

- Chaboche-v1 UMAT compiles and links in Abaqus.
- Abaqus receives nonzero stress from the UMAT.
- Reaction force is nonzero and consistent with stress times area.
- SDV1 accumulated viscoplastic strain evolves correctly.
- Cyclic hysteresis response is produced.
- `+/-0.5%` strain amplitude gives reasonable plastic cycling for the simplified validation case.
- The 10-cycle baseline is stable in `Delta_SDV1` per cycle.
- The cycle-jump prediction is validated against an explicit 20-cycle run with `0.0674%` relative error at cycle 20.

Careful conclusion:

The Chaboche unified viscoplastic UMAT has been successfully implemented and validated at the computational workflow level. It reproduces nonzero stress, reaction force, viscoplastic strain accumulation, cyclic hysteresis, and a stable per-cycle internal-variable increment suitable for cycle-jump prediction. However, the current Chaboche-v1 parameter set should be treated as a demonstration/validation set, not yet as a fully calibrated 316 stainless steel material model.

## Nesnas-Saanouni-Inspired SDV1 Cycle-Jump Analyzer

A postprocessing bridge script was added to connect the validated Chaboche-v1 workflow to the Nesnas-Saanouni two-time-scale cycle-jump concept:

- Script: `nesnas_saanouni_sdv1_cycle_jump_analyzer.py`
- Input: `chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv`
- Scalar cycle-evolution marker: `SDV1 = accumulated viscoplastic strain p`
- Stabilized reference window: cycles `2-10`
- Method level: postprocessing only; no Abaqus rerun, UMAT change, restart, or STATEV injection

Generated CSV files:

- `nesnas_sdv1_cycle_derivatives.csv`
- `nesnas_sdv1_first_second_order_predictions.csv`
- `nesnas_sdv1_adaptive_jump_recommendations.csv`
- `nesnas_sdv1_adaptive_jump_validation.csv`

Generated SVG files:

- `nesnas_sdv1_cycle_derivatives.svg`
- `nesnas_sdv1_first_second_order_prediction.svg`
- `nesnas_sdv1_adaptive_jump_size.svg`

Generated report:

- `NESNAS_SDV1_CYCLE_JUMP_ANALYZER_REPORT.md`

Reference statistics:

- Mean `dSDV1/dN` over cycles `2-10`: `0.00718546519056`
- Standard deviation of `dSDV1/dN` over cycles `2-10`: `3.36821320212e-06`
- Relative range of `dSDV1/dN` over cycles `2-10`: `0.142903719212%`
- Mean `d2SDV1/dN2` over stabilized curvature points: `3.1146925e-07`

Adaptive jump settings used for the demonstration:

- `eta = 1.0`
- `JUMPMIN = 5`
- `JUMPMAX = 60`
- Curvature check tolerance = `0.01`
- Recommended `Delta N` from cycle 10 = `9`

Cycle-20 validation from this Nesnas-style analyzer:

- First-order predicted `SDV1` at cycle 20 = `0.142121435146`
- Second-order predicted `SDV1` at cycle 20 = `0.142137008608`
- Explicit Abaqus `SDV1` at cycle 20 = `0.1420256943`
- First-order relative error = `0.0674109329494%`
- Second-order relative error = `0.0783761759477%`

Adaptive jump validation:

- Jump base cycle = `10`
- Recommended `Delta N` = `9`
- Adaptive target cycle = `19`
- First-order predicted `SDV1` at cycle 19 = `0.134935969955`
- Second-order predicted `SDV1` at cycle 19 = `0.13494858446`
- Explicit Abaqus `SDV1` at cycle 19 = `0.1348549426`
- First-order relative error = `0.0600848240619%`
- Second-order relative error = `0.0694389525661%`

Interpretation:

The new analyzer formalizes the current cycle-jump demonstration as a first-order cycle-space extrapolation with optional second-order curvature diagnostics and an adaptive jump-size estimate. This matches the first practical layer of the Nesnas-Saanouni idea: observe internal-variable evolution from computed cycles, estimate cycle derivatives, and predict skipped-cycle evolution. It is still not a full Nesnas-Saanouni FE acceleration method because the complete UMAT state vector is not yet extrapolated and injected back into Abaqus.

## Chaboche-v1 STATEV Inventory for Level-2 Preparation

A STATEV inventory was created to prepare the transition from Level-1 postprocessing prediction toward Level-2 restart/state-variable injection.

Files created:

- `create_chaboche_v1_statev_inventory.py`
- `chaboche_v1_statev_inventory.csv`
- `CHABOCHE_V1_STATEV_INVENTORY_REPORT.md`

Source inspected:

- Active UMAT: `umat\chaboche_vp_v1_working.f`
- Representative input deck: `chaboche_vp_v1_cyclic_eps005_20cycles.inp`
- Confirmed `*DEPVAR` count: `15`

STATEV layout inferred from the active UMAT:

- `STATEV(1)`: accumulated viscoplastic strain `p`
- `STATEV(2-7)`: backstress tensor components `X11, X22, X33, X12, X13, X23`
- `STATEV(8-13)`: viscoplastic strain tensor components `Evp11, Evp22, Evp33, Evp12, Evp13, Evp23`
- `STATEV(14)`: current isotropic hardening stress `RISO`
- `STATEV(15)`: last viscoplastic multiplier increment `DP`

Classification:

- Required for restart/injection: `STATEV(1-13)`
- Diagnostic or recomputable: `STATEV(14-15)`
- Unclear variables needing manual confirmation: none identified from the active UMAT

Implication:

The current Level-1 cycle-jump predictor uses only `STATEV(1)` / `SDV1`. For a Level-2 Abaqus restart or injected-state continuation, the jump must eventually be extended to a consistent internal state vector including accumulated viscoplastic strain, backstress tensor components, and viscoplastic strain tensor components. `STATEV(14)` can be recomputed from `STATEV(1)` and the material constants in this UMAT, while `STATEV(15)` is a last-increment diagnostic.

## Full STATEV Cycle-History Extraction from 20-Cycle ODB

A full state-vector cycle-history extractor was created and run on the validated 20-cycle ODB. This is the next Level-2 preparation step before any vector-valued cycle-jump predictor or Abaqus restart/state injection.

Files created:

- `extract_chaboche_v1_full_statev_cycle_history.py`
- `chaboche_v1_full_statev_cycle_history.csv`
- `chaboche_v1_full_statev_cycle_stability.csv`
- `CHABOCHE_V1_FULL_STATEV_CYCLE_HISTORY_REPORT.md`

Input ODB:

- `chaboche_vp_v1_cyclic_eps005_20cycles.odb`

Execution:

- Command: `abaqus python extract_chaboche_v1_full_statev_cycle_history.py`
- Status: succeeded
- Abaqus was not rerun; only the existing ODB was postprocessed.
- UMAT and input files were not modified.

Extraction:

- Cycle-end targets: cycles `1-20`
- Extracted fields: `SDV1` through `SDV15`
- Values are averaged over the available integration point field values.
- The nearest available ODB frame to each integer cycle-end time was used.

Final cycle-end state at cycle 20:

- `STATEV(1)` / `p` = `0.142025694251`
- `STATEV(2)` / `X11` = `-85.8880233765`
- `STATEV(3)` / `X22` = `42.9440116882`
- `STATEV(4)` / `X33` = `42.9440116882`
- `STATEV(8)` / `Evp11` = `-0.0017925434513`
- `STATEV(9)` / `Evp22` = `0.000896271725651`
- `STATEV(10)` / `Evp33` = `0.000896271725651`
- `STATEV(14)` / `RISO` = `1.41522598267`
- `STATEV(15)` / `DP` = `0`

Stability classification over cycles `2-10`:

- Stable extrapolation candidate: `STATEV(1)` / accumulated viscoplastic strain `p`
- Small or nearly zero components: `STATEV(5-7)` and `STATEV(11-13)` shear components
- Diagnostic or recomputable: `STATEV(14-15)`
- Needs caution: `STATEV(2-4)` normal backstress components and `STATEV(8-10)` normal viscoplastic strain components

Interpretation:

This confirms that a vector-valued Level-2 cycle-jump method cannot simply extrapolate all state variables blindly. `STATEV(1)` remains the cleanest stabilized scalar marker. The shear components are effectively zero for this uniaxial block test. The normal backstress and viscoplastic strain components are physically important for restart/injection, but their cycle-end increments need more careful handling, likely including consistent phase-point extraction and/or vector-valued conservative jump control.

## Vector-Valued STATEV Cycle-Jump Postprocessing Analyzer

A vector-valued STATEV cycle-jump analyzer was created as a Level-2 preparation step. This extends the scalar `SDV1` predictor to selected independent state variables, but it remains postprocessing only.

Files created:

- `vector_statev_cycle_jump_analyzer.py`
- `chaboche_v1_vector_statev_cycle_jump_predictions.csv`
- `chaboche_v1_vector_statev_cycle_jump_errors.csv`
- `chaboche_v1_vector_statev_adaptive_jump_control.csv`
- `CHABOCHE_V1_VECTOR_STATEV_CYCLE_JUMP_REPORT.md`

Inputs:

- `chaboche_v1_full_statev_cycle_history.csv`
- `chaboche_v1_full_statev_cycle_stability.csv`

Method:

- Reference window: cycles `2-10`
- Jump base cycle: `10`
- Active vector components used for jump control: `STATEV(1), STATEV(2-4), STATEV(8-10)`
- Near-zero shear components reported only: `STATEV(5-7), STATEV(11-13)`
- Recomputable/diagnostic components reported only: `STATEV(14-15)`
- No Abaqus rerun, no UMAT edit, no input-file edit, and no `STATEV` injection

Phase consistency:

- Maximum absolute cycle-end frame time error = `0.00974273681641`
- Interpretation: cycle-end data are nearest available ODB frames rather than exact integer cycle times. This is acceptable for this postprocessing diagnostic, but it is important for backstress and viscoplastic strain trends.

Adaptive vector jump result:

- Conservative global `Delta N` = `2`
- Vector-global adaptive target cycle = `12`
- Controlling component = `STATEV(2)` / `X11`
- Controlling component prior stability classification = `needs caution`

Comparison with scalar SDV1-only result:

- Scalar SDV1-only adaptive target retained for comparison = cycle `19`
- Fixed validation target retained for comparison = cycle `20`
- First-order `SDV1` relative error at vector-global target cycle 12 = `0.0118027922862%`
- First-order `SDV1` relative error at scalar adaptive target cycle 19 = `0.0600848519171%`
- First-order `SDV1` relative error at fixed target cycle 20 = `0.0674109657445%`

Active component first-order errors at vector-global target cycle 12:

- `STATEV(1)` / `p`: `0.0118027922862%`
- `STATEV(2)` / `X11`: `0.427408706426%`
- `STATEV(3)` / `X22`: `0.427408706426%`
- `STATEV(4)` / `X33`: `0.427408706426%`
- `STATEV(8)` / `Evp11`: `0.202728724628%`
- `STATEV(9)` / `Evp22`: `0.202728724739%`
- `STATEV(10)` / `Evp33`: `0.202728724739%`

Interpretation:

The vector-valued analysis is more conservative than the scalar SDV1-only cycle jump. While `STATEV(1)` remains highly predictable, the normal backstress and viscoplastic strain components restrict the global vector jump. This confirms that a future Level-2 injected-state Abaqus continuation should not blindly jump only `SDV1` if the goal is a physically consistent material state. A scalar-only injection test may still be useful as a controlled experiment, but a consistent vector state will require careful treatment of `STATEV(1-4,8-10)` and preferably exact phase-point extraction.

## Exact Cycle-End Phase Output Preparation

An exact phase-point output preparation deck was created to remove the cycle-end frame ambiguity observed in the full STATEV extraction and vector-valued cycle-jump analyzer.

Files created:

- `prepare_exact_phase_output_deck.py`
- `chaboche_vp_v1_cyclic_eps005_20cycles_exact_cycle_outputs.inp`
- `CHABOCHE_V1_EXACT_PHASE_OUTPUT_PREP_REPORT.md`

Source input deck:

- `chaboche_vp_v1_cyclic_eps005_20cycles.inp`

Reason:

- Previous maximum absolute cycle-end time error = `0.00974273681641`
- The previous extraction used nearest available ODB frames at cycle-end targets.
- This is acceptable for preliminary diagnostics but not ideal for phase-sensitive state variables such as `STATEV(2-4)` backstress components and `STATEV(8-10)` viscoplastic strain components.

Output-control change in the copied deck:

```text
*OUTPUT, FIELD, TIME INTERVAL=1.0, TIME MARKS=YES
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, SDV

*OUTPUT, HISTORY, TIME INTERVAL=1.0, TIME MARKS=YES
*NODE OUTPUT, NSET=RIGHT_FACE
U1, RF1
```

Preserved:

- Geometry
- Material constants
- UMAT expectation
- Boundary conditions
- Amplitude definition
- Total step time
- Number of cycles

Status:

- Abaqus was not run automatically.
- The original input deck was not modified.
- The UMAT was not modified.
- No `STATEV` injection was attempted.

Next intended use:

Run the copied exact-output deck once, repeat full `STATEV(1-15)` cycle-history extraction, and rerun the vector-valued STATEV cycle-jump analyzer before deciding on any scalar-only or vector-state injection test.

## Exact Cycle-End Output Datacheck

A datacheck-only run was performed for the copied exact-output deck.

Job:

- `chaboche_vp_v1_cyclic_eps005_20cycles_exact_check`

Input:

- `chaboche_vp_v1_cyclic_eps005_20cycles_exact_cycle_outputs.inp`

UMAT:

- `umat\chaboche_vp_v1_working.f`

Environment note:

- The first attempt failed before datacheck because `ifx` was not on the shell `PATH`.
- The second attempt found `ifx` but failed at linking because Microsoft `LINK` was not on the shell `PATH`.
- The successful datacheck used Intel oneAPI plus Visual Studio Build Tools:

```text
set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64
```

Result:

- Datacheck status: passed
- Abaqus job status: completed
- Errors: `0`
- Dat file warnings: `1`
- Full analysis was not run.
- UMAT was not modified.
- Original input deck was not modified.
- No `STATEV` injection was attempted.

Warning:

- Abaqus warned that exact predefined output time points were requested and that `TIME MARKS=YES` can force smaller increments and increase the increment count.
- Interpretation: this warning is expected and confirms that Abaqus accepted the exact phase-point output request.

Report:

- `CHABOCHE_V1_EXACT_PHASE_DATACHECK_REPORT.md`

Next intended step:

Run the full exact-output analysis using the same compiler/linker environment, then repeat full `STATEV(1-15)` extraction and vector-valued STATEV cycle-jump analysis on the exact-output ODB.

## Exact-Output Full STATEV Extraction

The exact-output ODB `chaboche_vp_v1_cyclic_eps005_20cycles_exact.odb` was postprocessed to produce a separate exact-output extraction set.

- Extractor script: `extract_chaboche_v1_full_statev_cycle_history_exact.py`
- History CSV: `chaboche_v1_full_statev_cycle_history_exact.csv`
- Stability CSV: `chaboche_v1_full_statev_cycle_stability_exact.csv`
- Exact extraction report: `CHABOCHE_V1_FULL_STATEV_CYCLE_HISTORY_EXACT_REPORT.md`

Key observation:

- Maximum absolute cycle-end `time_error` = `0` (exact-phase frames), improving on the previous nearest-frame max time error `0.00974273681641`.

Notes:

- Abaqus was not rerun by these postprocessing scripts; the exact-output ODB was produced by the earlier full analysis and then postprocessed.
- UMAT and input files were not modified; no STATEV injection was attempted.

## Level-2 Cycle-Jump Preparation Summary

A comprehensive Level-2 preparation summary was created to synthesize all STATEV diagnostics and formalize the decision to defer injection:

- Document: `CHABOCHE_V1_LEVEL2_CYCLE_JUMP_PREPARATION_SUMMARY.md`
- Optional LaTeX version: `thesis_cycle_jump_section/latex/chaboche_level2_cycle_jump_preparation.tex`

Key conclusion:

The simplified Chaboche-v1 UMAT is increment-schedule sensitive, as revealed by the exact-output diagnostic branch. The 5.12% difference in cycle-20 SDV1 between original and exact-output runs indicates that STATEV injection should be deferred until UMAT integration robustness is improved. The work remains at Level-2 preparation, which is thesis-strong content: it demonstrates rigorous diagnostics and identifies robustness as a prerequisite for Level-3 restart/state injection.

