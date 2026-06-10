# Stage 16N-R3J Restart-Preserved Jump Submission

Date: 2026-06-10 Europe/Berlin

## Purpose

Stage 16N-R3J is the first nonzero restart-preserved cycle-jump test after the R3E exact-overwrite pass. It keeps the finite-element state from native Abaqus restart and overwrites only independent material memory, `STATEV(1:25)`, inside the UMAT at the restart continuation `KINC=0` call.

## Submitted production jobs

| Case | Active PBS job | Abaqus job | Restart checkpoint | Slope pair | Material-state jump | Continuation target |
|---|---:|---|---:|---|---|---:|
| R3J1 | `1342923.mmaster02` | `stage16n_r3j1_jump_250_to_255_to_500_a4` | 250 | 100 -> 250 | 250 -> 255 | 500 |
| R3J2 | `1342924.mmaster02` | `stage16n_r3j2_jump_500_to_505_to_750_a4` | 500 | 250 -> 500 | 500 -> 505 | 750 |

The original desired one-cycle slope pairs, `249 -> 250` and `499 -> 500`, were not available in the R1A ODB as stress/SDV field-output frames. The corrected active jobs therefore use the nearest available endpoint field-output pairs ending at the restart checkpoints: `100 -> 250` for R3J1 and `250 -> 500` for R3J2.

## Setup attempts

| Jobs | Result | Cause |
|---|---|---|
| `1342915`, `1342916` | setup failure | initial upload path quoting populated incorrect remote directories |
| `1342917`, `1342918` | setup failure | requested slope source cycles 249 and 499 had no stress/SDV field-output frames |
| `1342919`, `1342920` | setup failure | cluster Python rejected `from __future__ import annotations` |
| `1342921`, `1342922` | setup failure | older `pathlib.write_text` rejected the `newline` keyword |
| `1342923`, `1342924` | running | state extraction, extrapolated state creation, UMAT compile/link, and Abaqus datacheck passed |

## Live resource check

At the first live check after successful datacheck:

| PBS job | State | Queue | Host | Requested resources | Walltime used | CPU time | CPU percent | Memory | Vmem |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| `1342923.mmaster02` | R | teachingq | `mnode101/0*0` | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00` | 00:01:16 | 00:00:15 | 91 | 379696kb | 5048756kb |
| `1342924.mmaster02` | R | teachingq | `mnode102/0*0` | `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00` | 00:01:16 | 00:00:00 | 0 | 0b | 5231932kb |

Both active jobs use `1 MPI rank x 16 OpenMP threads` through `cpus=16 mp_mode=threads`.

## Pass criteria

The comparison reports:

- global RF/U/loop metrics,
- primary local metrics: `HOLE_RING_MISES_MAX`, `HOLE_RING_SDV1_MAX`, `HOLE_RING_SDV8_MAX`, `HOLE_RING_SDV11_MAX`,
- diagnostic-only metric: `HOLE_RING_S11_MAX_ABS`.

Classification:

- pass: `max_primary_local_error_pct <= 5`,
- review: `5 < max_primary_local_error_pct <= 10`,
- fail: `max_primary_local_error_pct > 10` or solver instability.
