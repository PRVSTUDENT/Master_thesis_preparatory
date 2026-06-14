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

## Branch-Specific Interpretation

The first true cycle-skip refinement showed branch-dependent behavior. A +20 skip from cycle 250 to 270 passed the accuracy criterion, whereas the corresponding +20 skip from cycle 500 to 520 failed due to local hole-ring error. Therefore, the restart-preserved true-skip machinery is functional, but the safe jump size must be chosen adaptively and locally rather than assumed constant across the simulation.

The current thesis-safe boundary is therefore:

- Stable restart-preserved material overwrite: passed through R3J +20.
- Base cycle 250 true-skip branch: +20 passes and +50 fails; safe Delta N is somewhere between 20 and 50.
- Base cycle 500 true-skip branch: +20 and +50 both fail; safe Delta N is below 20.
- Next bracketing step: refine each branch separately instead of repeating one fixed jump size at both locations.

This supports the main adaptive-cycle-jump argument: fixed jump sizes are not reliable; local state evolution near the hole controls the acceptable Delta N.

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
