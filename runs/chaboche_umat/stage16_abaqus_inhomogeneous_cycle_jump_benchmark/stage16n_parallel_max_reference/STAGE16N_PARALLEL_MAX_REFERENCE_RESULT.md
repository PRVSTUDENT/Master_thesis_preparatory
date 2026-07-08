# Stage 16N Parallel Max Reference Result

## Run Status

The Stage 16N parallel max-reference Abaqus run completed successfully.

- PBS job: `1335408.mmaster02`
- Job name: `stage16n_maxref`
- Abaqus job: `stage16n_parallel_max_reference_1000cycles`
- Exit status: `0`
- Walltime used: `17:56:43`
- CPU time used: `178:03:42`
- Requested resources: `select=1:ncpus=30:mpiprocs=1:ompthreads=30:mem=135gb`
- Abaqus solver parallelism: `1 MPI RANK x 30 THREADS`
- Max completed non-jump cycle: `1000`
- Last partial cycle: `none`

This establishes the full non-jump Stage 16N baseline for later cycle-jump comparison as 1000 completed cycles.

## Extracted Reference Evidence

- `stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv`
- `stage16n_parallel_max_reference_1000cycles_selected_cycle_loops.csv`
- `stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv`

## Cycle 1 to Cycle 1000 Evolution

Global metrics:

- `RF1_max`: `2356.83407974` to `2908.24448395` (`+23.40%`)
- `RF1_min`: `-2509.71160126` to `-3074.82277679` (`+22.52%` magnitude change)
- `loop_area_abs`: `433.821593417` to `577.068315332` (`+33.02%`)

Selected local hole-ring metrics:

- `HOLE_RING_SDV1_MAX`: `0.0560648106039` to `26.0519256592`
- `HOLE_RING_SDV8_MAX`: `0.299562007189` to `92.4455032349`
- `HOLE_RING_SDV11_MAX`: `7.90187931061` to `61.3075714111`
- `HOLE_RING_MISES_MAX`: `398.503352332` to `492.827310009` (`+23.67%`)

## Interpretation

The previous serial run reached 592 completed cycles in about 22 hours. With explicit Abaqus threading, the same 1000-cycle non-jump reference completed in under 18 hours. This confirms that CPU usage was fixed and provides a complete full-cycle reference window for validating Stage 16N cycle-jump results.
