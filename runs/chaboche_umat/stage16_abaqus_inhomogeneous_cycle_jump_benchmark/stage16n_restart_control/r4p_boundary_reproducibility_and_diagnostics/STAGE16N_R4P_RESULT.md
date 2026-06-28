# Stage 16N-R4P Result

Status: prepared locally, pending guarded HPC submission.

Batch: `R4P_boundary_reproducibility_and_diagnostics`

Prepared on: 2026-06-28 Europe/Berlin

## Scientific Basis

R4P is a boundary reproducibility and diagnostics batch for the 250-branch true-jump edge. The current evidence is:

- R4M target270 passed.
- R4O target271 passed.
- R4O target272 failed.
- R4O target274 failed.

Therefore the current 250-branch true-jump boundary is between target271 and target272.

## Prepared Queue

Eight PBS jobs were prepared in two afterany dependency chains. Only A1 and B1 should be runnable at initial submission, so no more than two R4P jobs are active at the same time.

| chain | order | case | target | mode | cores | dependency |
| --- | ---: | --- | ---: | --- | ---: | --- |
| A | 1 | `R4P_A1_repeat_target271` | 271 | repeat true-jump | 16 | none |
| A | 2 | `R4P_A2_repeat_target272` | 272 | repeat true-jump | 16 | afterany A1 |
| A | 3 | `R4P_A3_target272_exact_native_control` | 272 | exact/native control | 16 | afterany A2 |
| A | 4 | `R4P_A4_target272_failure_diagnostics` | 272 | diagnostic rerun | 16 | afterany A3 |
| B | 1 | `R4P_B1_repeat_target270` | 270 | repeat true-jump | 16 | none |
| B | 2 | `R4P_B2_target271_diagnostics` | 271 | diagnostic rerun | 16 | afterany B1 |
| B | 3 | `R4P_B3_8core_target271_calibration` | 271 | 8-core calibration | 8 | afterany B2 |
| B | 4 | `R4P_B4_8core_target272_calibration` | 272 | 8-core calibration | 8 | afterany B3 |

## Submission Status

Pending. This file must be updated with PBS job IDs after guarded submission from the clean HPC clone.

Expected submitted-jobs record:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4p_boundary_reproducibility_and_diagnostics/STAGE16N_R4P_SUBMITTED_JOBS.txt`

