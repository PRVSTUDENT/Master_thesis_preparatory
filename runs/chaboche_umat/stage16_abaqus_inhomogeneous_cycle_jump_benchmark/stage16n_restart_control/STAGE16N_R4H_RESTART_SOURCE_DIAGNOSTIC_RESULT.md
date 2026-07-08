# Stage 16N R4H Restart-Source Diagnostic Result

Updated: 2026-06-19.

## Job status

All six R4H jobs completed at PBS/Abaqus level with `Exit_status=0`.

| Case | PBS job | Host | Start time | Finish time | Walltime | CPU time | CPU percent | Memory | vmem | Requested resources |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---|
| R4H1 long replay 280 -> 500 | 1349085 | mnode100 | Wed Jun 17 16:55:59 2026 | Wed Jun 17 20:10:47 2026 | 03:14:43 | 17:57:57 | 647 | 94375660 kb | 5377960 kb | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime `24:00:00` |
| R4H2 source 250 -> 281, restart 280 -> 500 | 1349086 | mnode101 | Wed Jun 17 16:55:59 2026 | Wed Jun 17 20:30:22 2026 | 03:34:18 | 20:05:38 | 654 | 94375908 kb | 8104540 kb | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime `24:00:00` |
| R4H3 long replay 270 -> 500 | 1349087 | mnode100 | Wed Jun 17 20:10:48 2026 | Wed Jun 17 23:37:09 2026 | 03:26:14 | 18:59:19 | 648 | 94375880 kb | 5437452 kb | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime `24:00:00` |
| R4H4 source 250 -> 271, restart 270 -> 500 | 1349088 | mnode101 | Wed Jun 17 20:30:25 2026 | Thu Jun 18 00:05:17 2026 | 03:34:47 | 19:57:39 | 651 | 94375800 kb | 7718236 kb | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime `24:00:00` |
| R4H5 long replay 505 -> 750 | 1349089 | mnode100 | Wed Jun 17 23:37:11 2026 | Thu Jun 18 03:16:59 2026 | 03:39:44 | 20:00:30 | 638 | 94375928 kb | 5599832 kb | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime `24:00:00` |
| R4H6 source 500 -> 506, restart 505 -> 750 | 1349090 | mnode101 | Thu Jun 18 00:05:18 2026 | Thu Jun 18 03:35:54 2026 | 03:30:30 | 19:14:24 | 648 | 94375736 kb | 5570452 kb | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime `24:00:00` |

All jobs ran in `teachingq`, used `resources_used.ncpus=16`, and finished with `job_state=F` and `Exit_status=0`.

## Classification

| Case | Mode | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error | Interpretation |
|---|---|---:|---|---:|---:|---:|---|
| R4H1 | long restarted replay, restart 280 -> 500 | 500 | pass | 0% | 0% | 0% | Long-replay restart record at 280 is clean. |
| R4H2 | short source 250 -> 281, restart from 280 -> 500 | 500 | fail | 1.1887403% | 11.83033% | 0.92936729% | Interior one-extra-cycle source restart still reproduces the R4G5/R4F1 failure. |
| R4H3 | long restarted replay, restart 270 -> 500 | 500 | pass | 0% | 0% | 0% | Long-replay restart record at 270 is clean. |
| R4H4 | short source 250 -> 271, restart from 270 -> 500 | 500 | review | 2.5314199% | 9.3860617% | 1.2392968% | Interior one-extra-cycle source restart still reproduces the R4G4 review case. |
| R4H5 | long restarted replay, restart 505 -> 750 | 750 | pass | 0% | 0% | 0% | Long-replay restart record at 505 is clean. |
| R4H6 | short source 500 -> 506, restart from 505 -> 750 | 750 | review | 0.31896796% | 8.0369449% | 1.5702038% | Interior one-extra-cycle source restart reproduces the R4F2 review-level result. |

## Interpretation

R4H closes the immediate ambiguity. Restart records written by a long restarted replay are exact: R4H1, R4H3, and R4H5 all pass with zero comparison error. The short source-split strategy remains inconsistent even when it writes one extra cycle and restarts from the interior target cycle: R4H2, R4H4, and R4H6 reproduce the earlier source-split signatures.

Decision: do not submit R4J9/R4J10 yet. The next useful audit is not another extrapolated jump; it is a source-split phase/history audit comparing long-replay and short-source files around the first continuation step, restart read step/inc, selected local states, and any load/amplitude/state carry-over differences.

## Lightweight evidence copied locally

R4H case folders now contain the lightweight evidence copied from HPC: `STAGE16N_R4H_CASE_STATUS.md`, comparison CSVs, cycle metrics, selected-cycle CSVs, `.sta`, PBS stdout where present, and `qstat_<jobid>_finished_full.txt`. Heavy Abaqus files were not copied.

Remote root: `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4h_restart_source_diagnostics`.
Local root: `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4h_restart_source_diagnostics`.

## Storage note

The HPC cleanup/watchdog had run by 2026-06-19 05:02:49 CEST. The post-check showed `/home` at 17T total, 11T used, 5.9T free; `/scratch` at 110T total, 82T used, 28T free; `/home/pr21vyci` at 66G.
