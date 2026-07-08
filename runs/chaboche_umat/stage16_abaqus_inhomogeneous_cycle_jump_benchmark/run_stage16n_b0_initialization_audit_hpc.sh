#!/usr/bin/env bash
set -euo pipefail

JOB="${1:-stage16n_b0_audit_100_initialization_only}"
ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
mkdir -p "$LOG_DIR"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

if [[ ! -f "${JOB}.inp" ]]; then
  echo "Missing input deck: ${JOB}.inp" >&2
  exit 2
fi
if [[ ! -f "stage16n_sdvini_sigini_state_reader.for" ]]; then
  echo "Missing UMAT/state-reader file" >&2
  exit 2
fi
if [[ ! -f "state.bin" ]]; then
  echo "Missing exact state binary: state.bin" >&2
  exit 2
fi

export STAGE16N_STATE_FILE="$PWD/state.csv"
export STAGE16N_STATE_BIN="$PWD/state.bin"

echo "Stage 16N-B0 initialization audit job: ${JOB}"
echo "Abaqus cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "State binary: ${STAGE16N_STATE_BIN}"

abaqus job="${JOB}_datacheck" \
  input="${JOB}.inp" \
  user=stage16n_sdvini_sigini_state_reader.for \
  cpus="${ABAQUS_CPUS}" \
  mp_mode="${ABAQUS_MP_MODE}" \
  interactive datacheck ask_delete=OFF scratch=. | tee "${LOG_DIR}/${JOB}_datacheck.log"

abaqus job="${JOB}" \
  input="${JOB}.inp" \
  user=stage16n_sdvini_sigini_state_reader.for \
  cpus="${ABAQUS_CPUS}" \
  mp_mode="${ABAQUS_MP_MODE}" \
  interactive ask_delete=OFF scratch=. | tee "${LOG_DIR}/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" | tee "${LOG_DIR}/${JOB}_parallelism_check.log" || true

abaqus python ../../../stage16n_compare_b0_initialization_audit.py \
  | tee "${LOG_DIR}/${JOB}_compare.log"

echo "Stage 16N-B0 initialization audit completed: ${JOB}"
