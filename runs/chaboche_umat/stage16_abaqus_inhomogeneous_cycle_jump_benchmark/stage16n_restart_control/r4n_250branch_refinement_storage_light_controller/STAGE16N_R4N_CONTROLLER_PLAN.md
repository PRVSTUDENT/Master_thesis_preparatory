# Stage 16N-R4N 250-Branch Refinement Storage-Light Controller Plan

## Purpose

R4N follows the R4M target-270 pass and does not return to the old retained R1A/R1B source packages. It regenerates one complete cycle-250 source package in scratch, then tests additional true-jump targets sequentially to bracket the practical 250-branch jump limit.

## Sequence

1. Regenerate `stage16n_r1b_restart_ref_250cycles` in scratch.
2. Require the full source package: `.odb`, `.stt`, `.res`, `.mdl`, `.prt`, `.sim`, `.sta`.
3. Extract exact cycle-100 and cycle-250 source states from the regenerated ODB.
4. Run target275: jump 250 -> 275, continue 276 -> 500.
5. If target275 passes, run target280: jump 250 -> 280, continue 281 -> 500.
6. If target280 passes and walltime remains, run optional target285: jump 250 -> 285, continue 286 -> 500.
7. If any target reviews/fails or hits setup/I/O failure, stop escalation and keep diagnostics only.

## Storage Rules

- Abaqus runs only in scratch.
- No heavy copy-back to `/home`.
- Continuation decks use `*RESTART, READ` only; no continuation `*RESTART, WRITE`.
- Copy back only `.md`, `.csv`, `.txt`, small `.log`, PBS stdout, qstat reports, and `_logs/`.
- Delete target heavy files after each classification.
- Delete regenerated source heavy files at final controller cleanup unless a future manifest explicitly records a retention reason.

## Resources

- Queue: `entryq`
- Cores: 16
- Memory: 90 GB
- Walltime: 24 h

## Decision Rule

- target275 pass and target280 pass: validated target advances from 270 to 280.
- target275 pass and target280 review/fail: practical boundary is between 275 and 280.
- target275 review/fail: practical boundary is between 270 and 275.
- setup/I/O failure: not scientific; fix controller and rerun a cheap diagnostic.

## Hard Blocks

- Do not run R4J9/R4J10.
- Do not run any 505-branch job.
- Do not use old incomplete retained R1A/R1B restart packages.
- Do not retain the regenerated source `.stt` or `.odb` after classification without an explicit heavy-retention manifest entry.
