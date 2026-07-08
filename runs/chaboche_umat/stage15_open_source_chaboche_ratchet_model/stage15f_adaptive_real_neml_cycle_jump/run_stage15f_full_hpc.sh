#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

set +u
if [ -f /etc/profile ]; then
  source /etc/profile
fi
if command -v module >/dev/null 2>&1; then
  module purge || true
  module load python/gcc/11.4.0/3.11.7 || true
fi
set -u
hash -r

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

mkdir -p logs
{
  echo "[Stage 15F full] host=$(hostname)"
  echo "[Stage 15F full] python=$(command -v python3)"
  python3 --version
} | tee logs/STAGE15F_FULL_LOG.txt

python3 stage15f_correct_stage15e_ranking.py 2>&1 | tee -a logs/STAGE15F_FULL_LOG.txt
python3 stage15f_adaptive_controller.py 2>&1 | tee -a logs/STAGE15F_FULL_LOG.txt
tail -n 80 logs/STAGE15F_FULL_LOG.txt > logs/STAGE15F_JOB_OUT_TAIL.txt || true

