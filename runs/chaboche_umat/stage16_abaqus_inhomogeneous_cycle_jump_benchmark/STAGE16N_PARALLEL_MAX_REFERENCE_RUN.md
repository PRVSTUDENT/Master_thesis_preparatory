# Stage 16N Parallel Max Reference Run

## Purpose

Run the plate-with-hole NEML-equivalent UMAT model without cycle jumps, using the full 30-core HPC allocation, to determine the maximum number of conventional Abaqus cycles possible within one 22-hour walltime block.

This maximum completed cycle count will be used as the full-reference baseline limit for later cycle-jump comparisons.

## Submitted Job

- PBS job: `1335408.mmaster02`
- Job name: `stage16n_maxref`
- Queue: `teachingq` via `entry_teachingq`
- Walltime: `22:00:00`
- CPU request: `select=1:ncpus=30:mpiprocs=1:ompthreads=30:mem=135gb`
- Abaqus command mode: `cpus=30 mp_mode=threads`

## Verification Commands

Check queue state:

```bash
qstat -f 1335408.mmaster02
```

After the run starts, verify Abaqus is using the requested parallel resources:

```bash
cd ~/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_parallel_max_reference
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" stage16n_parallel_max_reference_1000cycles.msg
```

The previous serial run reported:

```text
1 MPI RANK x 1 THREAD
```

This run should not be accepted as the parallel max-reference baseline unless the `.msg` file confirms more than one thread or otherwise shows parallel solver usage.

After completion or walltime termination, read:

```bash
cat STAGE16N_PARALLEL_MAX_REFERENCE_STATUS.md
```

The key field is:

```text
Max completed non-jump cycle
```
