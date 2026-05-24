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
export STAGE15G_ACTIVE_WORKERS=1
export STAGE15G_STOP_SECONDS="${STAGE15G_STOP_SECONDS:-84900}"

mkdir -p case_outputs logs

{
  echo "[Stage 15G full] host=$(hostname)"
  echo "[Stage 15G full] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
  echo "[Stage 15G full] stop seconds=${STAGE15G_STOP_SECONDS}"
} | tee logs/STAGE15G_FULL_LOG.txt

python3 stage15g_preflight_check.py 2>&1 | tee logs/STAGE15G_PREFLIGHT_LOG.txt

set +e
python3 stage15g_real_neml_long_b1_runner.py \
  --target-cycles 2000000 \
  --stop-after-seconds "${STAGE15G_STOP_SECONDS}" \
  --status-every-seconds 60 \
  --checkpoint-every 1000 \
  --output-dir case_outputs \
  --resume \
  2>&1 | tee -a logs/STAGE15G_FULL_LOG.txt
runner_status=${PIPESTATUS[0]}
set -e

tail -n 100 logs/STAGE15G_FULL_LOG.txt > logs/STAGE15G_JOB_OUT_TAIL.txt || true

if [ "${runner_status}" -ne 0 ]; then
  echo "[Stage 15G full] runner failed with status ${runner_status}" | tee -a logs/STAGE15G_FULL_LOG.txt
  exit "${runner_status}"
fi

echo "[Stage 15G full] completed wrapper" | tee -a logs/STAGE15G_FULL_LOG.txt

