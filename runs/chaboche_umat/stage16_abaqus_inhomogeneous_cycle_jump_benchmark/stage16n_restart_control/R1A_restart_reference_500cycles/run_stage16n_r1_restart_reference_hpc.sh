#!/usr/bin/env bash
set -euo pipefail

JOB="${1:-}"
if [[ -z "$JOB" ]]; then
  echo "Usage: $0 <job-name>" >&2
  exit 2
fi

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
mkdir -p "$LOG_DIR"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R1] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R1] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R1] Abaqus job: ${JOB}"
echo "[Stage16N-R1] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

if [[ ! -f "${JOB}.inp" ]]; then
  echo "Missing input deck: ${JOB}.inp" >&2
  exit 2
fi
if [[ ! -f "stage16n_neml_equivalent_chaboche_umat.for" ]]; then
  echo "Missing UMAT: stage16n_neml_equivalent_chaboche_umat.for" >&2
  exit 2
fi

abaqus job="${JOB}_datacheck" input="${JOB}.inp" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}_datacheck.log"

abaqus job="${JOB}" input="${JOB}.inp" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "${LOG_DIR}/${JOB}_parallelism_check.log" || true

if [[ -f "${JOB}.odb" && -f "stage16n_extract_hysteresis_and_local_states.py" ]]; then
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "${JOB}" \
    2>&1 | tee "${LOG_DIR}/${JOB}_extract.log" || true
fi

{
  echo "# Stage 16N-R1 Restart Reference Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`${JOB}\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  if [[ -f "${JOB}.sta" ]]; then
    if grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
      echo "- Solver status: \`completed\`"
    else
      echo "- Solver status: \`check ${JOB}.sta\`"
    fi
  fi
  echo "- Restart files:"
  find . -maxdepth 1 -type f \\( -name "${JOB}.res" -o -name "${JOB}.stt" -o -name "${JOB}.mdl" -o -name "${JOB}.sim" \\) -printf "  - \`%f\`\\n" | sort
} > "STAGE16N_R1_RESTART_REFERENCE_STATUS.md"

echo "[Stage16N-R1] end: $(date '+%Y-%m-%d %H:%M:%S')"
