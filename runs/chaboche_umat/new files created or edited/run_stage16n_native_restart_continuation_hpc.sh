#!/usr/bin/env bash
set -euo pipefail

JOB="${1:-}"
OLDJOB="${2:-}"
TARGET_CYCLE="${3:-}"
if [[ -z "$JOB" || -z "$OLDJOB" || -z "$TARGET_CYCLE" ]]; then
  echo "Usage: $0 <job-name> <oldjob-name> <target-cycle>" >&2
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

echo "[Stage16N-R2] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R2] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R2] Abaqus job: ${JOB}"
echo "[Stage16N-R2] oldjob: ${OLDJOB}"
echo "[Stage16N-R2] target cycle: ${TARGET_CYCLE}"
echo "[Stage16N-R2] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${OLDJOB}.${ext}" ]]; then
    echo "Missing native restart source: ${OLDJOB}.${ext}" >&2
    exit 2
  fi
done

if [[ ! -f "${JOB}.inp" ]]; then
  echo "Missing continuation input deck: ${JOB}.inp" >&2
  exit 2
fi
if [[ ! -f "stage16n_neml_equivalent_chaboche_umat.for" ]]; then
  echo "Missing UMAT: stage16n_neml_equivalent_chaboche_umat.for" >&2
  exit 2
fi

abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}_datacheck.log"

abaqus job="${JOB}" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "${LOG_DIR}/${JOB}_parallelism_check.log" || true

if [[ -f "${JOB}.odb" && -f "stage16n_extract_hysteresis_and_local_states.py" ]]; then
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "${JOB}" \
    2>&1 | tee "${LOG_DIR}/${JOB}_extract.log"
fi

python3 stage16n_compare_native_restart_against_1000ref.py \
  --restart-metrics "${JOB}_cycle_metrics.csv" \
  --restart-local-states "${JOB}_selected_cycle_local_states.csv" \
  --cycles "${TARGET_CYCLE}" \
  --out-dir "." \
  2>&1 | tee "${LOG_DIR}/${JOB}_compare.log"

{
  echo "# Stage 16N-R2 Native Restart Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`${JOB}\`"
  echo "- Oldjob: \`${OLDJOB}\`"
  echo "- Target cycle: \`${TARGET_CYCLE}\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  if [[ -f "${JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
    echo "- Solver status: \`completed\`"
  else
    echo "- Solver status: \`check ${JOB}.sta\`"
  fi
} > "STAGE16N_R2_CASE_STATUS.md"

echo "[Stage16N-R2] end: $(date '+%Y-%m-%d %H:%M:%S')"
