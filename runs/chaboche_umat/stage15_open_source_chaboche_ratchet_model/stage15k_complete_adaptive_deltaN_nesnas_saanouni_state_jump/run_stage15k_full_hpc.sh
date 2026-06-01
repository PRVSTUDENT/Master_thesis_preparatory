#!/bin/bash
#PBS-safe full Stage 15K gated runner.
set -euo pipefail

mkdir -p logs restart_verification fixed_state_jump adaptive_state_jump plots

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export STAGE15K_ACTIVE_WORKERS="${STAGE15K_ACTIVE_WORKERS:-40}"

echo "Stage 15K full run started on $(hostname) at $(date)"
echo "Working directory: $(pwd)"
which python
python --version

python stage15k_neml_state_introspection.py 2>&1 | tee logs/stage15k_introspection_full_HPC.log
python stage15k_restart_reinjection_test.py 2>&1 | tee logs/stage15k_restart_reinjection_full_HPC.log
python stage15k_fixed_state_jump_smoke.py 2>&1 | tee logs/stage15k_fixed_smoke_full_HPC.log
python stage15k_fixed_state_jump_matrix.py 2>&1 | tee logs/stage15k_fixed_matrix_HPC.log
python stage15k_adaptive_deltaN_controller.py 2>&1 | tee logs/stage15k_adaptive_controller_HPC.log
python stage15k_adaptive_state_jump_matrix.py 2>&1 | tee logs/stage15k_adaptive_matrix_HPC.log
python stage15k_validate_against_baseline.py 2>&1 | tee logs/stage15k_validate_HPC.log
python stage15k_make_plots.py 2>&1 | tee logs/stage15k_plots_HPC.log
python stage15k_write_master_summary.py 2>&1 | tee logs/stage15k_master_summary_HPC.log

echo "Stage 15K full run finished at $(date)"
