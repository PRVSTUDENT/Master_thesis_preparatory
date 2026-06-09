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

| Case | PBS job | Status at early check | Start time | Host |
|---|---|---|---|---|
| `R3E1` | `1342248.mmaster02` | running; datacheck compiled and completed; checked at `mtime=Tue Jun 9 06:17:21 2026`, `walltime=00:07:22`, `cput=00:31:37`, `cpupercent=639`, `mem=6742616kb`, `vmem=5065784kb`, `ncpus=16` | Tue Jun 9 06:09:58 2026 | `mnode101` |
| `R3E2` | `1342249.mmaster02` | running; datacheck compiled and completed; checked at `mtime=Tue Jun 9 06:17:23 2026`, `walltime=00:07:23`, `cput=00:40:17`, `cpupercent=643`, `mem=8734044kb`, `vmem=5244024kb`, `ncpus=16` | Tue Jun 9 06:09:58 2026 | `mnode102` |

At the early `qstat -f` check, both jobs had `job_state=R`, `queue=teachingq`, `Resource_List.ncpus=16`, `Resource_List.mpiprocs=1`, `Resource_List.mem=90gb`, and `Resource_List.walltime=24:00:00`.

## Next Monitoring Step

Monitor `1342248.mmaster02` and `1342249.mmaster02` to completion. After completion, copy back lightweight outputs only:

- full PBS history with `qstat -x -f`
- `.sta`
- `STAGE16N_R3E_CASE_STATUS.md`
- `stage16n_r3e_exact_overwrite_comparison_summary.csv`
- `stage16n_r3e_exact_overwrite_comparison_details.csv`
- cycle metrics and selected local-state/loop CSVs
- `_logs/*overwrite_trace.txt`

Do not copy `.odb`, `.stt`, `.sim`, `.mdl`, `.prt`, `.msg`, `state.csv`, or `state.bin` unless explicitly requested.
