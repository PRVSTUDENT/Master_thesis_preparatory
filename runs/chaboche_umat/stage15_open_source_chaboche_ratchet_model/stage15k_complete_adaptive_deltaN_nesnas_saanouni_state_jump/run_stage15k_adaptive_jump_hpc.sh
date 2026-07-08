#!/bin/bash
set -euo pipefail

mkdir -p logs adaptive_state_jump
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python stage15k_adaptive_deltaN_controller.py 2>&1 | tee logs/stage15k_adaptive_controller_HPC.log
python stage15k_adaptive_state_jump_matrix.py 2>&1 | tee logs/stage15k_adaptive_matrix_HPC.log
