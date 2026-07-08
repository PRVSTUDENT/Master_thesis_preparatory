# Stage 16N CPU Scaling Plan

The 1000-cycle parallel reference confirmed Abaqus was launched with `1 MPI RANK x 30 THREADS`, but PBS accounting showed only partial average CPU utilization. This means the model benefits from parallel Abaqus, but 30 cores is not the most resource-efficient default.

Current production default: use `16` CPUs with `mp_mode=threads`, requested as `select=1:ncpus=16:mpiprocs=1:ompthreads=16`.

## Goal

Find the cheapest CPU count for Stage 16N full-reference and cycle-jump jobs:

- minimize walltime enough to stay inside queue limits;
- avoid requesting idle cores;
- compare core-hour cost, not only elapsed time.

## Benchmark

Run a short fixed benchmark deck, default 50 cycles, with matching PBS resources:

```bash
cd ~/master_thesis/Abaqus_trial
BENCHMARK_CYCLES=50 CPU_COUNTS="4 8 12 16 20 30" \
  bash runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/submit_stage16n_cpu_scaling_sweep_hpc.sh
```

Each job writes a compact summary file:

```text
runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_cpu_scaling_benchmark/cycles_0050/*_scaling_summary.csv
```

## Decision Rule

Choose the smallest CPU count that captures most of the walltime improvement. The production default is now 16 CPUs because the 30-thread run averaged only about 10 busy cores across the job.

The 30-CPU run should only be used if a short scaling benchmark shows a clear walltime reduction that justifies the extra allocation and license-token cost.

## 16-CPU Verification

For a 16-CPU production run, the Abaqus `.msg` file must show:

```text
1 HOST:        1 MPI RANK  x 16 THREADS
```

PBS accounting should also show:

```text
Resource_List.ncpus = 16
Resource_List.mpiprocs = 1
Resource_List.select = 1:ncpus=16:mpiprocs=1:ompthreads=16:...
```

Perfect saturation of all 16 cores cannot be guaranteed for Abaqus/Standard, but this configuration avoids reserving 30 cores when the measured average demand was much closer to 10.
