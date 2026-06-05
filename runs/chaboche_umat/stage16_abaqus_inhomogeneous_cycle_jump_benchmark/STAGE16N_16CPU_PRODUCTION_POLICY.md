# Stage 16N 16-CPU Production Policy

Future Stage 16N Abaqus production jobs should use 16 CPUs by default.

## Reason

The completed 1000-cycle reference run verified that Abaqus launched with `1 MPI RANK x 30 THREADS`, but PBS accounting showed:

- Walltime: `17:56:43`
- CPU time: `178:03:42`
- Average effective cores: about `9.9`

This means the 30-thread run was valid and faster than the accidental serial run, but it did not keep 30 cores busy. A 16-core allocation is a more defensible production default because it leaves headroom above the observed average while avoiding the cost of reserving 30 cores.

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
