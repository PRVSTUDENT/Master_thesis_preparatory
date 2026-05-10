# Chaboche Cycle-Jump FE Validation: Master Debug Report

## Overview

This document tracks all major work phases and debugging decisions for the Chaboche-v1 UMAT cycle-jumping validation project.

**Current Stage:** 4A.1 (Exact-state injection data extraction) — **COMPLETE**

---

## Stage 4A.1: Exact-State Injection Data Extraction (COMPLETE)

**Objective:** Extract exact cycle-19 and cycle-20 STATEV and stress from validated ODB for injection-mechanics testing.

**Date Completed:** May 9, 2026  
**Tool:** Abaqus Python / odbAccess2

**Results Summary:**

| Metric | Value |
|--------|-------|
| Cycle-19 frame time | 18.990257 s |
| Cycle-19 time error | 9.743e-03 s (~9.7 ms) |
| Cycle-20 frame time | 20.000000 s |
| Cycle-20 time error | 0.0 s |
| Cycle-19 residual S11 | 335.577 MPa |
| Cycle-20 reference S11 | 376.434 MPa |
| Cycle-19 STATEV1 (acc. viscoplastic strain) | 0.134855 |
| Cycle-20 reference STATEV1 | 0.142026 |

**Key Findings:**

1. **ODB Structure:** The ODB contains 1008 frames across a single step named `CYCLIC_20`. SDV fields are stored individually (SDV1, SDV2, ..., SDV15), not as a composite array.

2. **Cycle-19 Time Precision:** The nearest frame to time 19.0 occurs at 18.990257 s, representing a 9.7 millisecond deviation. This is within acceptable tolerance for injection testing.

3. **STATEV Continuity:** STATEV1 increases by 0.007171 (5.3%) from cycle 19 to cycle 20, consistent with monotonic cyclic plastic hardening expected in the Chaboche model.

4. **Residual Stress:** Significant uniaxial stress remains at cycle-19 (335.6 MPa in S11), increasing to 376.4 MPa by cycle-20. This residual stress is **critical** for accurate state injection; omitting it would introduce a physically inconsistent restart state.

5. **Off-diagonal Stresses:** Stress components S22, S33, S12, S13, S23 are all essentially zero (10^−15 to 10^−16 range), confirming uniaxial loading as expected.

**Outputs Created:**

All files in `runs/chaboche_umat/stage4_injected_cycle_jump/`:
- `cycle19_exact_statev_for_injection.csv` — STATEV1..STATEV15 for cycle 19
- `cycle19_exact_stress_for_injection.csv` — S11, S22, S33, S12, S13, S23 for cycle 19
- `cycle20_reference_statev.csv` — Reference STATEV for cycle 20 (comparison)
- `cycle20_reference_stress.csv` — Reference stress for cycle 20 (comparison)
- `STAGE4A_EXACT_STATE_INJECTION_PREP_REPORT.md` — Detailed extraction report with tables

**Technical Details:**

- **Source ODB:** `chaboche_vp_v1_cyclic_eps005_20cycles.odb` (20-cycle explicit baseline)
- **Extraction Method:** Abaqus Python (`abaqus python prepare_stage4a_exact_state_injection_data.py`)
- **Integration Averaging:** All stress and STATEV values averaged over all integration points in the model
- **Frame Selection:** Binary-search-like approach to find nearest frame to target times 19.0 and 20.0

**Next Steps:**

Ready to proceed to **Stage 4B**: Create SDVINI-based injected continuation input decks.
- Variant 1: STATEV-only injection (no stress initialization)
- Variant 2: STATEV+stress injection (full state initialization)

These tests will validate the cycle-skipping mechanics by comparing injected cycle-20 results against explicit cycle-20 baseline.

---

## Previous Stages (Summary)

### Stage 3: Increment-Size Sensitivity Study (COMPLETE)

The Chaboche-v1 UMAT was validated to be increment-size sensitive. STATEV1 increases monotonically as time-step size DMAX decreases (0.020 → 0.010 → 0.005 s), with a total sensitivity of ~2.3% over 4× step reduction. This confirmed that Level-3 (predicted state-jumping) must account for step-size effects, justifying the deferral to Level-3A (cycle-skipping via injected-state continuation using real explicit data).

### Stage 2: Full-STATEV Diagnostics (COMPLETE)

Confirmed that all 15 state variables are correctly integrated by the UMAT and extracted from the ODB. STATEV values show physically reasonable behavior:
- STATEV1: Accumulated viscoplastic strain (increases monotonically with cycles)
- STATEV2..4: Backstress components (cyclic hardening / softening)
- STATEV8..10: Viscoplastic strain components (deviatoric)
- STATEV14: Isotropic hardening (RISO from pressure-dependent term)

### Stage 1: SDV1 Validation (COMPLETE)

