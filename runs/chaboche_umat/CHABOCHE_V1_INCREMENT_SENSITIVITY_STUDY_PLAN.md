# Chaboche-v1 Increment-Schedule Sensitivity Study Plan

## Purpose

Quantify how sensitive the Chaboche-v1 UMAT integration is to the accepted time increment schedule (DMAX parameter in Abaqus *STATIC step definition).

## Background and Motivation

### Level-1 and Level-2 Progress

- **Level 1 (Postprocessing):** Scalar SDV1 cycle-jump predictor validated with 0.0674% error over 20 cycles.
- **Level 2 (Preparation):** Full STATEV extraction and vector-valued cycle-jump diagnostics completed. Analysis identified:
  - Normal backstress and viscoplastic strain components exhibit higher cycle-to-cycle variability than scalar accumulated strain.
  - Vector-valued jump control is more conservative: original DeltaN=2 (target cycle 12) controlled by STATEV(2)/X11.
  - Exact-phase diagnostic run using `TIME MARKS=YES` successfully removed frame-time ambiguity (time_error=0).

### Critical Finding: Increment-Schedule Sensitivity

The exact-output diagnostic run with `TIME MARKS=YES` revealed an **unexpected 5.12232% difference in cycle-20 STATEV(1)**:

| Metric | Original | Exact-output | Difference |
| --- | ---: | ---: | ---: |
| Cycle-20 STATEV(1) | 0.142025694251 | 0.134750679135 | -5.12232% |
| Max cycle-end time_error | 0.00974 | 0 | improved |

The `TIME MARKS=YES` directive forced Abaqus to accept smaller time increments to align output with integer cycle times. This altered the accepted increment sequence, causing the UMAT to integrate along a different computational path and produce a measurably different cumulative viscoplastic strain.

### Why Before STATEV Injection?

Before implementing Level-3 constitutive cycle-jump integration (injecting the full 13-component STATEV vector and restarting), we must understand:

1. **How much does the UMAT response depend on increment schedule?** If STATEV(1) changes by 5% when INCREMENT SCHEDULE changes slightly, what happens when we inject a state vector and continue integration with a different increment sequence?

2. **Is there a robust integration baseline?** If reducing DMAX by half causes SDV1 to diverge significantly, the UMAT integration may not be sufficiently robust for reliable state injection.

3. **What is the acceptable tolerance?** Scalar SDV1 jumping showed 0.0674% error; if increment-schedule changes cause larger errors, we should improve UMAT robustness before committing to Level-3.

## Study Design

### Approach

Run the 20-cycle Chaboche-v1 analysis using five controlled input decks that vary only the time increment schedule and output request settings. All other parameters (geometry, material, boundary conditions, load history, UMAT) remain identical.

### Generated Input Decks

All decks are located in: `increment_sensitivity_study/`

#### 1. Baseline: Original Deck with Original Output
- **File:** `chaboche_eps005_20cycles_dt_original_output.inp`
- **DMAX:** 0.02 (original)
- **TIME MARKS:** No (original nearest-frame output)
- **Purpose:** Establishes baseline. This is the validated 20-cycle run used in Level-1 and Level-2 analyses.
- **Expected increments:** ~507 (from original run logs)

#### 2. DMAX=0.02 (Same as Original, Explicitly Labeled)
- **File:** `chaboche_eps005_20cycles_dtmax_0p02.inp`
- **DMAX:** 0.02 (unchanged from original)
- **TIME MARKS:** No
- **Purpose:** Confirms that explicit DMAX specification does not change behavior.
- **Expected increments:** ~507 (should match baseline)
- **Expected SDV1(20):** should match baseline (within numerical precision)

#### 3. DMAX=0.01 (Half of Original)
- **File:** `chaboche_eps005_20cycles_dtmax_0p01.inp`
- **DMAX:** 0.01 (half)
- **TIME MARKS:** No
- **Purpose:** Tests sensitivity to finer increment resolution.
- **Expected increments:** ~1000+ (Abaqus will use more, smaller increments)
- **Expected SDV1(20):** varies from baseline if UMAT is increment-schedule sensitive

