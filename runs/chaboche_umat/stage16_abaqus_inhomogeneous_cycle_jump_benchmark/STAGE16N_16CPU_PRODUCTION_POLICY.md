# Stage 16N 16-CPU Production Policy

Future Stage 16N Abaqus production jobs should use 16 CPUs by default.

## Locked Production Setting

```text
Production default : 1 MPI rank x 16 OpenMP threads
PBS request        : select=1:ncpus=16:mpiprocs=1:ompthreads=16
Abaqus launch      : cpus=16 mp_mode=threads
Max walltime/job   : 24:00:00
Simultaneous jobs  : 2
Total active cores : 32
```

The 16-CPU configuration is not claimed to provide perfect CPU saturation. It is selected as a resource-efficient production compromise after verifying that Abaqus launches correctly in threaded mode and avoids the earlier serial fallback.

## Two-Job Scheduling Policy

From 2026-06-06 onward, Stage 16N solver planning assumes at most two simultaneous production jobs:

```text
Maximum simultaneous jobs : 2
Each job                  : 16 CPU cores
Maximum walltime/job      : 24 h
Total active usage        : 32 CPU cores
Production mode           : 1 MPI rank x 16 OpenMP threads
```

The two available slots should not be used blindly. First-time method checks remain gate cases and must be reviewed before launching dependent jobs. Once a method class passes its gate, independent jobs may be submitted in pairs.

For fixed cycle-jump validation:

```text
If B1 passes:
    submit B2 and B3 simultaneously.

If B1 fails:
    do not submit B2/B3.
    use the two slots for smaller/debug B1 variants instead.
```

## Reason

The completed 1000-cycle reference run verified that Abaqus launched with `1 MPI RANK x 30 THREADS`, but PBS accounting showed:

- Walltime: `17:56:43`
- CPU time: `178:03:42`
- Average effective cores: about `9.9`

This means the 30-thread run was valid and faster than the accidental serial run, but it did not keep 30 cores busy. A 16-core allocation is a more defensible production default because it leaves headroom above the observed average while avoiding the cost of reserving 30 cores.

The 16-CPU verification benchmark then completed successfully:

```text
PBS job:        1335555.mmaster02
Benchmark:      50 cycles
Walltime:       00:36:00
CPU time:       03:54:55
Exit status:    0
Abaqus launch:  1 MPI RANK x 16 THREADS
```

The measured effective usage was about 6.5 cores on average. This confirms correct threaded launch with lower resource reservation than the 30-CPU reference run.

## Required Settings

Use matching PBS and Abaqus settings:

```text
PBS:    select=1:ncpus=16:mpiprocs=1:ompthreads=16
Abaqus: cpus=16 mp_mode=threads
```

Do not mix a 16-core PBS request with an Abaqus command requesting a different CPU count.

## Acceptance Check

After launch, verify the Abaqus message file:

```bash
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" *.msg
```

The expected line is:

```text
1 HOST:        1 MPI RANK  x 16 THREADS
```

If the run reports `1 MPI RANK x 1 THREAD`, stop and fix the launcher before using the result.

## Scaling Caveat

This policy ensures correct 16-thread launch and prevents wasteful 30-core allocations. It cannot force perfect numerical scaling, because Abaqus/Standard sparse solves, UMAT execution, synchronization, and I/O may not fully saturate every core at every increment. The correct engineering target is efficient enough scaling with lower resource cost, not mathematically perfect CPU utilization.
