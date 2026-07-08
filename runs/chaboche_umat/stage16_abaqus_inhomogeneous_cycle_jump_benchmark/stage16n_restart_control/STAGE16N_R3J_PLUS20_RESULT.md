# Stage 16N-R3J +20 Restart-Preserved Jump Result

Date checked: 2026-06-12

## Summary

The cleanup-gated watchdog submitted the +20 restart-preserved jump pair after the final heavy `/home` `.stt` blockers were offloaded to `/scratch`. Both Abaqus jobs completed successfully and both endpoint comparisons passed exactly.

| Case | Job ID | Restart checkpoint | Slope pair | Material jump | Target cycle | Status | Max global error | Max primary local error | Diagnostic S11 error |
|---|---:|---:|---|---|---:|---|---:|---:|---:|
| R3J5 | 1344614 | 250 | 100 -> 250 | 250 -> 270 | 500 | pass | 0% | 0% | 0% |
| R3J6 | 1344615 | 500 | 250 -> 500 | 500 -> 520 | 750 | pass | 0% | 0% | 0% |

## PBS Accounting

| Case | Job ID | Exit status | Stageout status | Walltime | CPU time | CPU percent | Memory | Virtual memory | Host |
|---|---:|---:|---:|---|---|---:|---:|---:|---|
| R3J5 | 1344614 | 0 | 1 | 04:13:13 | 22:48:35 | 621 | 94375888kb | 5485864kb | mnode100 |
| R3J6 | 1344615 | 0 | 1 | 04:07:32 | 22:32:31 | 641 | 94375872kb | 7965660kb | mnode101 |

Both jobs were submitted by the watchdog at approximately 2026-06-12 06:52 CEST. R3J5 finished at 2026-06-12 11:05 CEST and R3J6 finished at 2026-06-12 11:00 CEST.

## Restart/Overwrite Evidence

- R3J5 generated an extrapolated material state for cycle 270 using the 100 -> 250 slope pair and overwrote `STATEV(1:25)` at `KSTEP=251`, `KINC=0`.
- R3J6 generated an extrapolated material state for cycle 520 using the 250 -> 500 slope pair and overwrote `STATEV(1:25)` at `KSTEP=501`, `KINC=0`.
- Each overwrite trace contains the expected 9 diagnostic trace lines.
- Both `.sta` files end with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`.

## Repository Evidence

R3J5:

- `restart_jump_cases/R3J5_250_to_270_to_500/STAGE16N_R3J_CASE_STATUS.md`
- `restart_jump_cases/R3J5_250_to_270_to_500/STAGE16N_R3J_EXTRAPOLATED_STATE.md`
- `restart_jump_cases/R3J5_250_to_270_to_500/qstat_1344614_finished_full.txt`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500.o1344614`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500.sta`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500_cycle_metrics.csv`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500_selected_cycle_loops.csv`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500_selected_cycle_local_states.csv`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500_comparison_summary.csv`
- `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500_comparison_details.csv`
- `restart_jump_cases/R3J5_250_to_270_to_500/_logs/stage16n_r3j5_jump_250_to_270_to_500_overwrite_trace.txt`
- `restart_jump_cases/R3J5_250_to_270_to_500/_logs/stage16n_r3j5_jump_250_to_270_to_500_parallelism_check.log`

R3J6:

- `restart_jump_cases/R3J6_500_to_520_to_750/STAGE16N_R3J_CASE_STATUS.md`
- `restart_jump_cases/R3J6_500_to_520_to_750/STAGE16N_R3J_EXTRAPOLATED_STATE.md`
- `restart_jump_cases/R3J6_500_to_520_to_750/qstat_1344615_finished_full.txt`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750.o1344615`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750.sta`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750_cycle_metrics.csv`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750_selected_cycle_loops.csv`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750_selected_cycle_local_states.csv`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750_comparison_summary.csv`
- `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750_comparison_details.csv`
- `restart_jump_cases/R3J6_500_to_520_to_750/_logs/stage16n_r3j6_jump_500_to_520_to_750_overwrite_trace.txt`
- `restart_jump_cases/R3J6_500_to_520_to_750/_logs/stage16n_r3j6_jump_500_to_520_to_750_parallelism_check.log`

## Interpretation

The restart-preserved UMAT cycle-jump workflow now passes nonzero +5, +10, and +20 material-state jumps in the inhomogeneous plate-with-hole Abaqus model. The result strengthens the conclusion that native Abaqus restart plus controlled UMAT state overwrite solves the fragile scratch reinjection problem.

Scientific caution remains: the endpoint response is still exactly insensitive under the current +20 jump tests. The next useful scientific step is a larger controlled escalation, such as +50 (`R3J7`: 250 -> 300 -> 500 and `R3J8`: 500 -> 550 -> 750), with the same audit discipline.
