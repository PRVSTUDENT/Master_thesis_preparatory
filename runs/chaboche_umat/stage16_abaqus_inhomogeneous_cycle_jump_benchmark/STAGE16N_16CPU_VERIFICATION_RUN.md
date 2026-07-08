# Stage 16N 16-CPU Verification Run

## Purpose

Verify that the Stage 16N production launcher can run with a 16-CPU allocation and that Abaqus reports 16 solver threads, instead of silently falling back to serial execution.

## Submitted Benchmark

- PBS job: `1335555.mmaster02`
- Job name: `s16n_scl_16c`
- Benchmark cycles: `50`
- PBS request: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=70gb`
- Abaqus command: `cpus=16 mp_mode=threads`

## Verified During Run

The Abaqus message file reports:

```text
1 HOST:        1 MPI RANK  x 16 THREADS
```

This confirms the 16-thread launch is configured correctly.

## Remaining Check

After the benchmark finishes, read:

```text
runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_cpu_scaling_benchmark/cycles_0050/stage16n_scaling_0050cycles_16cpu_scaling_summary.csv
```

and PBS accounting:

```bash
qstat -x -f 1335555.mmaster02
```

to compute the measured 16-CPU walltime, average effective cores, and efficiency.

Perfect CPU saturation is not guaranteed by Abaqus/Standard, but the launch is now correct and avoids the previous 30-core over-allocation default.
