# Stage 16N-R4P Result

Status: corrected guarded resubmission active.

Batch: `R4P_boundary_reproducibility_and_diagnostics`

Prepared on: 2026-06-28 Europe/Berlin

First submitted on: 2026-06-28 06:13:35 CEST

Corrected resubmission: 2026-06-28 06:21:04 CEST

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

## Submission Status

The first guarded submission produced PBS jobs `1358943.mmaster02` through `1358950.mmaster02`, but all eight finished immediately with `Exit_status=127` and `Stageout_status=1`. PBS walltime was 0--2 s per job, so this is a launch/staging infrastructure failure, not an Abaqus solve and not a scientific result.

The PBS stdout files reported:

`bash: run_stage16n_r4p_boundary_reproducibility_and_diagnostics_job_hpc.sh: Datei oder Verzeichnis nicht gefunden`

Diagnosis: the PBS wrappers resolved `REPO_ROOT` incorrectly when `PBS_O_WORKDIR` was the R4P case directory. That created an empty home-side R4P directory and rsynced no controller scripts into scratch. The wrappers have been patched to climb from `PBS_O_WORKDIR` to the real repository root, prefer the clean scratch clone when needed, and fail explicitly if `HOME_CASE_DIR` is missing before scratch staging.

Corrected guarded resubmission was completed after the wrapper fix. The corrected qstat snapshot showed A1 (`1358951.mmaster02`) and B1 (`1358952.mmaster02`) queued, with A2/B2/A3/B3/A4/B4 held by dependencies. No corrected R4P scientific result is available yet.

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
