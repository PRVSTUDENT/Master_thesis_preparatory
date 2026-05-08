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
