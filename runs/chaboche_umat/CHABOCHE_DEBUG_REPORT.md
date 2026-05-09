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

## Stage 3 Increment-Schedule Sensitivity

- DMAX=0.020: STATEV1=0.142025694251
- DMAX=0.010: STATEV1=0.143569096923, +1.0867%
- DMAX=0.005: STATEV1=0.145257070661, +2.2752%
- Conclusion: increment-size sensitivity confirmed

## Stage 4B Direct State Injection Follow-Up

Date: May 9, 2026

Compiler and linker environment:

- Intel oneAPI and Visual Studio Build Tools were loaded successfully.
- `ifx`, `link`, and `abaqus` were all found.
- Batch wrappers that invoke Abaqus from another `.bat` must use `call abaqus ...`.

STATEV-only path:

- Datacheck job: `chaboche_stage4b_statev_only_check`
- Datacheck status: passed
- Full job: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only`
- Full job status: completed
- ODB created: yes
- Increments: 57
- Cutbacks: 0
- User input warnings: 0
- Analysis warnings: 0
- Errors: 0

Interpretation:

- `SDVINI` works.
- STATEV injection mechanics work.
- This path intentionally omits residual stress, so it is not a final cycle-jump accuracy validation.

Direct stress path:

- Original deck `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp` failed because `*INITIAL CONDITIONS, TYPE=STRESS` was placed inside `*STEP`.
- Copied model-level deck created: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.inp`
- Original stress deck was not modified.
- Model-level datacheck job: `chaboche_stage4b_statev_stress_modellevel_check`
- Model-level datacheck status: failed during input processing.
- No `.msg` file was created.

Exact model-level stress error:

```text
***ERROR: AN INITIAL CONDITION HAS BEEN SPECIFIED ON ELEMENT 0 BUT THIS
          ELEMENT HAS NOT BEEN DEFINED
```

Conclusion:

- Moving `*INITIAL CONDITIONS, TYPE=STRESS` to model level fixed the keyword-placement issue.
- Direct stress initialization remains blocked by the element/data-line format.
- Next branch: prepare a `SIGINI` residual-stress initialization variant while preserving the working `SDVINI` STATEV initialization.

## Stage 4B STATEV-Only Postprocess and Direct-Stress Label Tests

Date: May 9, 2026

STATEV-only postprocess:

- Script: `postprocess_stage4b_injection_results.py`
- ODB: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.odb`
- CSV: `stage4_injected_cycle_jump/stage4b_statev_only_result.csv`
- Report: `stage4_injected_cycle_jump/STAGE4B_STATEV_ONLY_RESULT_REPORT.md`

Key comparison against explicit cycle-20 reference:

- STATEV1 result: `0.00559759652242`
- STATEV1 reference: `0.142025694251`
- STATEV1 absolute error: `0.136428097729`
- STATEV1 relative error: `96.0587437703%`
- S11 result: `374.138793945 MPa`
- S11 reference: `376.434143066 MPa`
- S11 absolute error: `2.29534912109 MPa`
- S11 relative error: `0.60976113973%`
- RIGHT_FACE average U1: `0`
- RIGHT_FACE summed RF1: `1496.55517578`

Interpretation:

- SDVINI initialization is confirmed mechanically.
- The completed STATEV-only run is a successful injection-mechanics checkpoint.
- The STATEV-only result is not a final cycle-jump accuracy validation because the residual stress/consistent continuation state is missing.

Direct-stress element-label tests:

- Source deck: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_modellevel.inp`
- Copied deck 1: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_elabel_instance.inp`
- Copied deck 2: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress_elabel_plain.inp`
- Datacheck job 1: `chaboche_stage4b_stress_elabel_instance_check`
- Datacheck job 2: `chaboche_stage4b_stress_elabel_plain_check`
- Result: both failed during input processing.
- No `.msg` file was created for either failed datacheck.

Instance-label error:

```text
***ERROR: AN INITIAL CONDITION HAS BEEN SPECIFIED ON ELEMENT 0 BUT THIS
          ELEMENT HAS NOT BEEN DEFINED
```

Plain-label error:

