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
export STAGE15E_MEMORY_SAFE=1
export STAGE15E_MAX_WORKERS="${STAGE15E_MAX_WORKERS:-12}"
export STAGE15E_STOP_SECONDS="${STAGE15E_STOP_SECONDS:-84900}"

mkdir -p logs

heartbeat_pid=""
cleanup() {
  if [ -n "${heartbeat_pid}" ]; then
    kill "${heartbeat_pid}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

(
  while true; do
    {
      date
      echo "host=$(hostname)"
      echo "STAGE15E_MAX_WORKERS=${STAGE15E_MAX_WORKERS}"
      if [ -f STAGE15E_CHECKPOINT.txt ]; then
        cat STAGE15E_CHECKPOINT.txt
      fi
    } > STAGE15E_HEARTBEAT.txt
    sleep 60
  done
) &
heartbeat_pid="$!"

{
  echo "[Stage 15E full] host=$(hostname)"
  echo "[Stage 15E full] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
  echo "[Stage 15E full] stop seconds=${STAGE15E_STOP_SECONDS}"
} | tee logs/STAGE15E_FULL_RUN_LOG.txt

python3 stage15e_preflight_check.py 2>&1 | tee logs/STAGE15E_PREFLIGHT_LOG.txt

set +e
python3 stage15e_real_neml_cycle_jump_controller.py \
  --output-dir . \
  --stop-after-seconds "${STAGE15E_STOP_SECONDS}" \
  2>&1 | tee -a logs/STAGE15E_FULL_RUN_LOG.txt
controller_status=${PIPESTATUS[0]}
set -e

tail -n 80 logs/STAGE15E_FULL_RUN_LOG.txt > logs/STAGE15E_JOB_OUT_TAIL.txt || true

if [ "${controller_status}" -ne 0 ]; then
  echo "[Stage 15E full] controller failed with status ${controller_status}" | tee -a logs/STAGE15E_FULL_RUN_LOG.txt
  exit "${controller_status}"
fi

echo "[Stage 15E full] completed" | tee -a logs/STAGE15E_FULL_RUN_LOG.txt

