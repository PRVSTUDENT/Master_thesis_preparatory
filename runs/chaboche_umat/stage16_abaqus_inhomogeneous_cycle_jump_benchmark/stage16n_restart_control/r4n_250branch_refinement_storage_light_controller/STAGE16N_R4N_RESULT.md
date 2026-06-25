# Stage 16N-R4N Result

- Checked: 2026-06-25
- PBS job: `1355855.mmaster02`
- Controller: `R4N_250branch_refinement_storage_light_controller`
- Queue/host: `mediumq`, `mnode074`
- Requested resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`
- PBS result: `Exit_status=0`, `Stageout_status=1`
- PBS accounting: walltime `08:34:00`, cput `38:44:20`, `resources_used.cpupercent=675`, memory `94371840kb`, average active cores about `4.52 / 16`
- Classification: `target275_review`

R4N regenerated the complete `stage16n_r1b_restart_ref_250cycles` cycle-250 source package in scratch and reached the first refinement continuation, target 275, with continuation restart writing disabled. The target-275 comparison at cycle 500 completed, but it reviewed rather than passed:

| metric | value |
| --- | ---: |
| max global error | `2.5313106%` |
| max primary-local error | `9.3841268%` |
| diagnostic S11 error | `1.2393651%` |
| dominant local metric | `HOLE_RING_SDV8_MAX` |
| dominant global metric | `RF1_max` |

Because target 275 reviewed, the controller did not advance to target 280 or optional target 285. This is a scientific refinement result for the 250-branch true-jump path, not an Abaqus input-processing blocker. `Stageout_status=1` is retained as an infrastructure/stage-out warning only; the lightweight result evidence was recovered.

## Evidence

- `STAGE16N_R4N_CONTROLLER_STATUS.md`
- `STAGE16N_R4N_TARGET275_COMPARISON_SUMMARY.txt`
- `stage16n_r4n_target275_jump_250_to_275_solve_276_to_500_comparison_summary.csv`
- `stage16n_r4n_target275_jump_250_to_275_solve_276_to_500_comparison_details.csv`
- `stage16n_r4n_target275_jump_250_to_275_solve_276_to_500_cycle_metrics.csv`
- `stage16n_r4n_target275_jump_250_to_275_solve_276_to_500_selected_cycle_local_states.csv`
- `stage16n_r4n_target275_jump_250_to_275_solve_276_to_500_selected_cycle_loops.csv`
- `qstat_1355855_finished_full.txt`
- `stage16n_r4n_250branch_refinement_storage_light_controller_pbs_tail.txt`
