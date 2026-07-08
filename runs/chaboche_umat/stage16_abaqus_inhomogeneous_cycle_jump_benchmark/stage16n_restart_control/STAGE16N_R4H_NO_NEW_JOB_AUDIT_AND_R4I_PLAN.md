# Stage 16N R4H No-New-Job Audit and R4I Plan

Updated: 2026-06-19.

## R4H interpretation

R4H isolates the active problem to restart records produced by short source-split jobs.

| Case family | Result | Meaning |
|---|---|---|
| R4H1/R4H3/R4H5 long replay | pass, zero error | Restart records produced by long restarted replay are clean. |
| R4H2/R4H4/R4H6 short source split | fail/review | Short source-split restart records are not equivalent to same-cycle long-replay restart records. |

The issue is not direct Abaqus restart, endpoint comparison, or simply restarting from a final source step. R4H2, R4H4, and R4H6 used interior restart targets and still reproduced the bad source-split behavior.

## Cheap audit findings

- The generated R4H source decks use the same nominal cycle-step load pattern as the clean continuation decks: `*STATIC 0.005, 1.0, 1.0E-08, 0.025`, `*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE`, `RIGHT_EDGE, 1, 1, 0.10`, and history output for `U1, RF1`.
- R4H short-source decks differ from the clean long-replay continuation pattern by writing restart output every source step and by requesting field output at both the restart target and source end.
- The source-target local-state audit is blocked in the retained lightweight evidence: R4H2/R4H4/R4H6 source selected-cycle local-state CSVs report `no selected field-output frames found`. Therefore, the existing lightweight CSVs cannot prove whether the short-source ODB already differs at the target cycle.
- Continuation classification is decisive anyway: long-replay restart records at cycles 270, 280, and 505 pass exactly; short-source restart records at the same cycles do not.

## R4I diagnostic batch

Prepare and submit exactly four cases:

| Case | Source solve | Restart | Continuation | Expected first solved step | Purpose |
|---|---|---|---|---|---|
| R4I1 | 250 -> 281, deck-clone style | 280 | 281 -> 500 | `CYCLE_0281` | Test whether R4H2 failed because its source deck shape differed from clean long replay. |
| R4I2 | 250 -> 300, buffered generated style | 280 | 281 -> 500 | `CYCLE_0281` | Test whether one extra post-target cycle is insufficient. |
| R4I3 | 250 -> 300, buffered generated style | 270 | 271 -> 500 | `CYCLE_0271` | Repeat the buffer test on the R4H4/R4G4 branch. |
| R4I4 | 500 -> 525, buffered generated style | 505 | 506 -> 750 | `CYCLE_0506` | Test whether the 500 branch is repaired by a buffer. |

Use production resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`, queue `teachingq`. Submit through `qsub_abq` only after the storage gate passes.

## Decision table

- R4I1 pass, R4I2 pass: R4H generator/deck construction was the issue; fix the short-source generator and rerun controls.
- R4I1 pass, R4I2 fail: clean deck cloning works but buffered generated deck still differs; focus on generated source deck differences.
- R4I1 fail, R4I2 pass: short source restart needs a larger post-target buffer; adopt buffered source-split restart strategy.
- R4I1 fail, R4I2 fail: short source-split restart is unreliable for the 250 -> 280 branch; stop using it as a cycle-jump foundation.
- R4I4 pass: the 500 branch can be repaired with buffered source strategy.
- R4I4 review/fail: the 500 branch also has source-split inconsistency.

R4J9/R4J10 remain blocked until R4I is classified.
