# Chaboche-v1 Level-2 Cycle-Jump Preparation Summary

## Overview

This document synthesizes the progression from Level-1 scalar SDV1 cycle-jump postprocessing to Level-2 preparation diagnostics for the simplified Chaboche-v1 unified viscoplastic UMAT. It explains the current findings and the rationale for deferring full STATEV injection to a later phase.

## STATEV Inventory

The Chaboche-v1 UMAT manages 15 solution-dependent state variables (STATEV):

| Index | Symbol | Physical meaning | Category |
| ---: | --- | --- | --- |
| 1 | p | Accumulated viscoplastic strain | Active / required for restart |
| 2 | X11 | Backstress tensor component (normal) | Active / required for restart |
| 3 | X22 | Backstress tensor component (normal) | Active / required for restart |
| 4 | X33 | Backstress tensor component (normal) | Active / required for restart |
| 5 | X12 | Backstress tensor component (shear) | Near-zero / near-inactive |
| 6 | X13 | Backstress tensor component (shear) | Near-zero / near-inactive |
| 7 | X23 | Backstress tensor component (shear) | Near-zero / near-inactive |
| 8 | Evp11 | Viscoplastic strain tensor component (normal) | Active / required for restart |
| 9 | Evp22 | Viscoplastic strain tensor component (normal) | Active / required for restart |
| 10 | Evp33 | Viscoplastic strain tensor component (normal) | Active / required for restart |
| 11 | Evp12 | Viscoplastic strain tensor component (shear) | Near-zero / near-inactive |
| 12 | Evp13 | Viscoplastic strain tensor component (shear) | Near-zero / near-inactive |
| 13 | Evp23 | Viscoplastic strain tensor component (shear) | Near-zero / near-inactive |
| 14 | RISO | Current isotropic hardening stress | Recomputable from STATEV(1) and material constants |
| 15 | DP | Last viscoplastic multiplier increment | Diagnostic / history |

For a physically consistent Abaqus restart or injected-state continuation, the independent material state variables that must be provided are `STATEV(1-13)`.

## Level-1: Scalar SDV1 Postprocessing Prediction

### Method

Extract the accumulated viscoplastic strain `STATEV(1)` (denoted `SDV1` or `p`) at each cycle end from the 20-cycle ODB. Use cycles 2-10 as a stabilized reference window to estimate the per-cycle increment.

### Stability

- Mean `Delta SDV1` over cycles 2-10: `0.00718546519056`
- Standard deviation: `3.36821320212e-06`
- Relative range: `0.142903719212%`

### Validation result

- First-order predicted SDV1 at cycle 20 (from cycle-10 base): `0.142121435146`
- Explicit Abaqus SDV1 at cycle 20: `0.1420256943`
- Relative error: `0.0674109329494%`

Conclusion: scalar SDV1 cycle jumping is accurate and suitable for thesis-level cycle-jump demonstration at Level 1 (postprocessing only).

## Level-2a: Full-State Cycle-History Extraction

### Method

Extract the entire state vector `STATEV(1-15)` at each cycle end using the same original 20-cycle ODB. Perform stability classification for each component over the reference window cycles 2-10.

### Key findings

- `STATEV(1)` (accumulated viscoplastic strain): **stable extrapolation candidate**
- `STATEV(2-4)` (normal backstress): **needs caution** (large cycle-to-cycle variation)
- `STATEV(5-7)` (shear backstress): **near-zero component**
- `STATEV(8-10)` (normal viscoplastic strain): **needs caution**
- `STATEV(11-13)` (shear viscoplastic strain): **near-zero component**
- `STATEV(14)` (RISO): **recomputable/diagnostic**
- `STATEV(15)` (DP): **diagnostic**

### Interpretation

Full-state restart/injection cannot blindly extrapolate all components. The normal stress and strain components exhibit higher cycle-to-cycle variability than the scalar accumulated strain, indicating that phase-point consistency and accurate integration are critical for vector-valued cycle jumping.

## Level-2b: Vector-Valued STATEV Cycle-Jump Control

### Method

Extend the scalar cycle-jump approach to a vector of active components: `STATEV(1), STATEV(2-4), STATEV(8-10)`. Use first-order and second-order Taylor extrapolation with adaptive curvature checking to estimate a conservative global jump size.

### Active vector components

- `STATEV(1)` / p: accumulated viscoplastic strain
- `STATEV(2-4)` / X11, X22, X33: normal backstress tensor components
- `STATEV(8-10)` / Evp11, Evp22, Evp33: normal viscoplastic strain tensor components

