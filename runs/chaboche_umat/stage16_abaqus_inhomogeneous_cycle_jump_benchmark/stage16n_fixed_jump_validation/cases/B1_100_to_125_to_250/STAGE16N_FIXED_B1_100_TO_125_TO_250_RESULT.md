# Stage 16N-C B1 Fixed Jump Result

Last updated: 2026-06-06

## Case

```text
Case name        : B1_100_to_125_to_250
PBS job          : 1341006.mmaster02
Abaqus job       : stage16n_fixed_b1_100_to_125_to_250
Base state       : cycle 100
Jump target      : cycle 125
Continuation     : cycles 126-250
Compare cycle    : 250
State strategy   : zero-order hold from cycle 100
```

This is the first real fixed state-initialized cycle-jump validation case. It is compared against both the completed 1000-cycle reference and the B0 cycle-100 to cycle-250 reinjection baseline.

## HPC accounting

```text
State               : F
Exit status         : 0
Started             : Sat Jun 6 07:22:19 2026
Finished            : Sat Jun 6 08:47:18 2026
Walltime used       : 01:24:54
CPU time used       : 09:01:35
CPU percent         : 659
Requested CPUs      : 16
Requested memory    : 90 GB
Requested walltime  : 22:00:00
Mail points         : abe
Mail user           : pr21vyci@mailserver.tu-freiberg.de
```

The job was submitted before the later 24-hour walltime policy update, so this B1 record still shows the older 22-hour walltime request. Future fixed-jump submit files use 24 hours.

## Solver and extraction status

```text
Abaqus solver status : completed successfully
Extraction status    : completed successfully
Parallelism          : 1 MPI rank x 16 threads
```

Extracted result files:

```text
stage16n_fixed_b1_100_to_125_to_250_cycle_metrics.csv
stage16n_fixed_b1_100_to_125_to_250_selected_cycle_local_states.csv
stage16n_fixed_b1_100_to_125_to_250_selected_cycle_loops.csv
```

## Comparison at cycle 250

| Quantity | Role | B1 total error vs reference | B0 baseline error | Additional error vs B0 |
| --- | --- | ---: | ---: | ---: |
| RF1_max | primary | 0.361433% | 0.259048% | 0.102384% |
| RF1_min | primary | 2.27018% | 0.687538% | 1.58264% |
| loop_area_abs | primary | 1.26223% | 0.967300% | 0.294934% |
| HOLE_RING_MISES_MAX | primary | 2.40141% | 7.63648% | -5.23507% |
| HOLE_RING_S11_MAX_ABS | primary | 1.21869% | 9.58753% | -8.36884% |
| HOLE_RING_SDV1_MAX | primary | 10.2916% | 0.360172% | 9.93139% |
| HOLE_RING_SDV8_MAX | diagnostic | 16.1769% | 10.9164% | 5.26047% |
| HOLE_RING_SDV11_MAX | primary | 11.2777% | 7.27213% | 4.00560% |

Comparison summary:

```text
Status                       : review
Maximum primary total error  : 11.2777%
Controlling primary quantity : HOLE_RING_SDV11_MAX
```

## Decision

B1 is a computational pass but not a method-gate pass.

The global response is promising:

```text
RF1_max additional error:   0.102384%
RF1_min additional error:   1.58264%
loop area additional error: 0.294934%
```

However, primary local state errors are too high:

```text
HOLE_RING_SDV1_MAX total error:  10.2916%
HOLE_RING_SDV11_MAX total error: 11.2777%
```

Therefore B2 and B3 should remain held. The next solver jobs should be smaller or diagnostic B1 variants rather than larger fixed jumps.

## Recommended next jobs under the two-slot policy

Use the two available 16-core slots for B1 diagnostics instead of B2/B3:

```text
Slot 1: B1-small = cycle 100 -> 112 -> continue to 250
Slot 2: B1-equilibration / phase diagnostic variant
```

The goal is to determine whether the local-state error comes primarily from jump size, phase handling, or the zero-order state approximation.