#### 4. DMAX=0.005 (Quarter of Original)
- **File:** `chaboche_eps005_20cycles_dtmax_0p005.inp`
- **DMAX:** 0.005 (quarter)
- **TIME MARKS:** No
- **Purpose:** Tests sensitivity to very fine increment resolution.
- **Expected increments:** ~2000+ (even finer integration)
- **Expected SDV1(20):** largest divergence expected if sensitivity is high

#### 5. Exact-Output with TIME MARKS (Diagnostic Reference)
- **File:** `chaboche_eps005_20cycles_exact_timemarks_diagnostic.inp`
- **DMAX:** 0.02 (same as original)
- **TIME MARKS:** Yes (forces exact cycle-end output)
- **Purpose:** Replicates the diagnostic branch for comparison. Isolates the effect of `TIME MARKS=YES`.
- **Expected increments:** ~1000+ (Abaqus adjusts to hit exact output times)
- **Expected SDV1(20):** 0.134750679135 (from prior diagnostic run)

## Execution Plan

### Suggested Run Sequence

Run **one datacheck first**, then execute full runs one at a time to allow incremental analysis:

```bash
# Datacheck first (minimal resource cost, catches input errors)
abaqus job=chaboche_eps005_20cycles_dt_original_output input=increment_sensitivity_study/chaboche_eps005_20cycles_dt_original_output.inp user=umat/chaboche_vp_v1_working.f datacheck interactive

# If datacheck passes, proceed with full runs
abaqus job=chaboche_eps005_20cycles_dt_original_output input=increment_sensitivity_study/chaboche_eps005_20cycles_dt_original_output.inp user=umat/chaboche_vp_v1_working.f interactive
abaqus job=chaboche_eps005_20cycles_dtmax_0p02 input=increment_sensitivity_study/chaboche_eps005_20cycles_dtmax_0p02.inp user=umat/chaboche_vp_v1_working.f interactive
abaqus job=chaboche_eps005_20cycles_dtmax_0p01 input=increment_sensitivity_study/chaboche_eps005_20cycles_dtmax_0p01.inp user=umat/chaboche_vp_v1_working.f interactive
abaqus job=chaboche_eps005_20cycles_dtmax_0p005 input=increment_sensitivity_study/chaboche_eps005_20cycles_dtmax_0p005.inp user=umat/chaboche_vp_v1_working.f interactive
abaqus job=chaboche_eps005_20cycles_exact_timemarks_diagnostic input=increment_sensitivity_study/chaboche_eps005_20cycles_exact_timemarks_diagnostic.inp user=umat/chaboche_vp_v1_working.f interactive
```

Or batch in a file using the provided `run_increment_sensitivity_study.bat` wrapper (if generated).

### Output Files

Each Abaqus run will produce:
- `.odb` file (binary database with results)
- `.msg` file (message log with summary)
- `.sta` file (status file)
- `.com` file (compilation log, if user subroutine is compiled)

### Postprocessing

After all runs complete, extract key metrics:

```bash
abaqus python extract_increment_sensitivity_results.py
```

This will produce:
- `chaboche_increment_sensitivity_summary.csv` (comparison table)
- `CHABOCHE_V1_INCREMENT_SENSITIVITY_REPORT.md` (analysis)

## Comparison Metrics

For each run, extract and compare:

### Primary Metrics (STATEV components)
- **STATEV(1):** Accumulated viscoplastic strain (p)
  - Baseline: 0.142025694251
  - Tolerance check: accept ±0.5% variation (0.707e-3)
- **STATEV(2-4):** Backstress tensor normal components (X11, X22, X33)
  - Check relative variation across runs
  - Note any systematic trends
- **STATEV(8-10):** Viscoplastic strain tensor normal components (Evp11, Evp22, Evp33)
  - Check relative variation across runs
- **STATEV(14):** RISO (isotropic hardening stress)
  - Should be recomputable from STATEV(1); check consistency

