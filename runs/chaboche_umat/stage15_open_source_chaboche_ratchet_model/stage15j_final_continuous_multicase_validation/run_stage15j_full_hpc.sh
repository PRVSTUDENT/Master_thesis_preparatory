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
export STAGE15J_ACTIVE_WORKERS="${STAGE15J_ACTIVE_WORKERS:-40}"
export STAGE15J_STOP_SECONDS="${STAGE15J_STOP_SECONDS:-70800}"
export STAGE15J_RESUME="${STAGE15J_RESUME:-0}"

mkdir -p case_outputs logs plots

{
  echo "[Stage 15J full] host=$(hostname)"
  echo "[Stage 15J full] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
  echo "[Stage 15J full] active workers=${STAGE15J_ACTIVE_WORKERS}"
  echo "[Stage 15J full] stop seconds=${STAGE15J_STOP_SECONDS}"
  echo "[Stage 15J full] resume=${STAGE15J_RESUME}"
} | tee logs/STAGE15J_FULL_LOG.txt

python3 stage15j_preflight_check.py 2>&1 | tee logs/STAGE15J_PREFLIGHT_LOG.txt

resume_args=()
if [ "${STAGE15J_RESUME}" = "1" ]; then
  resume_args+=(--resume)
fi

set +e
python3 stage15j_continuous_multicase_runner.py \
  --primary-target-cycles 1500000 \
  --extension-target-cycles 2000000 \
  --stop-after-seconds "${STAGE15J_STOP_SECONDS}" \
  --status-every-seconds 60 \
  --checkpoint-every 1000 \
  --output-dir case_outputs \
  --active-workers "${STAGE15J_ACTIVE_WORKERS}" \
  "${resume_args[@]}" \
  2>&1 | tee -a logs/STAGE15J_FULL_LOG.txt
runner_status=${PIPESTATUS[0]}
set -e

python3 stage15j_make_reduced_summary.py --input-dir case_outputs --output STAGE15J_TARGET_CYCLE_VALUES.csv \
  2>&1 | tee -a logs/STAGE15J_FULL_LOG.txt || true

python3 stage15j_postprocess_transferability.py \
  2>&1 | tee -a logs/STAGE15J_FULL_LOG.txt || true

tail -n 100 logs/STAGE15J_FULL_LOG.txt > logs/STAGE15J_JOB_OUT_TAIL.txt || true

if [ "${runner_status}" -ne 0 ]; then
  echo "[Stage 15J full] runner failed with status ${runner_status}" | tee -a logs/STAGE15J_FULL_LOG.txt
  exit "${runner_status}"
fi

echo "[Stage 15J full] completed wrapper" | tee -a logs/STAGE15J_FULL_LOG.txt
