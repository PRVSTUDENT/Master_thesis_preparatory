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
export STAGE15I_ACTIVE_WORKERS="${STAGE15I_ACTIVE_WORKERS:-24}"
export STAGE15I_HARD_MAX_WORKERS="${STAGE15I_HARD_MAX_WORKERS:-32}"
export STAGE15I_MAX_CYCLES_PER_LAUNCH="${STAGE15I_MAX_CYCLES_PER_LAUNCH:-10000}"
export STAGE15I_STOP_SECONDS="${STAGE15I_STOP_SECONDS:-70800}"

mkdir -p case_outputs logs

{
  echo "[Stage 15I full] host=$(hostname)"
  echo "[Stage 15I full] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
  echo "[Stage 15I full] active workers=${STAGE15I_ACTIVE_WORKERS}"
  echo "[Stage 15I full] max cycles per launch=${STAGE15I_MAX_CYCLES_PER_LAUNCH}"
  echo "[Stage 15I full] stop seconds=${STAGE15I_STOP_SECONDS}"
} | tee logs/STAGE15I_FULL_LOG.txt

python3 stage15i_preflight_check.py 2>&1 | tee logs/STAGE15I_PREFLIGHT_LOG.txt

set +e
python3 stage15i_multicase_long_runner.py \
  --target-cycles 1500000 \
  --extension-target-cycles 2000000 \
  --stop-after-seconds "${STAGE15I_STOP_SECONDS}" \
  --status-every-seconds 60 \
  --checkpoint-every 1000 \
  --output-dir case_outputs \
  --active-workers "${STAGE15I_ACTIVE_WORKERS}" \
  --max-cycles-per-launch "${STAGE15I_MAX_CYCLES_PER_LAUNCH}" \
  --resume \
  2>&1 | tee -a logs/STAGE15I_FULL_LOG.txt
runner_status=${PIPESTATUS[0]}
set -e

python3 stage15i_make_reduced_summary.py --input-dir case_outputs --output STAGE15I_TARGET_CYCLE_VALUES.csv \
  2>&1 | tee -a logs/STAGE15I_FULL_LOG.txt || true

tail -n 100 logs/STAGE15I_FULL_LOG.txt > logs/STAGE15I_JOB_OUT_TAIL.txt || true

if [ "${runner_status}" -ne 0 ]; then
  echo "[Stage 15I full] runner failed with status ${runner_status}" | tee -a logs/STAGE15I_FULL_LOG.txt
  exit "${runner_status}"
fi

echo "[Stage 15I full] completed wrapper" | tee -a logs/STAGE15I_FULL_LOG.txt
