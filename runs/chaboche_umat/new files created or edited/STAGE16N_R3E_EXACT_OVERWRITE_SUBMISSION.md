# Stage 16N-R3E Exact Overwrite Submission

## Objective

Stage 16N-R3E tests exact restart-preserved material-memory overwrite inside a native Abaqus restart run.

These are exact overwrite controls, not cycle-jump predictions:

- `R3E1`: restart from cycle 250, overwrite exact cycle-250 independent `STATEV`, continue to cycle 500.
- `R3E2`: restart from cycle 500, overwrite exact cycle-500 independent `STATEV`, continue to cycle 750.

## Implementation

The generated UMAT hook triggers only on the first restart continuation call:

- `R3E1`: `JSTEP(1)=251`, `KINC=0`, `TIME(1)=0`, `TIME(2)~=250`
- `R3E2`: `JSTEP(1)=501`, `KINC=0`, `TIME(1)=0`, `TIME(2)~=500`

The hook reads exact per-element/per-integration-point state from a direct-access binary generated from the restart-source ODB.

Only independent material-memory variables are table-overwritten:

```text
STATEV(1:25)
```

The hook does not table-overwrite derived or diagnostic variables:

```text
STATEV(26:27)
```

## Submitted Jobs

All jobs use:

```text
select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
walltime=24:00:00
1 MPI rank x 16 OpenMP threads
```

### First Attempt

The first attempt failed before the solve because Abaqus could not resolve `scratch=.` from the long case path.

| Case | PBS job | Status | Walltime | CPU time | Host |
|---|---|---|---:|---:|---|
| `R3E1` | `1342246.mmaster02` | `Exit_status=1`, datacheck scratch-path failure | 00:00:20 | 00:00:16 | `mnode101` |
| `R3E2` | `1342247.mmaster02` | `Exit_status=1`, datacheck scratch-path failure | 00:00:23 | 00:00:17 | `mnode102` |

### Corrected `_a2` Attempt

The runner was corrected to use `${PBS_JOBDIR}` as Abaqus scratch.

| Case | PBS job | Final status | Start time | Host |
|---|---|---|---|---|
| `R3E1` | `1342248.mmaster02` | Abaqus completed successfully; PBS `Exit_status=1` from `Stageout_status=1`; comparison pass, zero error at cycle 500 | Tue Jun 9 06:09:58 2026 | `mnode101` |
| `R3E2` | `1342249.mmaster02` | Abaqus completed successfully; PBS `Exit_status=1` from `Stageout_status=1`; comparison pass, zero error at cycle 750 | Tue Jun 9 06:09:58 2026 | `mnode102` |

Final PBS history retained the requested `queue=teachingq`, `Resource_List.ncpus=16`, `Resource_List.mpiprocs=1`, `Resource_List.mem=90gb`, and `Resource_List.walltime=24:00:00`. Job `1342248.mmaster02` used `walltime=04:06:17`, `cput=22:36:56`, `cpupercent=639`, `mem=94375880kb`, and `vmem=5530808kb`. Job `1342249.mmaster02` used `walltime=04:10:00`, `cput=22:43:25`, `cpupercent=643`, `mem=94375816kb`, and `vmem=5664888kb`.

## Final Result

Both exact overwrite controls passed scientifically:

| Case | Compared cycle | Status | Max global error pct | Max primary local error pct |
|---|---:|---|---:|---:|
| `R3E1` | 500 | `pass` | 0 | 0 |
| `R3E2` | 750 | `pass` | 0 | 0 |

The lightweight evidence copied back locally includes final qstat histories, `.sta`, `.dat`, cycle metrics, selected local states/loops, and comparison summaries/details.

## Next Step

Proceed to small restart-preserved jump tests:

- `R3J1`: restart from cycle 250, overwrite/extrapolate material memory to cycle 255, continue to cycle 500.
- `R3J2`: restart from cycle 500, overwrite/extrapolate material memory to cycle 505, continue to cycle 750.

Do not copy `.odb`, `.stt`, `.sim`, `.mdl`, `.prt`, `.msg`, `state.csv`, or `state.bin` unless explicitly requested.
