# Stage 16N-R3E Exact Overwrite Result

Date checked: 2026-06-10 Europe/Berlin.

## Verdict

Stage 16N-R3E passed scientifically.

Both corrected exact-overwrite restart controls completed Abaqus successfully and reproduced the reference at the target cycle with zero measured global and primary local error. PBS reported `Exit_status=1` and `Stageout_status=1` for both jobs, but the Abaqus `.sta` and `.msg` files show `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` / `THE ANALYSIS HAS BEEN COMPLETED`. The nonzero PBS exit is therefore treated as a stage-out/wrapper artifact, not a solver or UMAT failure.

## Jobs

| Case | PBS job | Restart | Target | Abaqus result | Comparison |
|---|---:|---:|---:|---|---|
| R3E1 | `1342248.mmaster02` | 250 | 500 | completed successfully | pass, zero error |
| R3E2 | `1342249.mmaster02` | 500 | 750 | completed successfully | pass, zero error |

## PBS accounting

| Job | PBS state | Exit | Stage-out | Walltime | CPUT | CPU percent | Mem | VMem | Host |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `1342248.mmaster02` | `F` | 1 | 1 | 04:06:17 | 22:36:56 | 639 | 94375880kb | 5530808kb | `mnode101` |
| `1342249.mmaster02` | `F` | 1 | 1 | 04:10:00 | 22:43:25 | 643 | 94375816kb | 5664888kb | `mnode102` |

Both requested `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb` and `walltime=24:00:00`.

## Comparison summaries

| Case | Compared cycle | Status | Max global error pct | Max primary local error pct |
|---|---:|---|---:|---:|
| R3E1 | 500 | pass | 0 | 0 |
| R3E2 | 750 | pass | 0 | 0 |

R3E1 was compared against the default Stage 16N 1000-cycle pilot reference at cycle 500. R3E2 was compared against the parallel 1000-cycle reference because the default pilot comparison table did not include cycle 750.

## Scientific conclusion

The restart-preserved route can overwrite exact independent material memory inside a native Abaqus restart without damaging the preserved FE equilibrium state. This confirms that the failed scratch `SDVINI`/`SIGINI` route was failing because it attempted to reconstruct too much of the inhomogeneous FE state from scratch, not because the material-memory overwrite concept is inherently unstable.

## Next step

Proceed to the first small restart-preserved jump tests:

- R3J1: restart from cycle 250, overwrite/extrapolate material memory to cycle 255, continue to cycle 500.
- R3J2: restart from cycle 500, overwrite/extrapolate material memory to cycle 505, continue to cycle 750.

Do not jump directly to larger deltas until these small jumps are compared.