```text
***ERROR: AN INITIAL CONDITION HAS BEEN SPECIFIED ON ELEMENT 0 BUT THIS
          ELEMENT HAS NOT BEEN DEFINED
LINE IMAGE: , 335.5768737792969, 0.0, 0.0, 0.0, 0.0, 0.0
```

Conclusion:

- Direct stress initialization remains blocked after testing `BLOCK_INST.BLOCK.1`, `BLOCK_INST.1`, and `1`.
- Next branch: create a `SIGINI` residual-stress initialization variant while keeping the validated `SDVINI` path.

## Stage 4B SDVINI Debug Correction

Date: May 9, 2026

Important correction:

- The original STATEV-only full job ran successfully, but it did not numerically prove SDVINI.
- Its final `STATEV1 = 0.00559759652242`, close to a fresh one-cycle result.
- Therefore the original run is a stable control/check run, not a proven injected continuation.

Root findings:

- Original deck `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp` omitted `*INITIAL CONDITIONS, TYPE=SOLUTION, USER`.
- Original `umat_chaboche_v1_with_sdvini.f` used a nonstandard SDVINI signature with `ORNT`; the copied debug UMAT uses the standard Abaqus/Standard `NOEL,NPT,LAYER,KSPT` form.

Copied debug files:

- `umat_chaboche_v1_with_sdvini_debug.f`
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_debug.inp`
- `postprocess_stage4b_sdvini_debug.py`
- `stage4_injected_cycle_jump/stage4b_sdvini_debug_first_final.csv`
- `stage4_injected_cycle_jump/STAGE4B_SDVINI_DEBUG_REPORT.md`

Debug run:

- Datacheck job: `chaboche_stage4b_statev_only_debug_check`
- Datacheck status: passed
- Full debug job: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_debug`
- Full debug status: completed
- Increments: 57
- Cutbacks: 0
- User input warnings: 0
- Analysis warnings: 0
- Errors: 0

ODB first/final frame evidence:

- First output frame time: `0`
- First output `STATEV1 = 0.13485494256`
- Injected cycle-19 `STATEV1 = 0.13485494256`
- Final output time: `1`
- Final output `STATEV1 = 0.14071752131`
- Explicit cycle-20 reference `STATEV1 = 0.142025694251`
- Final absolute error from reference: `0.00130817294121`
- Final `S11 = 368.581756592 MPa`

Conclusion:

- SDVINI is numerically proven in the copied debug branch.
- UMAT does not reset `STATEV1` to zero at initialization; the first ODB frame retains the injected value.
- The original STATEV-only mismatch was due to missing/improper SDVINI activation, not proof that injected STATEV was erased by UMAT.
- Fortran trace-file writes did not appear in the working directory or standard Abaqus text outputs; the ODB first-frame check is the reliable evidence.

Next branch:

- Create a clean corrected STATEV-only branch from the debug fix without trace instrumentation.
- After that, proceed to residual-stress initialization through `SIGINI`.

## Stage 4B.2 Clean SDVINI and SIGINI Branches

Date: May 9, 2026

Clean SDVINI branch:

- UMAT: `umat_chaboche_v1_with_sdvini_clean.f`
- Input: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean.inp`
- Runner: `run_stage4b_statev_only_clean.bat`
- Postprocessor: `postprocess_stage4b_clean_sdvini_result.py`
- Root report: `STAGE4B_CLEAN_SDVINI_BRANCH_REPORT.md`
- Detailed report: `stage4_injected_cycle_jump/STAGE4B_CLEAN_SDVINI_BRANCH_REPORT.md`

Clean branch status:

- Datacheck job: `chaboche_stage4b_statev_only_clean_check`
- Datacheck status: passed
- Full job: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean`
- Full job status: completed
- Increments: 57
- Cutbacks: 0
- User input warnings: 0
- Analysis warnings: 0
- Errors: 0

Clean branch first/final frame:

- First `STATEV1 = 0.13485494256`
- First `S11 = 0 MPa`
- Final `STATEV1 = 0.14071752131`
- Final `S11 = 368.581756592 MPa`
- Conclusion: clean branch reproduces the debug SDVINI result without instrumentation.

