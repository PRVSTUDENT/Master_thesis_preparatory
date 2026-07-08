# Stage 16N-B HPC Execution Status

## Current Gate

Stage 16N-B is the exact state reinjection verification gate. It must pass before any extrapolated fixed or adaptive cycle-jump validation is interpreted.

## Prepared Inputs

Exact states were extracted from the completed 1000-cycle reference ODB for:

```text
cycle 100
cycle 250
cycle 500
```

The extractor writes:

```text
stage16n_exact_reinjection/state/stage16n_exact_state_cycle0100.csv
stage16n_exact_reinjection/state/stage16n_exact_state_cycle0100.bin
stage16n_exact_reinjection/state/stage16n_exact_state_cycle0250.csv
stage16n_exact_reinjection/state/stage16n_exact_state_cycle0250.bin
stage16n_exact_reinjection/state/stage16n_exact_state_cycle0500.csv
stage16n_exact_reinjection/state/stage16n_exact_state_cycle0500.bin
```

The CSV files are for audit/debugging. The binary files are used by `SIGINI` and `SDVINI` through direct-access record reads.

## Reader Fixes Applied

The initial CSV preload design failed under the 16-thread Abaqus run because multiple threads tried to load the same CSV at the first initialization calls. The reader was changed to use a direct-access binary file:

```text
record = (NOEL - 1) * 8 + NPT
record contents = S1-S6, SDV1-SDV27
```

On this Abaqus/Intel Fortran environment, direct-access `RECL` is interpreted in 4-byte words, so the correct record length for 33 double values is:

```text
RECL = 66
```

## B0-1 Submission

Case:

```text
B0-1: exact cycle 100 state -> continue normally to cycle 250
```

Active submitted job:

```text
Job ID   : 1336497.mmaster02
Job name : s16n_b0_100_to_250
CPUs     : 16
PBS      : select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
```

Status at submission check:

```text
Datacheck completed successfully.
Full Abaqus analysis started.
The run advanced past the reinjection-equilibration step and into physical continuation cycles.
```

## Important Interpretation

The successful datacheck proves that the Stage 16N-B `SIGINI` / `SDVINI` state-reader mechanics now work under the locked 16-CPU threaded configuration.

The active full analysis still needs to finish and be compared against the 1000-cycle reference before Stage 16N-C should begin.
