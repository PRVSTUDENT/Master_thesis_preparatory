# Stage 16N R4Q4F--R4Q7F Feasibility Result

Checked: 2026-07-06 Europe/Berlin

## Summary

The explicit feasibility-only follow-up chain after the R4Q3 cycle1000 strict-gate accuracy miss has completed through cycle2000. All four jobs finished with `Exit_status=0`, wrote completed controller status files, and extracted the expected endpoint states.

This is feasibility evidence only. It does not validate accuracy beyond cycle1000 and does not widen the accepted 250-branch true-jump boundary beyond target271.

## PBS accounting

| Case | PBS job | Block | Final state | Walltime | CPU time | Host |
| --- | --- | --- | --- | --- | --- | --- |
| R4Q4F | `1363629.mmaster02` | source1000 -> target1021, solve 1022--1250 | `job_state=F`, `Exit_status=0`, `Stageout_status=1` | 11:32:59 | 10:41:48 | `mnode033/7` |
| R4Q5F | `1363630.mmaster02` | source1250 -> target1271, solve 1272--1500 | `job_state=F`, `Exit_status=0`, `Stageout_status=1` | 09:13:04 | 08:35:47 | `mnode008/0` |
| R4Q6F | `1363631.mmaster02` | source1500 -> target1521, solve 1522--1750 | `job_state=F`, `Exit_status=0`, `Stageout_status=1` | 09:34:51 | 08:36:21 | `mnode008/3` |
| R4Q7F | `1363633.mmaster02` | source1750 -> target1771, solve 1772--2000 | `job_state=F`, `Exit_status=0`, `Stageout_status=1` | 12:47:50 | 11:13:51 | `mnode001/0` |

`Stageout_status=1` is retained as an infrastructure warning, but the lightweight controller evidence was copied back and preserved.

## Controller classification

All four block summaries report `status=completed`, `classification_scope=feasibility_only_after_cycle1000_accuracy_fail`, `reference_available=no`, and `comparison_status=not_available`.

| Case | Restart point | Endpoint state | Detail |
| --- | --- | --- | --- |
| R4Q4F | `STEP=937`, `INC=63` | cycle1250 | `extraction=ok; cycle1250_state=ok` |
| R4Q5F | `STEP=1166`, `INC=63` | cycle1500 | `extraction=ok; cycle1500_state=ok` |
| R4Q6F | `STEP=1395`, `INC=63` | cycle1750 | `extraction=ok; cycle1750_state=ok` |
| R4Q7F | `STEP=1624`, `INC=57` | cycle2000 | `extraction=ok; cycle2000_state=ok` |

## Endpoint metrics

The copied endpoint cycle metrics are:

| Endpoint | RF1 max | RF1 min | RF1 mean | Loop area abs |
| --- | ---: | ---: | ---: | ---: |
| cycle1250 | 2908.24487305 | -3074.82762146 | 534.291372588 | 577.067685072 |
| cycle1500 | 2930.69926453 | -3018.15731049 | 241.990423641 | 567.880736397 |
| cycle1750 | 2970.01461029 | -3065.62748718 | 352.421058674 | 580.000236998 |
| cycle2000 | 2970.01576996 | -3065.62892914 | 352.421461661 | 580.000180464 |

## Important repo evidence

The lightweight result files are stored under:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4q_long_adaptive_chain_1cpu/`

Important copied files include:

- `R4Q4F_continue_from_cycle1000_1cpu_STATUS.txt`
- `R4Q4F_continue_from_cycle1000_1cpu_BLOCK_SUMMARY.csv`
- `R4Q4F_continue_from_cycle1000_1cpu_CONTROLLER.log`
- `R4Q5F_continue_from_cycle1250_1cpu_STATUS.txt`
- `R4Q5F_continue_from_cycle1250_1cpu_BLOCK_SUMMARY.csv`
- `R4Q5F_continue_from_cycle1250_1cpu_CONTROLLER.log`
- `R4Q6F_continue_from_cycle1500_1cpu_STATUS.txt`
- `R4Q6F_continue_from_cycle1500_1cpu_BLOCK_SUMMARY.csv`
- `R4Q6F_continue_from_cycle1500_1cpu_CONTROLLER.log`
- `R4Q7F_continue_from_cycle1750_1cpu_STATUS.txt`
- `R4Q7F_continue_from_cycle1750_1cpu_BLOCK_SUMMARY.csv`
- `R4Q7F_continue_from_cycle1750_1cpu_CONTROLLER.log`
- `qstat_r4q4f_1363629_finished_full.txt`
- `qstat_r4q5f_1363630_finished_full.txt`
- `qstat_r4q6f_1363631_finished_full.txt`
- `qstat_r4q7f_1363633_finished_full.txt`
- `qstat_r4q_f4_chain_after_finish_queue.txt`
- `stage16n_r4q4f_block04_1000_to_1021_solve_1022_to_1250_cycle_metrics.csv`
- `stage16n_r4q5f_block05_1250_to_1271_solve_1272_to_1500_cycle_metrics.csv`
- `stage16n_r4q6f_block06_1500_to_1521_solve_1522_to_1750_cycle_metrics.csv`
- `stage16n_r4q7f_block07_1750_to_1771_solve_1772_to_2000_cycle_metrics.csv`
- `stage16n_exact_state_cycle1250_summary.md`
- `stage16n_exact_state_cycle1500_summary.md`
- `stage16n_exact_state_cycle1750_summary.md`
- `stage16n_exact_state_cycle2000_summary.md`

Heavy Abaqus outputs remain on scratch in the per-job directories under `/scratch/pr21vyci/`.
