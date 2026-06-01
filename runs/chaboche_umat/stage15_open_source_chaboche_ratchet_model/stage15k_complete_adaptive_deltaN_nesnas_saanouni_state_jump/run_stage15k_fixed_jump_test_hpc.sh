#!/bin/bash
set -euo pipefail

mkdir -p logs fixed_state_jump
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python stage15k_fixed_state_jump_smoke.py 2>&1 | tee logs/stage15k_fixed_smoke_HPC.log