STATEV + SIGINI branch:

- UMAT: `umat_chaboche_v1_with_sdvini_sigini.f`
- Input: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini.inp`
- Runner: `run_stage4b_statev_sigini.bat`
- Postprocessor: `postprocess_stage4b_sigini_result.py`
- CSV: `stage4_injected_cycle_jump/stage4b_sigini_result.csv`
- Report: `stage4_injected_cycle_jump/STAGE4B_SIGINI_RESULT_REPORT.md`

SIGINI branch status:

- Datacheck job: `chaboche_stage4b_statev_sigini_check`
- Datacheck status: passed
- Full job: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_sigini`
- Full job status: completed
- Increments: 57
- Cutbacks: 0
- User input warnings: 0
- Analysis warnings: 0
- Errors: 0

SIGINI branch first/final frame:

- First `STATEV1 = 0.13485494256`
- First `S11 = 335.576873779 MPa`
- Final `STATEV1 = 0.141863301396`
- Final `S11 = 375.865997314 MPa`
- Final RIGHT_FACE average `U1 = 0`
- Final RIGHT_FACE summed `RF1 = 1503.46398926`

Reference comparison:

- Cycle-20 `STATEV1 = 0.142025694251`
- Cycle-20 `S11 = 376.434143066 MPa`
- Final STATEV1 absolute error: `0.000162392854691`
- Final S11 absolute error: `0.568145751953 MPa`

Conclusion:

- SDVINI and SIGINI are both numerically proven.
- The FE model starts from injected cycle-19 STATEV and residual stress.
- The one-cycle continuation to cycle 20 completes cleanly.
- This is a controlled exact-state FE continuation demonstration from cycle 19 to cycle 20.

## Stage 5A Predicted Cycle-19 State Preparation

Date: May 9, 2026

Purpose:

- Prepare the first predicted cycle-19 internal state for FE cycle-jump testing.
- Prediction uses cycle-10 data and first-order cycle-space extrapolation to target cycle 19.
- Exact cycle-19 data are used only for validation/error comparison, not for prediction.
- No Abaqus analysis rerun was performed.
- No UMAT was modified.

Files:

- Script: `prepare_stage5a_predicted_cycle19_state.py`
- Output folder: `stage5_predicted_cycle_jump/`
- Predicted STATEV: `stage5_predicted_cycle_jump/cycle19_predicted_statev_for_injection.csv`
- Predicted stress: `stage5_predicted_cycle_jump/cycle19_predicted_stress_for_injection.csv`
- Error CSV: `stage5_predicted_cycle_jump/cycle19_predicted_vs_exact_error.csv`
- Report: `stage5_predicted_cycle_jump/STAGE5A_PREDICTED_CYCLE19_STATE_REPORT.md`

Method:

- Base cycle: `10`
- Target cycle: `19`
- DeltaN: `9`
- Mean increment window: cycles `2-10`
- Formula: `predicted_cycle19 = value_cycle10 + DeltaN * mean_increment_per_cycle`
- `STATEV14` recomputed from predicted `STATEV1`
- `STATEV15` reset to `0` for injection

Key predicted-vs-exact errors:

- `STATEV1`: predicted `0.134935969953`, exact `0.13485494256`, absolute error `8.10273923441e-05`, relative error `0.0600848517717%`
- `STATEV2`: relative error `1.9241569878%`
- `STATEV3`: relative error `1.9241569878%`
- `STATEV4`: relative error `1.9241569878%`
- `STATEV8`: relative error `0.912963742425%`
- `STATEV9`: relative error `0.912963742313%`
- `STATEV10`: relative error `0.912963742313%`
- `S11`: predicted `339.014099121 MPa`, exact `335.576873779 MPa`, absolute error `3.4372253418 MPa`, relative error `1.02427360476%`

Interpretation:

- The first-order predicted cycle-19 `STATEV1` is very accurate.
- The predicted residual stress `S11` is close but slightly above the initial 1% target.
- This Stage 5A result is a candidate input for Stage 5B, with the caveat that stress/backstress prediction errors may dominate the skipped-cycle FE result.

## Stage 5B Predicted-State FE Cycle-Jump Continuation

