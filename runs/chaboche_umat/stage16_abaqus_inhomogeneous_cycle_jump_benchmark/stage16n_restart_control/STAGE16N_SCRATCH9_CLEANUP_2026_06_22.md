# Stage 16N Scratch9 Cleanup, 2026-06-22

## Reason

The HPC service desk ticket `2026061152000911` reported that weekend jobs may have crashed because shared scratch was full and noted that account `pr21vyci` occupied about 25 TB. No new solver jobs were submitted during this cleanup.

## Pre-Cleanup State

- Queue check: `qstat -u pr21vyci` showed no active jobs.
- `/scratch9`: 33T total, 28T used, 4.7T free, 86% used.
- `/scratch9/pr21vyci`: about 24T.

Largest contributors before deletion:

- `/scratch9/pr21vyci/home_offload`: about 15T.
- `/scratch9/pr21vyci/stage16n_r4ir`: about 2.7T.
- `/scratch9/pr21vyci/stage16n_r4i`: about 2.2T.
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j_next_refine`: about 1.1T.
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j_branch_refine`: about 1.1T.
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j_v2`: about 844G.
- `/scratch9/pr21vyci/stage16n_r4k/R4K1_250branch_controller`: about 526G.

## Deleted Targets

Deleted one explicit folder at a time:

- `/scratch9/pr21vyci/stage16n_r4i`
- `/scratch9/pr21vyci/stage16n_r4ir`
- `/scratch9/pr21vyci/stage16n_r4k/R4K1_250branch_controller`
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j_next_refine`
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j_branch_refine`
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j_v2`
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4j`
- `/scratch9/pr21vyci/home_offload/20260618_085426`
- `/scratch9/pr21vyci/home_offload/master_thesis`
- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases`
- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_exact_overwrite_cases`
- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/native_restart_cases`

Deletion logs on HPC:

- `/home/pr21vyci/stage16n_scratch9_cleanup_delete_20260622_130954.txt`
- `/home/pr21vyci/stage16n_scratch9_home_offload_cleanup_20260622_131621.txt`

## Protected / Preserved

Preserved for the 505-branch provenance review:

- `/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls`
- The R4E2 candidate source under that tree:
  `stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source`

Preserved restart-reference offload folders:

- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles`
- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles`

## Final State

Final check on 2026-06-22:

- `qstat -u pr21vyci`: no active jobs.
- `/scratch9`: 33T total, 20T used, 13T free, 61% used.
- `/scratch9/pr21vyci`: about 2.7T.

Remaining largest account-owned scratch areas:

- `/scratch9/pr21vyci/home_offload`: about 1.6T, mostly preserved R1A/R1B restart references.
- `/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls`: about 1.1T, protected for R4E2/505 provenance review.

## Scientific / Operational Notes

- R4K1 remains a scientific pass: zero comparison error at cycle 500.
- `Stageout_status=1` for R4K1 is recorded as an infrastructure/stage-out warning, not a scientific failure, because the lightweight comparison evidence was recovered, uploaded, and shows zero error.
- Do not submit R4J9/R4J10.
- Do not start new solver jobs until the R4E2 candidate provenance review and resource-calibration plan are explicit.

Service-desk reply value: `/scratch9/pr21vyci` is now approximately `2.7T`.
