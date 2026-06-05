# Stage 16N CPU Scaling Plan

The 1000-cycle parallel reference confirmed Abaqus was launched with `1 MPI RANK x 30 THREADS`, but PBS accounting showed only partial average CPU utilization. This means the model benefits from parallel Abaqus, but 30 cores may not be the most resource-efficient choice.

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

Choose the smallest CPU count that captures most of the walltime improvement. If 12 or 16 CPUs is within about 10-15% of the 30-CPU walltime, use the smaller count for production.

The 30-CPU run should only be used if it delivers a clear walltime reduction that justifies the extra allocation and license-token cost.
