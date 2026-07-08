# Stage 16N-B B0-1 Exact Reinjection Result

## Case

```text
Case:       B0-1
Route:      exact cycle 100 state -> continue normally to cycle 250
PBS job:    1336497.mmaster02
Job name:   s16n_b0_100_to_250
```

## PBS Accounting

```text
PBS state:          F
PBS exit status:    2
PBS walltime:       01:41:36
PBS CPU time:       10:52:42
Requested CPUs:     16
Requested memory:   90 GB
```

The PBS exit status is `2` because the original postprocessing path in the runner was wrong. The Abaqus solver itself completed successfully, and the extraction was rerun manually afterward with the corrected script path.

## Abaqus Solver Status

```text
Datacheck: completed
Full run:  completed
Parallel:  1 MPI RANK x 16 THREADS
```

The run advanced through the `REINJECTION_EQUILIBRATE` step and completed the physical continuation from the exact cycle-100 state to cycle 250.

## Comparison Against 1000-Cycle Reference

Summary status:

```text
status: review
maximum monitored error: 10.9164 %
controlling quantity: HOLE_RING_SDV8_MAX
```

Selected errors at cycle 250:

| Quantity | Relative error |
| --- | ---: |
| RF1 max | 0.259048 % |
| RF1 min | 0.687538 % |
| Loop area | 0.967300 % |
| Hole-ring Mises max | 7.63648 % |
| Hole-ring S11 max abs | 9.58753 % |
| Hole-ring SDV1 max | 0.360172 % |
| Hole-ring SDV8 max | 10.9164 % |
| Hole-ring SDV11 max | 7.27213 % |

## Interpretation

B0-1 proves that the Stage 16N-B field-level `SIGINI` / `SDVINI` mechanics can run under the locked 16-CPU threaded production configuration and complete a long continuation.

It is not yet a clean numerical pass for the exact reinjection gate because local hole-ring stress and selected local STATEV errors exceed the preferred 1-2% exact-restart tolerance. The global hysteresis quantities are excellent, but the local field mismatch must be investigated before Stage 16N-C fixed jumps are treated as validated.

## Next Debug Priority

Before submitting B0-2 and B0-3, inspect:

```text
1. whether the reference field frame is exactly at the intended cycle-end phase
2. whether the reinjection equilibration step changes local SDV/stress before continuation
3. whether missing nodal displacement/history initialization explains the local mismatch
4. whether comparison should use post-equilibration state as a separate diagnostic checkpoint
```