### Secondary Metrics (FE results)
- **Final S11:** Stress at cycle 20
- **Final RF1:** Reaction force at cycle 20
- **Number of increments:** Compare across decks
- **Warnings/errors:** Check .msg and .sta files for signs of convergence issues

## Interpretation and Decision Tree

### Expected Outcomes

#### Scenario A: UMAT is Robust (Small Variation)
- STATEV(1) varies by <0.5% across DMAX=0.02, 0.01, 0.005 decks
- Backstress and viscoplastic strain also show small, systematic changes
- **Interpretation:** UMAT integration is numerically stable. Proceed to Level-3 with confidence.
- **Next step:** Plan STATEV injection pilot test.

#### Scenario B: UMAT is Moderately Sensitive (1-2% Variation)
- STATEV(1) varies by 1-2% across DMAX variations
- Changes are monotonic (finer increments converge to a limit)
- **Interpretation:** UMAT shows expected convergence behavior. May proceed to Level-3 with adaptive increment selection.
- **Next step:** Optimize Abaqus step parameters; test Level-3 with tight tolerances.

#### Scenario C: UMAT is Highly Sensitive (>5% Variation)
- STATEV(1) varies by >5% across DMAX variations
- Changes are erratic or show large jumps
- TIME MARKS diagnostic shows outlier result (already observed: 5.12%)
- **Interpretation:** UMAT integration is numerically unstable or insufficiently robust for state injection.
- **Next step:** Defer Level-3. Recommend improving UMAT integration robustness (tighter tolerance in constitutive equations, adaptive sub-stepping, etc.).

### Decision Framework

| Scenario | STATEV(1) Variation | Backstress/Strain Variation | Convergence | Thesis Decision |
| --- | --- | --- | --- | --- |
| A (Robust) | <0.5% | ~similar | monotonic | Proceed to L3 |
| B (Moderate) | 1-2% | ~similar | monotonic | Proceed with caution |
| C (High) | >5% | erratic | poor | Defer L3; improve UMAT |

## Thesis Integration

### Current Thesis Narrative (after Level-2)

> The Chaboche-v1 scalar SDV1 cycle-jump predictor is validated at postprocessing level with 0.0674% error. Full-state Level-2 preparation diagnostics are complete. The exact-output diagnostic revealed increment-schedule sensitivity (5.12% change when TIME MARKS=YES), necessitating a robustness study before full STATEV injection.

### Thesis Narrative (after Sensitivity Study)

**If Scenario A or B:**

> The scalar cycle-jump method is validated. Level-2 diagnostics and the increment-schedule sensitivity study confirm that the UMAT integration is sufficiently robust for Level-3 constitutive cycle-jump implementation. State injection testing will proceed with controlled Abaqus increment parameters.

**If Scenario C:**

> The scalar cycle-jump method is validated at postprocessing level. However, Level-2 diagnostics and the increment-schedule sensitivity study reveal that the Chaboche-v1 UMAT integration is sensitive to the accepted time increment schedule. Specifically, reducing DMAX by factors of 2-4 produces cycle-20 STATEV(1) variations of X%, indicating that Level-3 full-state injection should be deferred until UMAT integration robustness is improved. This thesis presents the complete Level-1 and Level-2 diagnostic framework; Level-3 implementation is recommended as future work after UMAT hardening.

## Files and References

- **Study decks:** `increment_sensitivity_study/*.inp`
- **Preparation script:** `prepare_chaboche_increment_sensitivity_study.py`
- **This plan:** `CHABOCHE_V1_INCREMENT_SENSITIVITY_STUDY_PLAN.md`
- **Prior Level-2 analysis:** `CHABOCHE_V1_ORIGINAL_VS_EXACT_STATEV_COMPARISON_REPORT.md`
- **Postprocessing script (to be created):** `extract_increment_sensitivity_results.py`

## Status

- **Preparation:** ✓ Complete. Five input decks created with documented modifications.
- **Datacheck:** ⊘ Pending
- **Full runs:** ⊘ Pending
- **Extraction and analysis:** ⊘ Pending
- **Thesis integration:** ⊘ Pending results

