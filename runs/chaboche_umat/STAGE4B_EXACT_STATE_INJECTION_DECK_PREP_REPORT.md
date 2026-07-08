# Stage 4B — Exact-State Injection Deck Preparation Report

**Date:** May 9, 2026  
**Prepared by:** Copilot Agent  
**Purpose:** Create and document SDVINI-based injected continuation test decks for cycle-jump validation

---

## Overview

**Objective:** Validate the core cycle-skipping mechanism by testing exact-state injection from cycle-19 to cycle-20.

**Scope:** Two test variants:
1. **STATEV-only (Variant A):** Tests SDVINI subroutine alone (no stress init)
2. **STATEV+Stress (Variant B):** Tests full state injection (SDVINI + *INITIAL CONDITIONS)

**Method:** Extract the exact cycle-19 averaged STATEV and stress from the validated 20-cycle ODB, initialize them in two continuation decks, run one-cycle completions, and compare results against the explicit cycle-20 baseline.

---

## Input Data (from Stage 4A.1)

**Source:** `chaboche_vp_v1_cyclic_eps005_20cycles.odb` (20-cycle explicit baseline)

**Cycle-19 State (Frame time: 18.990257 s, error: 9.7 ms):**

| Variable | Value | Unit | Description |
|----------|-------|------|-------------|
| STATEV1 | 0.134855 | - | Accumulated viscoplastic strain |
| STATEV2..4 | -85.89, 42.95, 42.95 | MPa | Backstress components (X) |
| STATEV5..7 | ~0 (10⁻¹⁵) | - | Negligible (hydrostatic) |
| STATEV8..10 | -0.00179, 0.000896, 0.000896 | - | Viscoplastic strain components (Ep) |
| STATEV11..13 | ~0 (10⁻¹⁹) | - | Negligible |
| STATEV14 | 1.34401 | MPa | Isotropic hardening (RISO) |
| STATEV15 | 0.0 | - | Incremental plastic strain (reset) |
| **S11** | **335.577** | **MPa** | **Residual uniaxial stress** |
| S22, S33, S12, S13, S23 | ~0 (10⁻¹⁵) | MPa | Negligible (uniaxial loading) |

---

## Test Infrastructure

### UMAT + SDVINI Subroutine

**File:** `umat_chaboche_v1_with_sdvini.f`

**Contents:**
- Original Chaboche-v1 UMAT subroutine (no modifications)
- New SDVINI subroutine for cycle-19 state initialization

**SDVINI Function:**
```fortran
SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,ORNT,LAYER,KSPT)
  ! Initialize STATEV from cycle-19 averaged values
  STATEV(1) = 0.13485494256019592D0  ! STATEV1 (accumulated viscoplastic strain)
  STATEV(2) = -85.89347076416016D0   ! STATEV2 (backstress X1)
  STATEV(3) = 42.94673538208008D0    ! STATEV3 (backstress X2)
  ... [all 15 variables initialized]
  STATEV(15) = 0.0D0                 ! STATEV15 (reset for new continuation)
END SUBROUTINE
```

**Note:** SDVINI is called at the start of the analysis. It initializes all state variables uniformly across the model.

---

### Test Variant A: STATEV-only Injection

**File:** `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp`

**Configuration:**
- Geometry: Same 10×2×2 block (single C3D8 element)
- Material: Chaboche-v1 (same properties as baseline)
- Loading: One cycle, 0 → +0.05 → -0.05 → 0 strain
- Time: 0.0 to 1.0 s (same time scale as baseline)
- User subroutine: `umat_chaboche_v1_with_sdvini.f`
- Increment control: INC=1000 (DMAX ≈ 0.001 s)

**Stress Initialization:** **NONE** (stress will be calculated from strain)

**Purpose:** Test if SDVINI mechanism works and quantify stress effect on continuation

**Expected Result:**
- Simulation completes without errors
- STATEV evolves from initialized cycle-19 values during the continuation
- Final STATEV differs from explicit cycle-20 due to missing stress state
- Establishes baseline for stress-effect quantification

---

### Test Variant B: STATEV+Stress Injection

**File:** `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp`

**Configuration:**
- Geometry, material, loading, time: Identical to Variant A
- User subroutine: `umat_chaboche_v1_with_sdvini.f`

**Stress Initialization:**
```
*INITIAL CONDITIONS, TYPE=STRESS
BLOCK_INST.BLOCK.1, 335.5768737792969, 0.0, 0.0, 0.0, 0.0, 0.0
```
- S11 = 335.577 MPa (residual tension from cycle-19)
- S22, S33, S12, S13, S23 = 0.0 (uniaxial state)