Date: May 9, 2026

Purpose:

- Run the first true FE skipped-cycle continuation test.
- Workflow: cycle-10 data -> predicted cycle-19 state -> SDVINI/SIGINI injection -> one computed cycle to cycle 20.
- This uses the predicted Stage 5A state, not exact cycle-19 state.

Files:

- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle19.f`
- Input: `chaboche_stage5b_predicted_cycle19_to_cycle20.inp`
- Runner: `run_stage5b_predicted_cycle_jump.bat`
- Monitor: `monitor_stage5b_predicted_cycle_jump.py`
- Postprocessor: `postprocess_stage5b_predicted_cycle_jump.py`
- CSV: `stage5_predicted_cycle_jump/stage5b_predicted_cycle_jump_result.csv`
- Report: `stage5_predicted_cycle_jump/STAGE5B_PREDICTED_CYCLE_JUMP_RESULT_REPORT.md`

Run status:

- Datacheck job: `chaboche_stage5b_predicted_cycle19_to_cycle20_check`
- Datacheck status: passed
- Full job: `chaboche_stage5b_predicted_cycle19_to_cycle20`
- Full job status: completed
- Increments: 57
- Cutbacks: 0
- User input warnings: 0
- Analysis warnings: 0
- Errors: 0

First-frame injection check:

- Injected/predicted `STATEV1 = 0.134935969953`
- First-frame `STATEV1 = 0.134935975075`
- Injected/predicted `S11 = 339.014099121 MPa`
- First-frame `S11 = 339.014099121 MPa`

Final cycle-20 comparison:

- Final `STATEV1 = 0.141955494881`
- Reference `STATEV1 = 0.142025694251`
- STATEV1 absolute error: `7.01993703842e-05`
- STATEV1 relative error: `0.049427232695%`
- Final `S11 = 375.95602417 MPa`
- Reference `S11 = 376.434143066 MPa`
- S11 absolute error: `0.478118896484 MPa`
- S11 relative error: `0.127012627651%`
- Final RIGHT_FACE average `U1 = 0`
- Final RIGHT_FACE summed `RF1 = 1503.82409668`

Comparison to exact-state SIGINI result:

- Difference from exact-state SIGINI final `STATEV1 = 9.21934846763e-05`
- Difference from exact-state SIGINI final `S11 = 0.0900268559218 MPa`

Conclusion:

- Stage 5B satisfies the first-success criterion: both final `STATEV1` and `S11` errors are below 1%.
- This is a successful first FE cycle-skipping demonstration for the simplified Chaboche model.
- Remaining refinement target: improve vector/stress prediction quality for larger or more conservative jumps.

## Stage 6A Explicit 50-Cycle Reference

Date: May 9, 2026

Purpose:

- Create a no-skip 50-cycle Abaqus reference for validating a larger predicted FE cycle jump.
- Intended next jump: cycle 10 -> predicted cycle 49 -> run cycle 49 to 50.
- This increases skipped intermediate cycles from 8 to 38 for the next validation stage.

Files:

- Input deck: `chaboche_vp_v1_cyclic_eps005_50cycles.inp`
- Runner: `run_chaboche_50cycle_reference.bat`
- Monitor: `monitor_chaboche_50cycle_reference.py`
- Postprocessor: `postprocess_chaboche_50cycle_reference.py`
- Summary CSV: `chaboche_vp_v1_cyclic_eps005_50cycles_summary.csv`
- Cycle history CSV: `chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv`
- Report: `CHABOCHE_50CYCLE_REFERENCE_REPORT.md`

Model setup:

- Source basis: validated 20-cycle Chaboche-v1 cyclic deck
- UMAT: `umat/chaboche_vp_v1_working.f`
- Total cycles: `50`
- Total step time: `50.0`
- DMAX: `0.02`
- INC limit: `6000`
- Amplitude: explicit 50-cycle tabular fully reversed sequence
- Original 20-cycle input deck was not modified.
- Stage 5B validated files were not modified.

Run status:

- Datacheck job: `chaboche_vp_v1_cyclic_eps005_50cycles_check`
- Datacheck status: passed
- Full job: `chaboche_vp_v1_cyclic_eps005_50cycles`
- Full job status: completed
- Increments: `2507`
- Cutbacks: `0`
- User input warnings: `0`
- Analysis warnings: `0`
- Errors: `0`

Final cycle-50 reference:

- Final time: `50`
- Final time error: `0`
- Final `STATEV1 = 0.356620669365`
- Final `S11 = 374.653869629 MPa`
- Final RIGHT_FACE average `U1 = 0`
- Final RIGHT_FACE summed `RF1 = 1498.61547852`
- Final cycle increment `Delta_STATEV1 = 0.00713682174683`
- Final cycle increment `Delta_S11 = 40.8583984375 MPa`

Conclusion:

- Stage 6A explicit 50-cycle no-skip reference is ready.
- This is the validation target for Stage 6B predicted jump to cycle 50.

## Stage 6B.1 Predicted Cycle-49 State Preparation

Date: May 9, 2026

Purpose:

- Prepare the larger predicted FE cycle-jump input state for the 50-cycle validation case.
- Intended jump route: cycle 10 data -> predicted cycle 49 state -> one computed continuation cycle to cycle 50.
- Exact cycle-49 data from the 50-cycle no-skip reference were used only for validation/error comparison.
- No Abaqus run was performed.
- No UMAT or Abaqus input deck was modified.

Files:

- Script: `prepare_stage6b_predicted_cycle49_state.py`
- Folder: `stage6_50cycle_jump/`
- Predicted STATEV CSV: `stage6_50cycle_jump/cycle49_predicted_statev_for_injection.csv`
- Predicted stress CSV: `stage6_50cycle_jump/cycle49_predicted_stress_for_injection.csv`
- Error CSV: `stage6_50cycle_jump/cycle49_predicted_vs_exact_error.csv`
- Report: `stage6_50cycle_jump/STAGE6B_PREDICTED_CYCLE49_STATE_REPORT.md`

Prediction setup:

- Base cycle: `10`
- Target cycle: `49`
- DeltaN: `39`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_cycle49 = value_cycle10 + DeltaN * mean_increment_per_cycle`
- Actually skipped intermediate FE cycles in the next test: `38`
- Cycle-jump route would compute `10` base cycles + `1` continuation cycle instead of `50` full cycles.