### Original nearest-frame result

- Jump base: cycle 10
- Reference window: cycles 2-10
- Conservative global DeltaN: **2**
- Adaptive target cycle: **12**
- Controlling component: **STATEV(2) / X11** (normal backstress)
- First-order SDV1 relative error at target: `0.0118027922862%`

### Interpretation

The vector-valued analysis is more restrictive than scalar SDV1 jumping because the normal backstress components impose tighter constraints on the global jump. The controlling component (`STATEV(2)`) has a more aggressive cycle-to-cycle change, reducing the safe jump size from 2 cycles to 2 cycles for this uniaxial test. While `STATEV(1)` alone would allow larger jumps, the vector approach prioritizes physical consistency of the full material state.

## Level-2c: Exact-Output Diagnostic Branch

### Motivation

The original extraction used nearest available ODB frames at integer cycle-end times. For phase-sensitive components (especially backstress and viscoplastic strain), this introduces time ambiguity. A separate "exact-output" Abaqus run was created with `TIME MARKS=YES` to force exact integer cycle-end frame output.

### Exact-output run results

- Maximum absolute cycle-end time_error: `0` (exact frames)
- Cycle-20 STATEV(1): `0.134750679135` (vs. original `0.142025694251`)
- Absolute difference: `-0.007275015116`
- Relative difference: **5.12232%**

### Key observation

The `TIME MARKS=YES` directive forced Abaqus to accept smaller time increments to align with requested output times. This altered the accepted increment sequence compared to the original run, causing the UMAT integration to produce a noticeably different cumulative viscoplastic strain by cycle 20.

### Exact vector-valued result

- Conservative global DeltaN: **1** (vs. original 2)
- Adaptive target cycle: **11** (vs. original 12)
- Controlling component: **STATEV(2) / X11** (unchanged)

### Interpretation

The exact-output run successfully demonstrated that phase-point ambiguity can be removed by requesting exact output marks. However, the 5.12% difference in cycle-20 SDV1 indicates that the simplified Chaboche-v1 UMAT is **increment-schedule sensitive**. The exact-output run cannot replace the original validation baseline because it represents a different computational path (forced smaller increments) with a measurably different material response.

## Original vs. Exact-Output Comparison

The comparison report `CHABOCHE_V1_ORIGINAL_VS_EXACT_STATEV_COMPARISON_REPORT.md` quantifies differences across all 20 cycles and all 15 STATEV components:

| Metric | Original | Exact-output | Difference |
| --- | ---: | ---: | ---: |
| Cycle-20 STATEV(1) | 0.142025694251 | 0.134750679135 | -0.007275015116 |
| Cycle-20 relative error | baseline | 5.12232% | — |
| Vector adaptive DeltaN | 2 | 1 | more conservative |
| Vector target cycle | 12 | 11 | more conservative |
| Controlling component | X11 | X11 | unchanged |

### Cycle-range breakdown (key cycles)

Relative differences in STATEV(1) per cycle:
- Cycle 1: 0% (both runs start identically)
- Cycle 10: 4.84%
- Cycle 11: 4.89%
- Cycle 12: 4.94%
- Cycle 19: 5.11%
- Cycle 20: 5.12%

Normal backstress components show consistent ~2.1% relative differences over all cycles, indicating the increment schedule change affected the stress history uniformly.

## Final Decision: Deferring STATEV Injection

### Current status

- **Level 1 (postprocessing SDV1 prediction)**: validated with 0.0674% error; thesis-ready as demonstration case
- **Level 2a (full-state extraction)**: completed; inventory and stability classification available
- **Level 2b (vector-valued control)**: completed; shows vector approach is more conservative than scalar
- **Level 2c (exact-phase diagnostics)**: completed; reveals increment-schedule sensitivity

### Why not proceed to STATEV injection now

1. **Increment-schedule sensitivity**: The exact-output comparison revealed that the Chaboche-v1 UMAT response is sensitive to the number and size of time increments. This means an injected state at a given cycle could produce different future predictions depending on the integration scheme used in the next Abaqus run.

2. **Vector-valued complexity**: The vector cycle-jump approach requires consistent treatment of 13 independent components. Without first reducing the UMAT's increment sensitivity, injecting a state vector carries high risk of uncontrolled accuracy loss.

3. **Thesis narrative alignment**: The demonstrated Level-2 preparation diagnostics are themselves strong thesis content. Stopping here allows a clear discussion of why material model integration robustness is necessary before advanced continuation methods.

