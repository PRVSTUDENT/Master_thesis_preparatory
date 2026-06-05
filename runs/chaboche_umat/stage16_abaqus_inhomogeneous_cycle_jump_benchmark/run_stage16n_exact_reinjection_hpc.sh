#!/usr/bin/env bash
set -euo pipefail

# Stage 16N-B exact reinjection runner.
# Usage from a prepared case directory:
#   bash ../../run_stage16n_exact_reinjection_hpc.sh <job-name>

JOB="${1:-}"
if [[ -z "$JOB" ]]; then
  echo "Usage: $0 <job-name>" >&2
  exit 2
fi

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
mkdir -p "$LOG_DIR"

if [[ ! -f "${JOB}.inp" ]]; then
  echo "Missing input deck: ${JOB}.inp" >&2
  exit 2
fi
if [[ ! -f "stage16n_sdvini_sigini_state_reader.for" ]]; then
  echo "Missing UMAT/state-reader file: stage16n_sdvini_sigini_state_reader.for" >&2
  exit 2
fi

echo "Stage 16N-B exact reinjection job: ${JOB}"
echo "Abaqus cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

abaqus job="${JOB}_datacheck" \
  input="${JOB}.inp" \
  user=stage16n_sdvini_sigini_state_reader.for \
  cpus="${ABAQUS_CPUS}" \
  mp_mode="${ABAQUS_MP_MODE}" \
  interactive datacheck | tee "${LOG_DIR}/${JOB}_datacheck.log"

abaqus job="${JOB}" \
  input="${JOB}.inp" \
  user=stage16n_sdvini_sigini_state_reader.for \
  cpus="${ABAQUS_CPUS}" \
  mp_mode="${ABAQUS_MP_MODE}" \
  interactive | tee "${LOG_DIR}/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" | tee "${LOG_DIR}/${JOB}_parallelism_check.log" || true

abaqus python ../../stage16n_extract_hysteresis_and_local_states.py --job "${JOB}" \
  | tee "${LOG_DIR}/${JOB}_extract.log"

echo "Stage 16N-B exact reinjection completed: ${JOB}"