Key cycle-49 validation errors:

- `STATEV1`: predicted `0.350499925669`, exact `0.349483847618`, relative error `0.290736770316%`
- `STATEV2-4`: relative error `8.35356376404%`
- `STATEV8-10`: relative error `3.96914287256%`
- `S11`: predicted `348.668233236 MPa`, exact `333.795471191 MPa`, relative error `4.45565123814%`

Interpretation:

- The accumulated viscoplastic strain prediction remains reasonable for the 39-cycle extrapolation.
- The stress, backstress, and viscoplastic strain-tensor components show larger drift than in Stage 5A.
- Stage 6B.2 FE injection can be attempted as an exploratory stress-test, but the current first-order predictor is not yet a clean high-confidence cycle-49 input state.
- A shorter target such as cycle 29 or cycle 39, or an improved stress/backstress predictor, is recommended before claiming a robust 50-cycle skipped-FE validation.

## Stage 6C Multi-Target Prediction Scan

Date: May 9, 2026

Purpose:

- Evaluate predicted injection-state quality for target cycles 29, 39, and 49 before running another Abaqus FE cycle-jump continuation.
- Use the existing 50-cycle no-skip reference history.
- Select the largest defensible target for the next FE injection test.
- No Abaqus run was performed.
- No UMAT or Abaqus input deck was modified.

Files:

- Script: `prepare_stage6c_multitarget_prediction_scan.py`
- Folder: `stage6_multitarget_jump_scan/`
- Detailed error CSV: `stage6_multitarget_jump_scan/stage6c_multitarget_prediction_errors.csv`
- Summary CSV: `stage6_multitarget_jump_scan/stage6c_multitarget_prediction_summary.csv`
- Report: `stage6_multitarget_jump_scan/STAGE6C_MULTITARGET_PREDICTION_SCAN_REPORT.md`

Prediction setup:

