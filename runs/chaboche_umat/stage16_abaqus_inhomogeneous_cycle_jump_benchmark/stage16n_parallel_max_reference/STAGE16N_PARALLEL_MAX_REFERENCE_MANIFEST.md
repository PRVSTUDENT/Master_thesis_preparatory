# Stage 16N Parallel Max Reference Manifest

- Source deck: `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles.inp`
- Run job: `stage16n_parallel_max_reference_1000cycles`
- PBS job: `1335408.mmaster02`
- Abaqus CPUs requested: `30`
- Abaqus mp_mode: `threads`
- Purpose: find the maximum number of full non-jump cycles obtainable in one walltime-limited parallel Abaqus run.
- Validation check: inspect `stage16n_parallel_max_reference_1000cycles.msg` for solver lines reporting more than `1 MPI RANK x 1 THREAD`.
