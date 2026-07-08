# Stage 16N-R4K Deck-Clone Controller Plan

Prepared on 2026-06-22 after the R4I-R source-split recovery diagnostics.

## Current classification

- Deck-clone/truncate is confirmed for `250 -> 270 -> 500` by R4I-R5 with zero comparison error.
- Deck-clone/truncate is confirmed for `250 -> 280 -> 500` by R4I-R1 with zero comparison error.
- Generated buffered source decks remain non-equivalent: R4I-R2 failed at restart 280, while R4I-R3 and R4I-R4 reproduced review-level signatures at restart 270 and 505.
- The `505 -> 750` deck-clone branch is scientifically unclassified. R4I-R6 failed during continuation `.stt` writing, and R4I-R6B failed earlier during source `.stt` writing.
- A 2026-06-22 scan found no valid lightweight-visible existing cycle-505 restart source under `/scratch9/pr21vyci`, `/scratch/pr21vyci`, or `/home/pr21vyci/master_thesis/Abaqus_trial`.

## Prepared controllers

### R4K1 250-branch controller

Path:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4k_deck_clone_controllers/R4K1_250branch_controller/`

PBS job name:

`stage16n_r4k_250branch_controller`

Purpose:

Run the deck-clone exact control `250 -> exact 280 -> 500` using a source deck cloned from the clean replay shape. The source solve writes restart records through cycle 281. The continuation deck reads the cycle-280 restart record and does not request continuation restart writes.

### R4K2 505-branch preflight/controller

Path:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4k_deck_clone_controllers/R4K2_505branch_controller/`

PBS job name:

`stage16n_r4k_505branch_controller`

Purpose:

Locate and validate an existing clean cycle-505 restart source before any Abaqus solve. If no valid source exists, stop before recreating the source `.stt` failure and write `R4K2_505_RESTART_SOURCE_PREFLIGHT.md` plus `STAGE16N_R4K_CASE_STATUS.md`.

## Shared controller behavior

- Request one node with 16 cores, 90 GB memory, and 24 h walltime.
- Run from scratch and copy back only lightweight evidence.
- Exclude heavy Abaqus products such as `.odb`, `.stt`, `.res`, `.sim`, `.mdl`, `.prt`, `.dat`, `.msg`, and solver state files from repository copy-back.
- Wrap major phases with `phase_time`, including timestamps, exit code, and `/usr/bin/time -v`.
- Install `trap copy_lightweight_evidence EXIT` so failed tasks still preserve logs and status notes.

## Gate logic

- If R4K1 passes, the `250 -> 280 -> 500` exact deck-clone control remains confirmed under the controller workflow.
- If R4K2 reports no valid 505 source, postpone or redesign the 500-branch source strategy instead of recreating the failing `.stt`.
- Keep R4J9/R4J10 blocked until R4K exact controls are resolved.

## Submission update

- `1350764.mmaster02`: R4K1 submitted through the guarded wrapper on 2026-06-22. It was still running at the latest inspection; the source solve had reached cycle 255.
- `1350767.mmaster02`: corrected R4K2 preflight submitted through the guarded wrapper on 2026-06-22 and finished with `Exit_status=0`.
- R4K2 found one large candidate source after excluding generated-buffer/source-split R4I and R4I-R families:

`/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source`

The candidate has a 4.9 GB `.stt` and a successful source `.sta` at cycle 505. Treat it as a review candidate, not yet as a validated deck-clone/truncate source.