- Base cycle: `10`
- Mean increment window: cycles `2-10`
- Targets: `29`, `39`, `49`
- Prediction rule: `predicted_target = value_cycle10 + DeltaN * mean_increment_per_cycle`
- `STATEV14` recomputed from predicted `STATEV1`
- `STATEV15` reset to `0`

Scan summary:

| Target | Continue to | DeltaN | Skipped cycles | Computed route | Full route | Reduction | STATEV1 err | STATEV2-4 max err | STATEV8-10 max err | S11 err | Recommendation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 29 | 30 | 19 | 18 | 11 | 30 | 63.3333% | 0.135335% | 4.06463% | 1.92948% | 2.16515% | `acceptable_exploratory_candidate` |
| 39 | 40 | 29 | 28 | 11 | 40 | 72.5% | 0.212701% | 6.20776% | 2.94821% | 3.30894% | `not_headline_candidate` |
| 49 | 50 | 39 | 38 | 11 | 50 | 78% | 0.290737% | 8.35356% | 3.96914% | 4.45565% | `not_headline_candidate` |

Interpretation:

- Target cycle 29 is the largest target satisfying the current decision rules.
- Cycle 29 -> 30 would skip 18 intermediate FE cycles and reduce the computed route from 30 cycles to 11 cycles.
- Targets 39 and 49 remain useful as exploratory stress tests, but are not headline validation candidates with the current first-order vector/stress predictor.
- The scan confirms that scalar `STATEV1` extrapolation remains robust while stress/backstress consistency limits larger FE cycle jumps.

## Stage 6D Predicted Cycle-29 to Cycle-30 FE Jump

Date: May 9, 2026

Purpose:

- Run the largest currently acceptable FE cycle-jump validation from the Stage 6C scan.
- Route: cycle 10 data -> predicted cycle 29 state -> SDVINI/SIGINI injection -> one computed continuation cycle to cycle 30.
- Skipped intermediate FE cycles: cycles 11-28, i.e. `18` cycles.
- Computed-cycle route: `10` base cycles + `1` continuation cycle = `11` computed cycles instead of `30`.

Files:

- Preparation script: `prepare_stage6d_predicted_cycle29_state.py`
- Stage folder: `stage6_cycle29_jump/`
- Predicted STATEV CSV: `stage6_cycle29_jump/cycle29_predicted_statev_for_injection.csv`
- Predicted stress CSV: `stage6_cycle29_jump/cycle29_predicted_stress_for_injection.csv`
- Prediction error CSV: `stage6_cycle29_jump/cycle29_predicted_vs_exact_error.csv`
- Cycle-30 reference CSV: `stage6_cycle29_jump/cycle30_reference_statev_stress.csv`
- UMAT: `umat_chaboche_v1_with_sdvini_sigini_predicted_cycle29.f`
- Input deck: `chaboche_stage6d_predicted_cycle29_to_cycle30.inp`
- Runner: `run_stage6d_predicted_cycle29_jump.bat`
- Monitor: `monitor_stage6d_predicted_cycle29_jump.py`
- Postprocessor: `postprocess_stage6d_predicted_cycle29_jump.py`
- Result CSV: `stage6_cycle29_jump/stage6d_predicted_cycle29_jump_result.csv`
- Result report: `stage6_cycle29_jump/STAGE6D_PREDICTED_CYCLE29_JUMP_RESULT_REPORT.md`

Run status:

- Datacheck job: `chaboche_stage6d_predicted_cycle29_to_cycle30_check`
- Datacheck status: passed
- Full job: `chaboche_stage6d_predicted_cycle29_to_cycle30`
- Full job status: completed
- ODB created: yes
- Increments: `57`
- Cutbacks: `0`
- User input warnings: `0`
- Analysis warnings: `0`
- Errors: `0`

Injection check:

- Expected injected `STATEV1 = 0.206790621858`
- First-frame `STATEV1 = 0.206790626049`
- First-frame `STATEV1` absolute injection error: `4.19090173676e-09`
- Expected injected `S11 = 342.232143826 MPa`
- First-frame `S11 = 342.232147217 MPa`
- First-frame `S11` absolute injection error: `3.3905514556e-06 MPa`

