# Stage 16N-R2 Native Restart Control Result

## Objective

Stage 16N-R2 tests native Abaqus restart continuation with no UMAT overwrite and no `SDVINI`/`SIGINI` scratch reinjection.

The two control cases are:

```text
R2C1: restart from cycle 100, continue to cycle 250
R2C2: restart from cycle 250, continue to cycle 500
```

## Scientific Gate

This stage answers whether Abaqus can restart the inhomogeneous plate-with-hole model from its own restart files while preserving the finite-element displacement, strain, equilibrium, solver-history, and material state.

If R2 passes, the earlier cycle-250 failure is attributable to scratch `SDVINI`/`SIGINI` reinjection rather than to the material model or geometry.

## Preparation Status

Prepared cases:

```text
stage16n_restart_control/native_restart_cases/R2C1_100_to_250
stage16n_restart_control/native_restart_cases/R2C2_250_to_500
```

Checkpoint increments are parsed from the completed R1 `.sta` files:

```text
cycle 100 -> step 100, inc 53
cycle 250 -> step 250, inc 58
```

## Submission Status

Submitted on 2026-06-08.

The first submission attempt used job IDs `1341282.mmaster02` and
`1341283.mmaster02`. Both exited during Abaqus datacheck because the native
restart oldjob `.odb` file was not symlinked into the R2 case folders. This was
a setup issue, not a solver or restart-physics result. The link script and case
runner now include `.odb` together with `.res`, `.stt`, `.mdl`, `.sim`, and
`.prt`.

Corrected live submissions:

```text
R2C1_100_to_250: 1341284.mmaster02
R2C2_250_to_500: 1341285.mmaster02
```

Both corrected jobs request:

```text
select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
walltime=24:00:00
cpus=16 mp_mode=threads
```

At the first `qstat -f` check after resubmission, both jobs were running:

```text
1341284.mmaster02: job_state=R, exec_host=mnode100/0*0, stime=Mon Jun  8 06:47:09 2026
1341285.mmaster02: job_state=R, exec_host=mnode101/0*0, stime=Mon Jun  8 06:47:07 2026
```

Full qstat snapshots are stored in the case folders:

```text
native_restart_cases/R2C1_100_to_250/qstat_1341284_full.txt
native_restart_cases/R2C2_250_to_500/qstat_1341285_full.txt
```

## Results

Pending. The corrected R2 jobs are running.
