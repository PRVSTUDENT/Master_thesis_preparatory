# Stage 16N-R4J Branch Refinement Result

Checked on 2026-06-15 from HPC jobs `1345011.mmaster02` and `1345012.mmaster02`.

## Job history

| Case | PBS job | Node | Exit status | Walltime | CPU time | CPU percent | Memory | VMem | Requested resources |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| R4J5 250 -> 285, solve 286--500 | `1345011.mmaster02` | `mnode100` | 0 | 04:41:47 | 19:26:19 | 574 | 94375932kb | 5405592kb | `1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime 24:00:00 |
| R4J6 500 -> 510, solve 511--750 | `1345012.mmaster02` | `mnode101` | 0 | 05:13:59 | 21:45:58 | 563 | 94371840kb | 5645200kb | `1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, walltime 24:00:00 |

Both Abaqus solver jobs completed successfully. PBS history records `job_state=F` and `Exit_status=0` for both jobs. The earlier scratch wrapper attempts `1345009` and `1345010` exited immediately because the native restart source was not available in that first scratch staging attempt; the completed production jobs are `1345011` and `1345012`.

## Accuracy result

| Case | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error | Controlling local metric |
|---|---:|---|---:|---:|---:|---|
| R4J5 | 500 | review | 0.00016982914% | 6.9643175% | 0.00027322599% | `HOLE_RING_SDV1_MAX` |
| R4J6 | 750 | review | 0.31107055% | 7.2880782% | 1.323401% | `HOLE_RING_SDV8_MAX` |

The branch-refinement pair therefore solved robustly but did not pass the current 5% primary-local accuracy gate. R4J5 (+35 from the cycle-250 branch) is close to the gate and has nearly exact global and S11 response, while R4J6 (+10 from the cycle-500 branch) still exceeds the local gate. This updates the bracket:

- Cycle-250 branch: +20 passed, +35 is review/fail against the 5% local gate, +50 failed.
- Cycle-500 branch: +10 is review/fail, +20 failed, +50 failed.

## Lightweight evidence copied into the repository

Heavy Abaqus files remain excluded from GitHub and stored on scratch. The useful lightweight evidence copied back locally is in:

- `restart_jump_cases/R4J5_250_to_285_solve_286_to_500/`
- `restart_jump_cases/R4J6_500_to_510_solve_511_to_750/`

Key files per case are the comparison summary/detail CSVs, cycle metrics CSV, selected cycle local-state/loop CSVs, case status markdown, PBS stdout, overwrite trace, and `qstat_*_finished_full.txt`.

## Next decision

For the cycle-250 branch, the next useful test is below +35, for example +27 or +30, to locate the pass boundary between +20 and +35. For the cycle-500 branch, the next useful test is below +10, for example +5, because +10 already exceeds the local gate.