Reference handling:

- The original 50-cycle history row for cycle 30 is at time `29.9902572632`, not exact time `30.0`.
- The Stage 6D result report therefore uses a linear interpolation between the bracketing explicit 50-cycle ODB frames at `29.9902572632` and `30.0102577209`.
- Interpolation alpha: `0.487125691398`
- Interpolated explicit cycle-30 reference:
  - `STATEV1 = 0.213713369924`
  - `S11 = 366.855714346 MPa`
  - RIGHT_FACE `RF1 = 1467.42285738`

Final comparison:

- Final Stage 6D `STATEV1 = 0.213811308146`
- Final `STATEV1` absolute error: `9.79382215782e-05`
- Final `STATEV1` relative error: `0.0458269043313%`
- Final Stage 6D `S11 = 375.453552246 MPa`
- Final `S11` absolute error: `8.59783790031 MPa`
- Final `S11` relative error: `2.34365652874%`
- Final RIGHT_FACE `RF1 = 1501.81420898`
- Final RIGHT_FACE `RF1` relative error: `2.34365652874%`

Conclusion:

- Stage 6D is an `acceptable_exploratory_success` by the stated rule: final `STATEV1 < 1%` and final `S11 < 3%`.
- It is not a clean success because final `S11` is not below `1%`.
- This increases the skipped intermediate FE cycles from Stage 5B's `8` cycles to `18` cycles while retaining excellent accumulated-strain accuracy.
- Stress/backstress prediction remains the limiting factor for larger jumps.

## Stage 3 Thesis Package Integration

The Stage 3 sensitivity result was integrated into the standalone thesis cycle-jump package on May 9, 2026. The package now includes the new subsection, the summary table, the two Stage 3 plots, and the updated standalone PDF.

Current Stage 3 thesis status:

- Commit: `0da3bda`
- Branch: `copilot/curved-cephalopod`
- Message: `Add Chaboche increment-schedule sensitivity summary`

## Stage 4A Preparation: Exact-State Injection

Prepared: May 9, 2026

- Purpose: prepare exact cycle-19 averaged STATEV (and stresses if available)
	for an injection-mechanics continuation test. This confirms whether Abaqus
	can be restarted/continued correctly from an injected explicit state.
- Files created: `stage4_injected_cycle_jump/cycle19_exact_statev_for_injection.csv`,
	`stage4_injected_cycle_jump/cycle19_exact_stress_for_injection.csv`,
	and `stage4_injected_cycle_jump/STAGE4A_EXACT_STATE_INJECTION_PREP_REPORT.md`.
- Note: Stress placeholders are included; extract stresses from the ODB using Abaqus Python
	if exact stress initialization is required.
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

## Thesis Package Integration

The Level-2 preparation subsection was integrated into the standalone thesis cycle-jump PDF package:

- Integration date: May 8, 2026
- Standalone wrapper: `thesis_cycle_jump_section/cycle_jump_chaboche_standalone.tex`
- New section file: `thesis_cycle_jump_section/latex/chaboche_level2_cycle_jump_preparation_section.tex`
- Build report: `thesis_cycle_jump_section/THESIS_SECTION_BUILD_REPORT.md` (updated)

The standalone PDF now contains:
1. **Section 1:** Cycle-Jump Demonstration Using a Chaboche Unified Viscoplastic UMAT (Level-1 scalar SDV1 prediction)
2. **Section 2:** Level-2 Preparation: Full-State Cycle-Jump Diagnostics (Level-2 preparation diagnostics, robustness findings, deferral rationale)

Updated PDF specifications:
- Pages: 8 (previously 6)
- Size: 1070847 bytes
- Compilation status: successful

The thesis narrative is now complete through Level-2 preparation, positioning the work as rigorous cycle-jump diagnostics and preparation rather than attempting incomplete Level-3 implementation.

## Chaboche-v1 Increment-Schedule Sensitivity Study (Stage 3)

Before proceeding to Level-3 full-state STATEV injection and constitutive cycle-jump integration, a controlled robustness study must be performed.

