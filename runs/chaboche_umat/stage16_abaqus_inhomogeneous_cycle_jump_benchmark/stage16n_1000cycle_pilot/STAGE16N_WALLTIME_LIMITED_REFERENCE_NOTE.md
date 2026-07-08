# Stage 16N Walltime-Limited Reference Note

The Stage 16N 1000-cycle pilot was submitted with a 22-hour walltime limit. The run reached 592 completed cycles and entered cycle 593 before PBS terminated the job at the walltime limit.

This result should be treated as a walltime-limited full-cycle reference through cycle 592, not as a completed 1000-cycle reference.

Important accounting detail: the PBS job requested 30 CPUs, but the Abaqus solver ran as `1 MPI RANK x 1 THREAD`. PBS accounting reported about 22 CPU-hours over about 22 wall-clock hours, confirming that the expensive baseline was effectively a serial Abaqus run inside a 30-core allocation.

The partial 592-cycle result is still useful because the cyclic evolution thresholds were already exceeded before the planned 1000-cycle endpoint. The reference is therefore sufficient for the first adaptive Delta-N development and controlled jump validation inside the known reference window.

For future Stage 16N runs, pass the PBS CPU count explicitly to Abaqus with `cpus=$PBS_NP` and an appropriate parallel mode, then verify the `.msg` file reports more than `1 MPI RANK x 1 THREAD`.
