# Stage 16N-R4J +20 True-Skip Result

Date checked: 2026-06-14 Europe/Berlin

## Job Status

The true-skip +20 refinement pair completed as Abaqus analyses on the HPC scratch route.

| Case | PBS job | Restart checkpoint | Material-state jump | Solved cycles | Endpoint | Solver status |
|---|---:|---:|---:|---:|---:|---|
| R4J3 | 1344960.mmaster02 | 250 | 250 -> 270 | 271--500 | 500 | completed successfully |
| R4J4 | 1344961.mmaster02 | 500 | 500 -> 520 | 521--750 | 750 | completed successfully |

Both `.sta` files end with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`.

## Comparison Result

| Case | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error | Controlling metric |
|---|---:|---|---:|---:|---:|---|
| R4J3 | 500 | pass | 0.39923577% | 3.9830029% | 0.1398007% | `HOLE_RING_SDV1_MAX` |
| R4J4 | 750 | fail | 2.0853964% | 14.147994% | 13.256425% | `HOLE_RING_MISES_MAX` |

R4J3 passes the current primary-local 5% gate. R4J4 fails, controlled by the later checkpoint hole-ring Mises maximum and mirrored by the diagnostic absolute S11 error.

## Interpretation

The repaired restart route is solver-stable for true +20 skipped-cycle acceleration at both checkpoint windows, but +20 is not yet a globally safe production jump for the full Stage 16N benchmark because the later 500 -> 520 -> 750 window fails the local accuracy gate.

The current thesis-safe boundary is therefore:

- Stable restart-preserved material overwrite: passed through R3J +20.
- True skipped-cycle acceleration: +50 fails both windows; +20 passes the earlier 250 -> 270 -> 500 window but fails the later 500 -> 520 -> 750 window.
- Next bracketing step: test a smaller later-window true skip, such as +10 or +15 from cycle 500, before claiming a safe accelerated jump size beyond the earlier checkpoint.

## Repository Evidence

Lightweight result evidence copied from scratch and suitable for GitHub:

- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/STAGE16N_R3J_CASE_STATUS.md`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/STAGE16N_R3J_EXTRAPOLATED_STATE.md`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/stage16n_r4j3_jump_250_to_270_solve_271_to_500_comparison_summary.csv`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/stage16n_r4j3_jump_250_to_270_solve_271_to_500_comparison_details.csv`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/stage16n_r4j3_jump_250_to_270_solve_271_to_500_cycle_metrics.csv`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/stage16n_r4j3_jump_250_to_270_solve_271_to_500_selected_cycle_loops.csv`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/stage16n_r4j3_jump_250_to_270_solve_271_to_500_selected_cycle_local_states.csv`
- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/_logs/stage16n_r4j3_jump_250_to_270_solve_271_to_500_overwrite_trace.txt`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/STAGE16N_R3J_CASE_STATUS.md`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/STAGE16N_R3J_EXTRAPOLATED_STATE.md`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/stage16n_r4j4_jump_500_to_520_solve_521_to_750_comparison_summary.csv`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/stage16n_r4j4_jump_500_to_520_solve_521_to_750_comparison_details.csv`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/stage16n_r4j4_jump_500_to_520_solve_521_to_750_cycle_metrics.csv`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/stage16n_r4j4_jump_500_to_520_solve_521_to_750_selected_cycle_loops.csv`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/stage16n_r4j4_jump_500_to_520_solve_521_to_750_selected_cycle_local_states.csv`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/_logs/stage16n_r4j4_jump_500_to_520_solve_521_to_750_overwrite_trace.txt`

Heavy Abaqus outputs remain excluded from GitHub and should stay in scratch/offload storage.
