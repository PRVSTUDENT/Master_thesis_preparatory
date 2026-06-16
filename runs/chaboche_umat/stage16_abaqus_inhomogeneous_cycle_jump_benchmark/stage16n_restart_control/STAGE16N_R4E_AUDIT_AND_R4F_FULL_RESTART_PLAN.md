# Stage 16N R4E Audit and R4F Full-Restart Plan

Updated: 2026-06-16.

## R4E audit result

The corrected R4E exact-target true-skip jobs completed successfully but still reproduced the R4J7/R4J8 endpoint errors:

| Case | PBS job | Path | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error |
|---|---:|---|---:|---|---:|---:|---:|
| R4E1 | 1345655 | `restart_jump_cases/R4E1_250_to_280_exact_solve_281_to_500/` | 500 | fail | 1.1886389% | 11.829104% | 0.92936729% |
| R4E2 | 1345656 | `restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/` | 750 | fail | 1.4217578% | 13.598377% | 13.011616% |

The retained exact-target CSVs are byte-identical to the `state.csv` files handed to the R4E main true-skip decks:

| Case | Exact target | Data rows | SHA-256 |
|---|---:|---:|---|
| R4E1 | cycle 280 | 25184 | `4facbc0e87caf9c63febb31e51db819308cd496244ec33dabe79ff9a6ed2d3ff` |
| R4E2 | cycle 505 | 25184 | `b9254d54f41612772a55ee103b42db30734dcc8115d35800b61858d6b50a8948` |

The R4E exact-target CSVs are not identical to the earlier R4J extrapolated states:

| Comparison | Rows | Max absolute difference | Controlling field/key | Mean absolute difference |
|---|---:|---:|---|---:|
| R4E1 exact cycle 280 vs R4J7 extrapolated cycle 280 | 25184 | 70.03573608398443 | `S1`, `(NOEL=1239, NPT=1)` | 0.45458729863259084 |
| R4E2 exact cycle 505 vs R4J8 extrapolated cycle 505 | 25184 | 30.373046875 | `S1`, `(NOEL=1240, NPT=1)` | 0.16592580363277337 |

This rules out the simple failure mode that R4E accidentally consumed the same extrapolated `state.csv` as R4J7/R4J8. The overwrite traces also trigger at the intended restart steps: R4E1 at `KSTEP=251`, R4E2 at `KSTEP=501`. The trace is diagnostic output only, not a full count of all overwritten integration points.

The heavy binary `state.bin` files were not retained in the lightweight result directories after cleanup, so the durable repository audit is CSV-based.

## Interpretation

R4E is an exact material-state overwrite into a native restart that still carries the checkpoint-cycle mechanical state. Because R4E fails with the same endpoint comparisons as R4J7/R4J8, the current evidence suggests that material-only overwrite may be insufficient for a true skipped-cycle restart: Abaqus may also need the full mechanical/contact/internal restart state at the target cycle.

Do not submit R4J9/R4J10 until the full-target native restart controls are classified.

## R4F controls prepared

R4F removes the UMAT overwrite from the experiment. Each case first creates a short native-restart source solve to the target cycle, then restarts Abaqus from that target-cycle restart file set and solves the remaining cycles.

| Case | Source solve | Continuation solve | Overwrite |
|---|---|---|---|
| R4F1 | 250 -> 280 | 281--500 | none |
| R4F2 | 500 -> 505 | 506--750 | none |

Prepared files:

- `prepare_stage16n_r4f_full_target_restart_controls.py`
- `submit_stage16n_r4f_full_target_restart_case.sh`
- `stage16n_restart_control/full_target_restart_cases/stage16n_r4f_full_target_restart_cases.csv`
- `stage16n_restart_control/full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/`
- `stage16n_restart_control/full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/`

Classification rule remains:

- `pass`: primary local error <= 5%.
- `review`: primary local error > 5% and <= 10%.
- `fail`: primary local error > 10%.
