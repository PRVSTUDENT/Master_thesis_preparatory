# ChatGPT 5.5 Analysis Handoff: Chaboche Stage 15 Results

Use this file as the starting map for analysing the current Chaboche UMAT,
Stage 15 real-NEML cycle-jump results, and the most recent Stage 15K HPC job.

## Current HPC Job Status

Historical PBS query for job `1334253.mmaster02`:

```text
Job_Name = stage15k_statejump
job_state = F
queue = teachingq
exec_host = mfatnode005/0*0
resources_used.walltime = 00:00:01
resources_used.cput = 00:00:00
resources_used.cpupercent = 10
resources_used.mem = 4648kb
resources_used.vmem = 0kb
Resource_List.ncpus = 40
Resource_List.mem = 160gb
Resource_List.walltime = 23:55:00
comment = Job run at Sat May 30 at 00:34 on mfatnode005
Exit_status = 1
```

Interpretation: the Stage 15K PBS job finished with failure status
`Exit_status=1` after about one second. However, the local lightweight Stage 15K
gate logs currently report successful introspection, exact restart/reinjection,
and fixed-smoke checks. Treat this as a wrapper/job-level failure or intentional
gate stop until the Stage 15K logs and shell scripts are inspected.

## Best Starting Documents

1. `docs/CHABOCHE_STAGE15_DETAILED_CODE_REPORT.pdf`
2. `docs/CHABOCHE_STAGE15_DETAILED_CODE_REPORT.md`
3. `docs/stage15_real_neml_cycle_jump_package/00_MANIFEST.md`
4. `docs/stage15_real_neml_cycle_jump_package/02_STAGE15E_METHOD.md`
5. `runs/chaboche_umat/CHABOCHE_DEBUG_REPORT.md`
6. `runs/chaboche_umat/CHABOCHE_CYCLE_JUMP_PREDICTION_REPORT.md`

## Stage 15D Baseline Reference Data

These are the no-cycle-jump reference truth tables used by the prediction
benchmarks:

- `docs/stage15_real_neml_cycle_jump_package/baseline/B1_stress_m150_to_250_cycle_summary.csv`
- `docs/stage15_real_neml_cycle_jump_package/baseline/B2_stress_0_to_300_cycle_summary.csv`
- `docs/stage15_real_neml_cycle_jump_package/baseline/STAGE15D_BASELINE_MASTER_SUMMARY.md`
- `docs/stage15_real_neml_cycle_jump_package/baseline/STAGE15D_BASELINE_RUN_SUMMARY.csv`

## Stage 15E Prediction Benchmark Results

Use these to analyse fixed-window prediction performance:

- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_CYCLE_JUMP_MATRIX.csv`
- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_CYCLE_JUMP_ERRORS.csv`
- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_ACCEPTANCE_TABLE.csv`
- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_BEST_METHODS_BY_TARGET.csv`
- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_BEST_ACCEPTED_METHODS_BY_TARGET.csv`
- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_MASTER_SUMMARY.md`

Useful Stage 15E plots:

- `docs/stage15_real_neml_cycle_jump_package/plots/B1_error_vs_target.svg`
- `docs/stage15_real_neml_cycle_jump_package/plots/B1_mean_strain_prediction.svg`
- `docs/stage15_real_neml_cycle_jump_package/plots/B1_ratcheting_prediction.svg`
- `docs/stage15_real_neml_cycle_jump_package/plots/B2_error_vs_target.svg`
- `docs/stage15_real_neml_cycle_jump_package/plots/B2_mean_strain_prediction.svg`
- `docs/stage15_real_neml_cycle_jump_package/plots/B2_ratcheting_prediction.svg`
- `docs/stage15_real_neml_cycle_jump_package/plots/method_comparison_heatmap.svg`

## Stage 15F Adaptive Jump Results

Use these to analyse adaptive jump-size selection:

- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/STAGE15F_MASTER_SUMMARY.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/STAGE15F_ACCEPTED_ROUTE_SUMMARY.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/STAGE15F_ADAPTIVE_JUMP_ROUTES.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/STAGE15F_ADAPTIVE_JUMP_ERRORS.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/plots/B1_error_vs_jump_size.svg`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/plots/B1_adaptive_route_prediction.svg`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/plots/B1_accepted_jump_map.svg`

## Stage 15G Long B1 Validation Baseline

Use these to analyse long-cycle validation and resumable NEML baseline state:

- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/STAGE15G_MASTER_SUMMARY.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/STAGE15G_RUN_METADATA.json`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/case_outputs/B1_long_cycle_summary.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/case_outputs/B1_long_selected_loops.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/case_outputs/B1_long_checkpoint.json`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/case_outputs/B1_long_status.txt`

## Stage 15K Complete Adaptive Delta-N State-Jump Work

Use these to analyse the newer complete state-jump attempt and the recent HPC
failure:

- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/STAGE15K_COMPLETE_METHOD_PLAN.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/STAGE15K_NEML_STATE_INTROSPECTION_REPORT.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/STAGE15K_NESNAS_SAANOUNI_FORMULATION.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/fixed_state_jump/STAGE15K_FIXED_SMOKE_REPORT.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/fixed_state_jump/STAGE15K_FIXED_SMOKE_500_TO_1000.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/restart_verification/STAGE15K_RESTART_REINJECTION_REPORT.md`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/restart_verification/STAGE15K_RESTART_REINJECTION_ERRORS.csv`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/logs/stage15k_fixed_smoke_HPC.log`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/logs/stage15k_introspection_HPC.log`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/logs/stage15k_restart_reinjection_HPC.log`

Important Stage 15K scripts:

- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/stage15k_state_extrapolator.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/stage15k_restart_reinjection_test.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/stage15k_neml_state_introspection.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/submit_stage15k_complete_state_jump.pbs`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15k_complete_adaptive_deltaN_nesnas_saanouni_state_jump/run_stage15k_full_hpc.sh`

## Main Source Code For Model Understanding

- `runs/chaboche_umat/umat/chaboche_vp_v1_working.f`
- `runs/chaboche_umat/umat_chaboche_v1_with_sdvini_sigini.f`
- `runs/chaboche_umat/chaboche_vp_v1_cyclic_eps005_20cycles.inp`
- `runs/chaboche_umat/stage12_percentage_jump_1000cycles/jump35_cycle350_to_cycle1000/umat_chaboche_v1_with_sdvini_sigini_predicted_cycle350.f`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15d_real_neml_full_baseline/stage15d_real_neml_baseline_worker.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15e_real_neml_cycle_jump_benchmark/stage15e_real_neml_cycle_jump_controller.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15e_real_neml_cycle_jump_benchmark/stage15e_cycle_jump_methods.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15f_adaptive_real_neml_cycle_jump/stage15f_adaptive_controller.py`
- `runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline/stage15g_real_neml_long_b1_runner.py`

## Suggested Analysis Questions

1. Why did Stage 15K job `1334253.mmaster02` exit with status `1` after one second?
2. Are the Stage 15K restart/reinjection errors consistent with the intended
   state-jump method?
3. Which Stage 15E prediction windows are reliable for B1 and B2 at long target
   cycles?
4. Does Stage 15F's adaptive route selection support a stable Nesnas-Saanouni
   style delta-N rule?
5. What is the gap between scalar ratcheting prediction and full NEML history
   vector/state reinjection?
