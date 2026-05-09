# Stage 4B Clean SDVINI Branch Report

Date: May 9, 2026

## Purpose

Promote the proven SDVINI debug branch into a clean non-debug STATEV-only continuation baseline.

## Files

- UMAT: `umat_chaboche_v1_with_sdvini_clean.f`
- Input deck: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean.inp`
- Runner: `run_stage4b_statev_only_clean.bat`
- Postprocessor: `postprocess_stage4b_clean_sdvini_result.py`
- Result CSV: `stage4_injected_cycle_jump/stage4b_clean_sdvini_first_final.csv`
- Detailed report: `stage4_injected_cycle_jump/STAGE4B_CLEAN_SDVINI_BRANCH_REPORT.md`

## Result

- Datacheck job: `chaboche_stage4b_statev_only_clean_check`
- Datacheck status: passed
- Full job: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_clean`
- Full job status: completed
- Increments: 57
- Cutbacks: 0
- User input warnings: 0
- Analysis warnings: 0
- Errors: 0

## First/Final Frame Check

| Frame | Time | STATEV1 | S11 (MPa) |
|---|---:|---:|---:|
| First output frame | 0 | 0.13485494256 | 0 |
| Final output frame | 1 | 0.14071752131 | 368.581756592 |

The clean branch reproduces the debug branch without trace instrumentation.
