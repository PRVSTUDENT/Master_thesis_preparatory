# Stage 16N-R4E Exact-Target Control Result

Checked on 2026-06-16 from PBS history and copied lightweight run evidence.

## Purpose

R4E1 and R4E2 were exact-target true-skip controls. Each case first generated the exact target material state from a short native-restart source solve, then used that exact state in the true-skip deck. This was intended to separate extrapolated-state error from restart phase, overwrite timing, and comparison-mapping error.

## Jobs

| Case | PBS job | Host | Exit | Walltime | CPU time | CPU percent | Memory |
|---|---:|---|---:|---:|---:|---:|---:|
| R4E1 `250 -> exact 280 -> 500` | 1345655 | mnode100 | 0 | 05:08:21 | 22:15:38 | 593 | 94375852 kb |
| R4E2 `500 -> exact 505 -> 750` | 1345656 | mnode101 | 0 | 05:17:40 | 22:34:55 | 598 | 94371840 kb |

Both Abaqus true-skip solves completed successfully.

## Classification

| Case | Endpoint | Status | Max global error | Max primary local error | Controlling primary variable | Diagnostic S11 error |
|---|---:|---|---:|---:|---|---:|
| R4E1 | 500 | fail | 1.1886389% | 11.829104% | `HOLE_RING_SDV8_MAX` | 0.92936729% |
| R4E2 | 750 | fail | 1.4217578% | 13.598377% | `HOLE_RING_MISES_MAX` | 13.011616% |

Acceptance rule: pass <= 5% primary local error, review 5--10%, fail > 10%.

## Interpretation

The exact-target controls fail, and the summary errors are identical to the preceding extrapolated R4J7/R4J8 results. That means the current evidence does not support continuing directly to R4J9/R4J10. The next step is to audit exact-state extraction, state-file handoff, overwrite activation/timing, and comparison mapping before any more extrapolated refinement jobs are submitted.

## Lightweight Evidence Copied To Repository

- `restart_jump_cases/R4E1_250_to_280_exact_solve_281_to_500/`
- `restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/`

The copied evidence includes case manifests, exact-target notes, status files, PBS stdout, `.sta` files, comparison summary/detail CSVs, selected-cycle CSVs, cycle metrics, exact-target state summaries, and small setup/compare logs. Heavy state files and Abaqus binary artifacts remain off GitHub.