Baseline 20-cycle simulation validated. SDV1 (STATEV1 in UMAT notation) reaches 0.13485 by cycle-19 and 0.14203 by cycle-20, consistent with expected cyclic plastic hardening for ε_amplitude = 0.05.

---

## Architecture

**Core UMAT:** `umat_chaboche_v1.f` (no modifications in cycle-skip work)

**Input Deck Template:** `chaboche_eps005_20cycles.inp` (baseline for Stage 4 tests; Stage 4A extracted data from this via ODB)

**Cycle-Skipping Validation Structure:**
```
Stage 4A: Extract exact state (COMPLETE) ✓
├── 4A.1: ODB stress extraction (COMPLETE) ✓
└── 4A: CSV preparation (COMPLETE) ✓
    ↓
Stage 4B: Create injected continuation decks (PENDING)
├── 4B.1: STATEV-only variant
├── 4B.2: STATEV+stress variant
└── 4B: Run tests and compare results
```

---

---

## Stage 4B: Exact-State Injection Deck Preparation (COMPLETE)

**Objective:** Create SDVINI-based injected continuation input decks for two test variants.

**Date Completed:** May 9, 2026

**Deliverables:**

1. **UMAT + SDVINI Subroutine** (`umat_chaboche_v1_with_sdvini.f`)
   - Original Chaboche-v1 UMAT (unmodified)
   - New SDVINI subroutine initializing STATEV(1..15) from cycle-19 extracted values
   - Hardcoded cycle-19 state values for portability

2. **Input Decks:**
   - **Variant A (STATEV-only):** `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp`
     - Uses SDVINI initialization only
     - No stress initialization (stress recalculated from strain)
     - Purpose: Test SDVINI mechanism and quantify stress effect
   - **Variant B (STATEV+Stress):** `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp`
     - Uses SDVINI + *INITIAL CONDITIONS, TYPE=STRESS
     - Residual stress S11 = 335.577 MPa from cycle-19
     - Purpose: Test full state injection and validate cycle-skip core

3. **Batch Scripts:**
   - `run_stage4b_statev_only.bat` — Runs Variant A
   - `run_stage4b_statev_stress.bat` — Runs Variant B

4. **Documentation:**
   - `STAGE4B_EXACT_STATE_INJECTION_DECK_PREP_REPORT.md` — Complete test specification and run instructions

**Key Design Decisions:**

- **One-cycle continuation:** Both decks run exactly one cycle (time 0 to 1.0 s) with same amplitude profile as baseline
- **INC=1000:** Increment limit ensures ~1000 steps per cycle (DMAX ≈ 0.001 s)
- **Uniaxial residual stress:** Cycle-19 extracted stress is uniaxial (S11 only); off-diagonal components are machine zero
- **SDVINI hardcoded:** Cycle-19 values embedded directly in SDVINI; no CSV file dependency at runtime

**Expected Outcomes:**

| Test | Expected Result | Success Criterion |
|------|---|---|
| Variant A | Completes successfully; STATEV evolves; differs from cycle-20 by 1-3% | < 30 min runtime; STATEV1 < 0.142 at end |
| Variant B | Completes successfully; STATEV matches cycle-20 within 0.5% | < 30 min runtime; STATEV1 ≈ 0.142 ± 0.0007 |

**Success Implications:**

If Variant B matches explicit cycle-20:
- SDVINI initialization works correctly ✓
- Abaqus *INITIAL CONDITIONS for stress works ✓
- Exact-state injection is mechanically sound ✓
- Cycle-skipping validation passes ✓
- Ready for Level-3 predicted cycle-jump tests ✓

---

## Lessons Learned

1. **SDV Field Structure:** ODB stores individual SDV fields (SDV1, ..., SDV15), not composites. Extraction must query each field separately.

2. **Frame Timing:** Time values in ODB frames may have small floating-point errors. Nearest-frame search with tolerance is more robust than exact time matching.

3. **Residual Stress Criticality:** For accurate restart, both STATEV and stress must be injected. Omitting stress leads to physically inconsistent initial conditions.

4. **Integration Averaging:** Averaging over all integration points is the standard approach for ODB extraction. User-specified element sets can be added if region-specific averaging is needed.

---

## Files Referenced

| File | Purpose |
|------|---------|
| `runs/chaboche_umat/prepare_stage4a_exact_state_injection_data.py` | Extraction script (ODB→CSV) |
| `runs/chaboche_umat/chaboche_vp_v1_cyclic_eps005_20cycles.odb` | 20-cycle baseline ODB (source for extraction) |
| `runs/chaboche_umat/stage4_injected_cycle_jump/*.csv` | Extracted state files |
| `runs/chaboche_umat/chaboche_v1_full_statev_cycle_history.csv` | Pre-extracted cycle history (CSV fallback) |

---

**Report Last Updated:** 9 May 2026
