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

echo "[Stage16N-R3D] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R3D] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R3D] Abaqus job: ${JOB}"
echo "[Stage16N-R3D] oldjob: ${OLDJOB}"
echo "[Stage16N-R3D] target cycle: ${TARGET_CYCLE}"
echo "[Stage16N-R3D] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

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
if [[ ! -f "stage16n_restart_jump_debug_umat.for" ]]; then
  echo "Missing UMAT: stage16n_restart_jump_debug_umat.for" >&2
  exit 2
fi

set +e
abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_restart_jump_debug_umat.for \
  datacheck interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}_datacheck.log"
datacheck_rc=${PIPESTATUS[0]:-0}

abaqus job="${JOB}" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_restart_jump_debug_umat.for \
  interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}.log"
abaqus_rc=${PIPESTATUS[0]:-0}
set -e

abaqus_solver_status="failed"
if [[ -f "${JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
  abaqus_solver_status="completed_successfully"
fi

trace_file="${LOG_DIR}/${JOB}_debug_trace.txt"
grep -h -A3 "STAGE16N_R3_DEBUG_TRACE" \
  "${JOB}.msg" "${JOB}.dat" "${LOG_DIR}/${JOB}.log" 2>/dev/null \
  | head -n 320 > "${trace_file}" || true
trace_count="$(grep -c "STAGE16N_R3_DEBUG_TRACE" "${trace_file}" 2>/dev/null | tr -d ' ')"
if [[ -z "${trace_count}" ]]; then
  trace_count=0
fi

debug_status="failed"
if [[ "${abaqus_solver_status}" = "completed_successfully" && "${trace_count}" -gt 0 ]]; then
  debug_status="pass"
elif [[ "${abaqus_solver_status}" = "completed_successfully" ]]; then
  debug_status="review_no_trace"
fi

{
  echo "# Stage 16N-R3 Restart Debug Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`${JOB}\`"
  echo "- Oldjob: \`${OLDJOB}\`"
  echo "- Target cycle: \`${TARGET_CYCLE}\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  echo "- Solver status: \`${abaqus_solver_status}\`"
  echo "- Debug status: \`${debug_status}\`"
  echo "- Debug trace lines: \`${trace_count}\`"
  echo
  echo "- Raw return codes:"
  echo "  - datacheck: \`${datacheck_rc}\`"
  echo "  - abaqus: \`${abaqus_rc}\`"
  echo
  echo "- Logs:"
  echo "  - ${LOG_DIR}/${JOB}.log"
  echo "  - ${LOG_DIR}/${JOB}_datacheck.log"
  echo "  - ${trace_file}"
} > "STAGE16N_R3_DEBUG_CASE_STATUS.md"

echo "[Stage16N-R3D] end: $(date '+%Y-%m-%d %H:%M:%S')"

if [[ "${debug_status}" = "pass" ]]; then
  exit 0
elif [[ "${abaqus_solver_status}" = "completed_successfully" ]]; then
  exit 3
else
  exit 2
fi
