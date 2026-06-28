# Stage 16N-R4O Boundary Refinement Result

Checked: 2026-06-28 Europe/Berlin

## PBS accounting

All six R4O jobs finished with `Exit_status=0` and `Stageout_status=1`. Treat the stage-out flag as an infrastructure warning only, because the lightweight result evidence was recovered in the repository tree.

| Case | PBS job | Target | Walltime | CPU time | Average cores | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| R4O_A1_target271 | 1356502 | 271 | 11:18:58 | 50:40:50 | 4.48 / 16 | pass |
| R4O_B1_target274 | 1356503 | 274 | 10:53:52 | 50:11:39 | 4.61 / 16 | fail |
| R4O_A2_target272 | 1356504 | 272 | 09:43:31 | 50:32:43 | 5.20 / 16 | fail |
| R4O_A3_target273 | 1356505 | 273 | 00:00:04 | 00:00:01 | gated skip | skipped after A2 failed |
| R4O_B2_repeat275 | 1356506 | 275 | 00:00:04 | 00:00:01 | gated skip | skipped after B1 failed |
| R4O_B3_target276_guarded | 1356507 | 276 | 00:00:13 | 00:00:01 | gated skip | skipped after B2 had no comparison |

Full PBS history is stored in `qstat_r4o_1356502_1356507_finished_full.txt`.

## Scientific result

R4O refined the validated 250-branch storage-light source-regeneration path between the R4M target-270 pass and the R4N target-275 review.

| Case | Continuation | Status | Max global error (%) | Max primary local error (%) | Diagnostic S11 error (%) |
| --- | --- | --- | ---: | ---: | ---: |
| R4O_A1_target271 | 272 -> 500 | pass | 0.00016431012 | 4.1785861 | 0.00022768842 |
| R4O_A2_target272 | 273 -> 500 | fail | 1.8126719 | 14.385057 | 9.4271837 |
| R4O_B1_target274 | 275 -> 500 | fail | 0.46378221 | 13.495934 | 1.0204996 |

Interpretation: the 250-branch true-jump boundary is now bracketed tightly. Target 270 passed in R4M, target 271 passed in R4O, target 272 failed, and target 274 failed independently. Do not advance to target 273/275/276, target 280/285, broad true-jump batches, R4J9/R4J10, or the 505 branch without a new gated diagnostic/controller.

## Uploaded evidence

Important lightweight evidence is stored under this directory:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4o_250branch_boundary_refinement_queue/`

The uploaded payload includes case status markdown, case tables, comparison summary/details CSVs, cycle metrics, selected local-state/loop CSVs, small Abaqus tail files, storage logs, and the full R4O PBS accounting snapshot. Bulky scratch-only exact-state CSVs under `_source_state/` were intentionally not copied back or committed.
