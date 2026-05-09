# Stage 4A — Exact-State Injection Preparation Report

Prepared: May 9, 2026

Purpose
- Prepare exact cycle-19 STATEV and stress averages for an injection-mechanics test.

Scope
- This is an injection-mechanics preparation step only. It does not predict a jump.
- It is intended to verify that Abaqus can be initialized with the exact explicit
  cycle-19 STATEV (+ stress) and continue for one more cycle (cycle 20).
- No UMAT changes, no damage model, and no input-deck modification are performed.

Inputs
- runs/chaboche_umat/chaboche_v1_full_statev_cycle_history.csv (averaged integration-point history)

Outputs (created here)
- stage4_injected_cycle_jump/cycle19_exact_statev_for_injection.csv
- stage4_injected_cycle_jump/cycle19_exact_stress_for_injection.csv

Summary of extraction method
- The extraction script `prepare_stage4a_exact_state_injection_data.py` prefers
  to use Abaqus `odbAccess` when available. For portability (outside Abaqus
  Python) it falls back to the precomputed CSV `chaboche_v1_full_statev_cycle_history.csv`.
- The CSV contains averaged `STATEV1_end`..`STATEV15_end` for each cycle; the
  script copies the cycle-19 values into the `cycle19_exact_statev_for_injection.csv` file.
- Stress averages were not present in the fallback CSV; the stress CSV contains
  placeholders and a note that these must be filled by running an ODB extraction
  under Abaqus Python if exact stress initialization is required.

How to use
1. Create an SDVINI-based restart deck that reads `cycle19_exact_statev_for_injection.csv` into SDVINI.
2. Initialize element stresses via `*INITIAL CONDITIONS, TYPE=STRESS` using the stress CSV,
   or extract and embed stresses in the restart step if your workflow supports that.
3. Run Abaqus for one cycle (cycle 19 -> 20) and compare the resulting SDV1 and stress field
   to the full explicit `cycle 20` reference.

Checks performed here
- Quick tabular comparison `STATEV1..15` cycle 19 vs cycle 20 is included in the local script output.

Next steps
- If the SDVINI + INITIAL STRESS continuation reproduces the full explicit cycle-20, proceed to
  prepare a predicted-cycle jump (Level-3A continuation): derive cycle-19 STATEV from cycle-10 data.
- If the continuation fails, debug initialization order, SDVINI feed, and initial stress specification.