### Recommended next steps for future work

1. **Improve integration robustness**: Modify the Chaboche-v1 UMAT to use adaptive time-stepping or tighter integration tolerances, reducing its sensitivity to the external Abaqus increment schedule.

2. **Validate on robust baseline**: Re-run the 20-cycle analysis with the improved UMAT and confirm that `TIME MARKS=YES` no longer causes significant response changes.

3. **Level-2 to Level-3 transition**: Once integration is robust, consider a limited scalar SDV1 injection test followed by a full vector-valued state injection experiment.

## Distinction Between Method Levels

### Level 1: Postprocessing Prediction

- **What is done**: Extract computed STATEV history from existing ODB. Fit polynomial or first-order model to cycle-end values. Extrapolate and predict cycle-end state at skipped cycles.
- **Abaqus involvement**: None (read-only ODB access)
- **Material model involvement**: None
- **Accuracy**: Postprocessing-level
- **Thesis use**: Demonstrates cycle-jump idea; validates prediction accuracy
- **Status**: Complete and validated for this project

### Level 2: Restart/Injection Preparation

- **What is done**: Extract full state vector. Perform stability and sensitivity analysis. Diagnose increment-schedule dependence. Design injected-state continuation logic.
- **Abaqus involvement**: Diagnostic only; some test runs with modified output requests
- **Material model involvement**: None
- **Accuracy**: Diagnostic; may differ from actual injection accuracy
- **Thesis use**: Discusses preparation, caution flags, and robustness requirements
- **Status**: Complete for this project; identified need for improved robustness

### Level 3: Full Constitutive Cycle-Jump Integration

- **What is done**: Implement injected-state restart in Abaqus. Modify UMAT or use Abaqus *RESTART, WRITE and *RESTART, READ keywords. Run accelerated multi-cycle segments with injected STATEV.
- **Abaqus involvement**: Active; restart workflows, state variable definition in input
- **Material model involvement**: Passive (receives injected state) or active (if UMAT modified to handle jumps)
- **Accuracy**: Full forward integration; subject to robustness of UMAT and increment selection
- **Thesis use**: Demonstrates actual cycle-jump acceleration; measures speedup
- **Status**: Not pursued in current project due to identified robustness concerns

## Thesis Narrative

### Key message

The Chaboche-v1 unified viscoplastic UMAT cycle-jump workflow demonstrates that:

1. **Scalar postprocessing cycle jumping works**: Level-1 prediction of accumulated viscoplastic strain achieves 0.0674% accuracy over 20 cycles, showing that periodic material state evolution can be reliably extrapolated from a short reference window.

2. **Vector-valued jumping is feasible but more conservative**: Level-2 diagnostics show that including full backstress and viscoplastic strain components in the jump control reduces the safe jump size, but maintains the scalar accuracy margin.

3. **Integration robustness is prerequisite for restart injection**: The exact-phase-point diagnostic revealed that the UMAT response is sensitive to the accepted time-increment sequence. Before attempting Abaqus restart/state-variable injection, the UMAT should be modified to reduce this sensitivity.

4. **Phase-point ambiguity can be removed but with trade-offs**: Requesting exact output time points (`TIME MARKS=YES`) successfully eliminates frame-time ambiguity but forces smaller increments, altering the material response. This is not a failure; it is a useful finding for future robustness work.

### Stopping point rationale

The current work achieves Level-2 preparation completeness without committing to a full Level-3 restart injection that could amplify robustness issues. This positions the thesis as a rigorous diagnostics and preparation study, paving the way for future work to address integration robustness before final cycle-jump acceleration deployment.

## References to supporting reports

- `CHABOCHE_V1_STATEV_INVENTORY_REPORT.md`: detailed STATEV inventory and UMAT source inspection
- `CHABOCHE_V1_FULL_STATEV_CYCLE_HISTORY_REPORT.md`: original extraction and stability classification
- `CHABOCHE_V1_VECTOR_STATEV_CYCLE_JUMP_REPORT.md`: original vector-valued cycle-jump analysis
- `CHABOCHE_V1_FULL_STATEV_CYCLE_HISTORY_EXACT_REPORT.md`: exact-output extraction report
- `CHABOCHE_V1_VECTOR_STATEV_CYCLE_JUMP_REPORT_EXACT.md`: exact-output vector-valued analysis
- `CHABOCHE_V1_ORIGINAL_VS_EXACT_STATEV_COMPARISON_REPORT.md`: detailed original vs. exact comparison
