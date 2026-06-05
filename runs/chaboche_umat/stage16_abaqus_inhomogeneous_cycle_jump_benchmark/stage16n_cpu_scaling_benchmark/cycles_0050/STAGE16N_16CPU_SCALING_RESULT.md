# Stage 16N 16-CPU Scaling Result

## Job Status

- PBS job: `1335555.mmaster02`
- Job name: `s16n_scl_16c`
- Benchmark cycles: `50`
- Exit status: `0`
- PBS walltime: `00:36:00`
- PBS CPU time: `03:54:55`
- Requested resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=70gb`
- Abaqus command mode: `cpus=16 mp_mode=threads`
- Abaqus solver parallelism: `1 MPI RANK x 16 THREADS`

## Efficiency

- Wall seconds from benchmark script: `2157`
- Seconds per cycle: `43.14`
- Average effective cores from PBS accounting: approximately `6.5`
- Average utilization relative to 16 requested CPUs: approximately `40.8%`

## Interpretation

The 16-CPU launch is correct and does not fall back to serial execution. Abaqus reports `1 MPI RANK x 16 THREADS`, and the job completed successfully.

The run still does not saturate all 16 cores, which is expected for this Abaqus/Standard direct-sparse and UMAT workload. However, this is a more resource-conscious production default than requesting 30 CPUs, because the previous 30-thread full reference averaged about 9.9 effective cores.

Note: the raw `stage16n_scaling_0050cycles_16cpu_scaling_summary.csv` file has `analysis_completed=0` because the initial summary script searched for the completion phrase in the `.dat` file. The authoritative evidence is the Abaqus log and PBS `Exit_status = 0`, both of which confirm successful completion. The script has been corrected for future benchmark runs.
