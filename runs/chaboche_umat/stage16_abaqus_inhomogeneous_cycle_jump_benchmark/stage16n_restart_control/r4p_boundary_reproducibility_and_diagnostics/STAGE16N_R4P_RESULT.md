# Stage 16N-R4P Result

Status: corrected guarded resubmission completed and classified.

Batch: `R4P_boundary_reproducibility_and_diagnostics`

Prepared on: 2026-06-28 Europe/Berlin

First submitted on: 2026-06-28 06:13:35 CEST

Corrected resubmission: 2026-06-28 06:21:04 CEST

Final classification: 2026-07-01 Europe/Berlin

Storage gate: `/scratch9/pr21vyci` was 2.862T, below the 5T abort threshold.

Guarded wrapper: `/home/pr21vyci/bin/qsub_abq_guarded`

## Scientific Basis

R4P is a boundary reproducibility and diagnostics batch for the 250-branch true-jump edge. The current evidence is:

- R4M target270 passed.
- R4O target271 passed.
- R4O target272 failed.
- R4O target274 failed.

Therefore the current 250-branch true-jump boundary is between target271 and target272.

## Submitted Queue

Eight PBS jobs were prepared in two afterany dependency chains. Only A1 and B1 should be runnable at initial submission, so no more than two R4P jobs are active at the same time.

| chain | order | case | target | mode | cores | PBS job | dependency |
| --- | ---: | --- | ---: | --- | ---: | --- | --- |
| A | 1 | `R4P_A1_repeat_target271` | 271 | repeat true-jump | 16 | `1358951.mmaster02` | none |
| A | 2 | `R4P_A2_repeat_target272` | 272 | repeat true-jump | 16 | `1358953.mmaster02` | afterany `1358951.mmaster02` |
| A | 3 | `R4P_A3_target272_exact_native_control` | 272 | exact/native control | 16 | `1358955.mmaster02` | afterany `1358953.mmaster02` |
| A | 4 | `R4P_A4_target272_failure_diagnostics` | 272 | diagnostic rerun | 16 | `1358957.mmaster02` | afterany `1358955.mmaster02` |
| B | 1 | `R4P_B1_repeat_target270` | 270 | repeat true-jump | 16 | `1358952.mmaster02` | none |
| B | 2 | `R4P_B2_target271_diagnostics` | 271 | diagnostic rerun | 16 | `1358954.mmaster02` | afterany `1358952.mmaster02` |
| B | 3 | `R4P_B3_8core_target271_calibration` | 271 | 8-core calibration | 8 | `1358956.mmaster02` | afterany `1358954.mmaster02` |
| B | 4 | `R4P_B4_8core_target272_calibration` | 272 | 8-core calibration | 8 | `1358958.mmaster02` | afterany `1358956.mmaster02` |

## Final Result

All corrected R4P jobs `1358951.mmaster02` through `1358958.mmaster02` finished with `Exit_status=0` and `Stageout_status=1`. The stage-out flag is treated as an infrastructure warning because the lightweight evidence was recovered in the case folders. No corrected R4P job remained active in `qstat` on 2026-07-01 10:39 CEST.

| case | PBS job | mode | target | endpoint | classification | max global % | max primary-local % | diagnostic S11 % |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| `R4P_B1_repeat_target270` | `1358952.mmaster02` | repeat true-jump | 270 | 500 | pass | 0.39923577 | 3.9830029 | 0.1398007 |
| `R4P_A1_repeat_target271` | `1358951.mmaster02` | repeat true-jump | 271 | 500 | pass | 0.00016431012 | 4.1785861 | 0.00022768842 |
| `R4P_B2_target271_diagnostics` | `1358954.mmaster02` | diagnostic repeat | 271 | 500 | pass | 0.00016431012 | 4.1785861 | 0.00022768842 |
| `R4P_B3_8core_target271_calibration` | `1358956.mmaster02` | 8-core calibration | 271 | 500 | pass | 0.00016431012 | 4.1785861 | 0.00022768842 |
| `R4P_A2_repeat_target272` | `1358953.mmaster02` | repeat true-jump | 272 | 500 | fail | 1.8126719 | 14.385057 | 9.4271837 |
| `R4P_A4_target272_failure_diagnostics` | `1358957.mmaster02` | diagnostic repeat | 272 | 500 | fail | 1.8126719 | 14.385057 | 9.4271837 |
| `R4P_B4_8core_target272_calibration` | `1358958.mmaster02` | 8-core calibration | 272 | 500 | fail | 1.8126719 | 14.385057 | 9.4271837 |
| `R4P_A3_target272_exact_native_control` | `1358955.mmaster02` | exact/native control | 272 | 500 | pass | 0 | 0 | 0 |

Scientific interpretation:

- Target270 remains a pass and reproduces the R4M metric signature.
- Target271 passed in three corrected R4P runs, including the 8-core calibration; it reproduces the R4O target271 metrics exactly.
- Target272 failed in three corrected true-jump runs, including the 8-core calibration; it reproduces the R4O target272 failure metrics exactly.
- The A3 exact/native target272 control passed with zero comparison error after reading the native source at `restart_step=272`, `restart_inc=57`. Therefore the target272 failure is not an Abaqus native restart-continuity failure; it is the extrapolated true-jump state-prediction boundary.
- The accepted 250-branch storage-light true-jump boundary remains target271. Target272 is rejected. R4J9/R4J10, 505-branch continuation, and broader target273/275/276/280/285 progression remain blocked unless a new explicit gated controller is defined.

Runtime/accounting summary:

- 16-core jobs used roughly 6.82--7.37 average active cores from `resources_used.cpupercent` and 39:37:49--52:07:05 CPU time over 07:29:38--09:09:05 walltime.
- 8-core jobs used roughly 4.80--4.87 average active cores, with `1358956` at 35:11:55 CPU over 09:50:27 walltime and `1358958` at 30:47:55 CPU over 08:35:10 walltime.
- Full PBS accounting is stored in `qstat_r4p_1358951_1358958_finished_full.txt`.

## Submission Status

The first guarded submission produced PBS jobs `1358943.mmaster02` through `1358950.mmaster02`, but all eight finished immediately with `Exit_status=127` and `Stageout_status=1`. PBS walltime was 0--2 s per job, so this is a launch/staging infrastructure failure, not an Abaqus solve and not a scientific result.

The PBS stdout files reported:

`bash: run_stage16n_r4p_boundary_reproducibility_and_diagnostics_job_hpc.sh: Datei oder Verzeichnis nicht gefunden`

Diagnosis: the PBS wrappers resolved `REPO_ROOT` incorrectly when `PBS_O_WORKDIR` was the R4P case directory. That created an empty home-side R4P directory and rsynced no controller scripts into scratch. The wrappers have been patched to climb from `PBS_O_WORKDIR` to the real repository root, prefer the clean scratch clone when needed, and fail explicitly if `HOME_CASE_DIR` is missing before scratch staging.

Corrected guarded resubmission was completed after the wrapper fix. The corrected jobs are now finished and classified as described above.

Submitted-jobs record:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/STAGE16N_R4P_SUBMITTED_JOBS.txt`

Corrected resubmission record:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/STAGE16N_R4P_RESUBMITTED_JOBS.txt`

Storage/submission evidence:

- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/_submission_logs/r4p_storage_gate_df.txt`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/_submission_logs/r4p_storage_gate_scratch9_user.txt`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/_submission_logs/*_qsub_guarded.log`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/qstat_r4p_after_submission_verify.txt`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/qstat_r4p_after_corrected_resubmission.txt`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/qstat_r4p_1358951_1358958_finished_full.txt`