- Increment-sensitivity baseline postprocess: `chaboche_eps005_20cycles_dt_original_output` was postprocessed to produce a state-vector history and summary report under `increment_sensitivity_study/` (see `CHABOCHE_INCREMENT_SENSITIVITY_BASELINE_REPORT.md`).

**Motivation:**

The exact-output diagnostic run revealed that `TIME MARKS=YES` altered the accepted time increment sequence, causing a 5.12232% difference in cycle-20 STATEV(1). This indicates that the Chaboche-v1 UMAT integration is sensitive to time increment scheduling. Before injecting a state vector and restarting the integration, we must quantify this sensitivity and ensure it remains within acceptable bounds for vector-valued continuation.

**Study Package Created:**

- **Preparation script:** `prepare_chaboche_increment_sensitivity_study.py`
- **Study plan:** `CHABOCHE_V1_INCREMENT_SENSITIVITY_STUDY_PLAN.md`
- **Study folder:** `increment_sensitivity_study/`

**Generated input decks (no Abaqus runs yet):**

1. `chaboche_eps005_20cycles_dt_original_output.inp` — baseline (DMAX=0.02, original output)
2. `chaboche_eps005_20cycles_dtmax_0p02.inp` — explicit DMAX=0.02 (same as original)
3. `chaboche_eps005_20cycles_dtmax_0p01.inp` — finer: DMAX=0.01
4. `chaboche_eps005_20cycles_dtmax_0p005.inp` — very fine: DMAX=0.005
5. `chaboche_eps005_20cycles_exact_timemarks_diagnostic.inp` — TIME MARKS=YES reference

**Next Steps:**

1. Run **datacheck** on first deck to verify input integrity.
2. Run each deck sequentially (one full job at a time).
3. Extract STATEV(1-15) and FE metrics from all ODB files.
4. Compare results; determine if variation is acceptable (<0.5%), moderate (1-2%), or high (>5%).
5. Decide whether to proceed to Level-3 or defer STATEV injection pending UMAT robustness improvements.


- Increment-sensitivity baseline run `chaboche_eps005_20cycles_dt_original_output`: STATEV1_cycle20=0.142025694251

- Increment-sensitivity baseline run `chaboche_eps005_20cycles_dtmax_0p01`: STATEV1_cycle20=0.143569096923

## dtmax_0p005 Increment-Limit Correction (Copied Deck)

- Original full run `chaboche_eps005_20cycles_dtmax_0p005` failed because `INC=2500` was insufficient for `DMAX=0.005` and total step time `20.0`.
- Theoretical minimum increments at max-step sizing: `20 / 0.005 = 4000`.
- A copied deck was created (no overwrite):
	- `increment_sensitivity_study\chaboche_eps005_20cycles_dtmax_0p005_inc6000.inp`
- Required step update applied in copied deck:
	- `*STEP, NAME=CYCLIC_20, NLGEOM=NO, INC=6000`
- Preserved unchanged in copied deck:
	- `DMAX=0.005`
	- total step time `20.0`
	- geometry, material constants, boundary conditions, amplitude, and output requests
	- UMAT path expectation (`umat\chaboche_vp_v1_working.f`)
- UMAT change: none
- Physics/modeling change: none (increment-capacity fix only)

Datacheck status for copied deck job `chaboche_eps005_20cycles_dtmax_0p005_inc6000_check`:

- passed
- no warning/error messages observed in the datacheck message summary block
- full analysis intentionally not run yet

- Increment-sensitivity baseline run `chaboche_eps005_20cycles_dtmax_0p005_inc6000`: STATEV1_cycle20=0.145257070661

- Increment-sensitivity baseline run `chaboche_eps005_20cycles_dtmax_0p005_inc6000`: STATEV1_cycle20=0.145257070661

- Increment-sensitivity baseline run `chaboche_eps005_20cycles_dtmax_0p005_inc6000`: STATEV1_cycle20=0.145257070661

## Stage 3 Increment-Schedule Sensitivity

- DMAX=0.020: STATEV1=0.142025694251
- DMAX=0.010: STATEV1=0.143569096923, +1.0867%
- DMAX=0.005: STATEV1=0.145257070661, +2.2752%
- Conclusion: increment-size sensitivity confirmed