**Purpose:** Test full state injection and validate cycle-skip core mechanism

**Expected Result:**
- Simulation completes without errors
- Final STATEV closely matches explicit cycle-20 (within ~0.5% tolerance)
- Validates that exact-state injection reproduces the explicit continuation
- Confirms cycle-skipping is mechanically sound

---

## Run Instructions

### Variant A: STATEV-only Test

**Command:**
```batch
cd D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat
abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp ^
        user=umat_chaboche_v1_with_sdvini.f ^
        interactive ask_delete=OFF scratch=cleanup
```

**Batch Script:** `run_stage4b_statev_only.bat`

**Outputs:**
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.odb`
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.msg` (messages)
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.sta` (status)

### Variant B: STATEV+Stress Test

**Command:**
```batch
cd D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat
abaqus job=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress ^
        input=chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp ^
        user=umat_chaboche_v1_with_sdvini.f ^
        interactive ask_delete=OFF scratch=cleanup
```

**Batch Script:** `run_stage4b_statev_stress.bat`

**Outputs:**
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.odb`
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.msg`
- `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.sta`

---

## Expected Outcomes & Validation

### Success Criteria

✅ **Variant A (STATEV-only) passes if:**
1. Abaqus completes the job without fatal errors
2. ODB contains all 1000+ frames
3. STATEV1 evolves from 0.134855 (initial) during the cycle
4. Final STATEV1 value is lower than explicit cycle-20 (0.142026) — indicates stress effect

✅ **Variant B (STATEV+Stress) passes if:**
1. Abaqus completes the job without fatal errors
2. ODB contains all 1000+ frames
3. Final STATEV1 is within ±0.5% of explicit cycle-20 (target: 0.142026 ± 0.0007)
4. Final S11 is within ±1% of explicit cycle-20 (target: 376.43 ± 3.76 MPa)

### Failure Modes & Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|-----------|
| Abaqus error "SDVINI not found" | User subroutine file not linked | Verify `-user=` path is correct and file exists |
| "SDV index out of range" | NSTATV mismatch | Check DEPVAR=15 in material definition |
| "Element deleted" early | Stress initialization causes divergence | Verify stress values are physically reasonable |
| Large difference from cycle-20 | Stress state mismatch | Expected for Variant A; check Variant B for full injection |

---

## Comparison & Analysis (Post-Run)

After both tests complete, extract cycle-20 results from both ODBs and the explicit baseline:

1. **Extract cycle-end STATEV1** from each ODB
2. **Compare Variant B to explicit cycle-20** — should match within 0.5%
3. **Compare Variant A to explicit cycle-20** — expected to differ by 1-3% (stress effect)
4. **Plot STATEV1 vs cycle** for all three (Variant A, Variant B, explicit) to visualize injection accuracy

---

## Physical Interpretation

**Why stress matters:**
- Residual stress (S11 = 335.577 MPa) at cycle-19 represents elastic energy stored in the material
- This energy influences plastic flow during the subsequent cycle via the backstress-stress interaction
- Omitting stress (Variant A) effectively "erases" this energy, leading to different plastic flow
- Including stress (Variant B) preserves the material's state and ensures accurate continuation

**Why this validates cycle-skipping:**
- If Variant B matches explicit cycle-20, we confirm that:
  1. SDVINI mechanism works correctly
  2. Abaqus *INITIAL CONDITIONS for stress works as expected
  3. The exact-state injection produces physically correct results
  4. Cycle-skipping via state injection is mechanically sound
- This is a prerequisite for Level-3 predicted cycle-jump testing

---

## Files Created

| File | Purpose |
|------|---------|
| `umat_chaboche_v1_with_sdvini.f` | UMAT + SDVINI subroutine (combined) |
| `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.inp` | Variant A input deck (STATEV-only) |
| `chaboche_stage4b_cycle19_exact_to_cycle20_statev_stress.inp` | Variant B input deck (full state injection) |
| `run_stage4b_statev_only.bat` | Batch script for Variant A |
| `run_stage4b_statev_stress.bat` | Batch script for Variant B |

---

## Next Steps

1. **Run Variant A & B** using batch scripts
2. **Wait for Abaqus completion** (each should take 10-30 seconds on modern hardware)
3. **Extract cycle-end results** from both ODBs (STATEV1, S11, S22, etc.)
4. **Compare results** against explicit cycle-20 baseline
5. **Document findings** in Stage 4B results report
6. **If successful**, proceed to Level-3 predicted cycle-jump testing (Stage 4C)

---

**Report Status:** Ready for testing  
**Last Updated:** May 9, 2026
