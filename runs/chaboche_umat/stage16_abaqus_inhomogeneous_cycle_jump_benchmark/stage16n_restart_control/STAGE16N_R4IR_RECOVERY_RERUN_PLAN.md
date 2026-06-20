# Stage 16N R4I-R Recovery Rerun Plan

Updated: 2026-06-20.

## Reason for rerun

R4I cannot be classified from the first submission because all four Abaqus source solves, datachecks, continuations, and extraction steps completed, but comparison failed after extraction because the remote reference CSV paths were missing. The extracted R4I metrics and selected-cycle CSVs were not preserved in `/home`, and the scratch run directories were no longer recoverable.

No scratch deletion or extraction cleanup is needed now. The latest inventory showed `/scratch/pr21vyci` at only 48K, with an inventory header only and empty delete-candidate/keep lists. The cluster-wide `/scratch` usage is not caused by the current Stage 16N files.

## Recovery cases

| Case | Source solve | Restart | Continuation | First solved cycle | Purpose |
|---|---|---|---|---|---|
| R4I-R1 | 250--281 deck-clone style | 280 | 281--500 | `CYCLE_0281` | Test whether cloned/truncated clean deck shape fixes the R4H2/R4I1 branch. |
| R4I-R2 | 250--300 buffered generated style | 280 | 281--500 | `CYCLE_0281` | Test whether a larger post-target buffer repairs restart from 280. |
| R4I-R3 | 250--300 buffered generated style | 270 | 271--500 | `CYCLE_0271` | Test whether a larger post-target buffer repairs restart from 270. |
| R4I-R4 | 500--525 buffered generated style | 505 | 506--750 | `CYCLE_0506` | Test whether a larger post-target buffer repairs the 500 -> 505 branch. |

## Hardening changes

- Generated a separate recovery root: `r4ir_restart_source_buffer_recovery/`.
- Generated a separate dispatcher: `submit_stage16n_r4ir_restart_source_buffer_recovery_case.sh`.
- Switched PBS queue to `entryq`.
- Kept Stage 16N resource policy: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`, maximum intended active use `2 x 16` cores.
- Staged absolute reference CSVs into the scratch case directory before comparison:
  - `reference_1000_cycle_metrics.csv`
  - `reference_1000_selected_cycle_local_states.csv`
  - `reference_parallel_cycle_metrics.csv`
  - `reference_parallel_selected_cycle_local_states.csv`
- Added a `copy_lightweight_evidence` function in the runner and call it immediately after continuation extraction, before comparison can abort.
- Kept scratch directories after the run with `KEEP_SCRATCH=1`.
- Continued to exclude heavy Abaqus files from copy-back: `.odb`, `.stt`, `.res`, `.sim`, `.mdl`, `.prt`, `.dat`, `.msg`, and related generated binary/state files.

## Submission gate

Before submission, run:

```bash
abaqus_storage_gate
qstat -u $USER
df -h /home /scratch
du -sh /home/$USER
```

Submit only through `qsub_abq` or `~/bin/qsub_abq_guarded`; do not use raw `qsub`.

## Decision table

- R4I-R1 pass: cloned/truncated clean deck fixes the R4H2 problem; the earlier short-source generator was not equivalent.
- R4I-R1 fail: short-source restart itself remains unreliable.
- R4I-R2 pass: a larger post-target buffer can repair restart from 280.
- R4I-R3 pass: a larger post-target buffer can repair restart from 270.
- R4I-R4 pass: a larger post-target buffer can repair the 500 -> 505 branch.
- If all still fail/review: stop using short source-split restart as a cycle-jump foundation.

R4J9/R4J10 remain blocked until these recovery comparisons exist and are classified.
