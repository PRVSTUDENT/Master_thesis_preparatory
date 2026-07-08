# Stage 15E Real NEML Cycle-Jump Package Manifest

Date/time prepared: 2026-05-24 20:55 CEST

## Source Paths

- HPC source path: `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15e_real_neml_cycle_jump_benchmark`
- Local source path: `D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat\stage15_open_source_chaboche_ratchet_model\stage15e_real_neml_cycle_jump_benchmark`
- Documentation package: `docs/stage15_real_neml_cycle_jump_package`

## HPC Job

- Job ID: `1330335.mmaster02`
- Queue: `teachingq`
- Node: `mfatnode004`
- State: finished
- Walltime used: `00:00:16`
- CPU time used: `00:00:12`
- Memory used: `316732kb`
- Virtual memory used: `409796kb`

## Baseline Range

- `B1_stress_m150_to_250`: 279725 cycles available from Stage 15D
- `B2_stress_0_to_300`: 183632 cycles available from Stage 15D

## Accepted Cases

- B1 produced accepted cycle-jump predictions for the short and midrange targets.
- B2 produced no accepted predictions under the current 1%, 2%, or 5% normalized-error rules.
- Overall strict 1% accepted lanes: 13
- Overall relaxed 2% accepted lanes: 14
- Overall relaxed 5% accepted lanes: 19

## Uploaded Files

- `baseline/STAGE15D_BASELINE_RUN_SUMMARY.csv`
- `baseline/STAGE15D_BASELINE_MASTER_SUMMARY.md`
- `baseline/B1_stress_m150_to_250_cycle_summary.csv`
- `baseline/B2_stress_0_to_300_cycle_summary.csv`
- `stage15e_results/STAGE15E_CYCLE_JUMP_MATRIX.csv`
- `stage15e_results/STAGE15E_CYCLE_JUMP_ERRORS.csv`
- `stage15e_results/STAGE15E_ACCEPTANCE_TABLE.csv`
- `stage15e_results/STAGE15E_BEST_METHODS_BY_TARGET.csv`
- `stage15e_results/STAGE15E_MASTER_SUMMARY.md`
- `plots/*.svg`
- `scripts/stage15e_real_neml_cycle_jump_controller.py`
- `scripts/stage15e_cycle_jump_methods.py`
- `scripts/stage15e_preflight_check.py`
- `scripts/run_stage15e_smoke_hpc.sh`
- `scripts/run_stage15e_full_hpc.sh`
- `scripts/submit_stage15e_cycle_jump.pbs`
- `logs/STAGE15E_PREFLIGHT_LOG.txt`
- `logs/STAGE15E_SMOKE_TEST_LOG.txt`
- `logs/STAGE15E_QSUB_LOG.txt`
- `logs/STAGE15E_JOB_OUT_TAIL.txt`

## Intentionally Excluded

- Virtual environments
- `__pycache__`
- PBS core dumps
- Large raw NEML histories
- Temporary smoke-test folders
- Full PBS stdout beyond the small tail log
- Rejected fallback histories

## Reproduce

```bash
cd ~/master_thesis/Abaqus_trial/runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15e_real_neml_cycle_jump_benchmark
python3 stage15e_preflight_check.py
bash run_stage15e_smoke_hpc.sh
qsub submit_stage15e_cycle_jump.pbs
```

