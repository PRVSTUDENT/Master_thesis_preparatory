#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r4k2b_505candidate_validation_505_to_750"
OLDJOB="stage16n_r4k2b_r4e2_candidate_cycle505_source"
RESTART_CYCLE="505"
FIRST_SOLVED_CYCLE="506"
FINAL_CYCLE="750"
PURPOSE="R4K2B storage-light validation: use preserved R4E2 cycle-505 restart source, continue 506--750"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

phase_time() {
  local label="$1"
  shift
  echo
  echo "============================================================"
  echo "PHASE START: $label"
  echo "TIME: $(date)"
  echo "============================================================"
  /usr/bin/time -v "$@"
  local rc=$?
  echo "============================================================"
  echo "PHASE END: $label"
  echo "TIME: $(date)"
  echo "EXIT: $rc"
  echo "============================================================"
  return $rc
}

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${SCRATCH_CASE_DIR:-}" ]]; then
    mkdir -p "$HOME_CASE_DIR"
    rsync -av \
      --include='*/' \
      --include='*.md' \
      --include='*.csv' \
      --include='*.txt' \
      --include='*.sta' \
      --include='*.log' \
      --include='*.out' \
      --include='*.pbs.out' \
      --exclude='*.odb' \
      --exclude='*.stt' \
      --exclude='*.res' \
      --exclude='*.sim' \
      --exclude='*.mdl' \
      --exclude='*.prt' \
      --exclude='*.dat' \
      --exclude='*.msg' \
      --exclude='*' \
      "$SCRATCH_CASE_DIR/" "$HOME_CASE_DIR/"
  fi
}

cleanup_continuation_heavy() {
  if [[ "${CLEAN_HEAVY_AFTER_CLASSIFICATION:-1}" != "1" ]]; then
    return 0
  fi
  find . -maxdepth 1 -type f \( \
    -name "${JOB}*.odb" -o -name "${JOB}*.stt" -o -name "${JOB}*.res" -o \
    -name "${JOB}*.sim" -o -name "${JOB}*.mdl" -o -name "${JOB}*.prt" -o \
    -name "${JOB}*.dat" -o -name "${JOB}*.msg" -o -name "${JOB}*.023" -o \
    -name "${JOB}*.cax" -o -name "${JOB}*.abq" -o -name "${JOB}*.pac" -o \
    -name "${JOB}*.sel" -o -name "${JOB}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
}

trap copy_lightweight_evidence EXIT

on_error() {
  local rc=$?
  {
    echo "# Stage 16N-R4K2B Case Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Job: \`$JOB\`"
    echo "- Purpose: \`$PURPOSE\`"
    echo "- Source: preserved R4E2 cycle-505 candidate"
    echo "- Classification: \`infrastructure_or_solver_execution_failure\`"
    echo "- Exit code: \`$rc\`"
    echo "- Heavy continuation cleanup: \`enabled\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > STAGE16N_R4K2B_CASE_STATUS.md
  copy_lightweight_evidence
  cleanup_continuation_heavy
  copy_lightweight_evidence
  exit "$rc"
}
trap on_error ERR

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4K2B] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4K2B] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4K2B] job: $JOB"
echo "[Stage16N-R4K2B] purpose: $PURPOSE"
echo "[Stage16N-R4K2B] no source-generation phase will be run"

bash link_r4e2_candidate_restart_source.sh

RESTART_INC="$(awk -v step="$RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${OLDJOB}.sta")"
python3 - <<PY
from pathlib import Path
path = Path("${JOB}.inp")
path.write_text(path.read_text().replace("INC=__R4I_RESTART_INC__", "INC=" + "$RESTART_INC"))
PY

echo "[Stage16N-R4K2B] restart read: oldjob=$OLDJOB step=$RESTART_CYCLE inc=$RESTART_INC"

phase_time "R4K2B continuation datacheck" \
  abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

phase_time "R4K2B continuation solve" \
  abaqus job="$JOB" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}.log"

phase_time "R4K2B ODB extraction" \
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_extract.log"

copy_lightweight_evidence

set +e
phase_time "R4K2B comparison" \
  python3 stage16n_compare_r3j_jump_against_reference.py \
    --jump-metrics "${JOB}_cycle_metrics.csv" \
    --jump-local-states "${JOB}_selected_cycle_local_states.csv" \
    --ref-metrics "reference_parallel_cycle_metrics.csv" \
    --ref-local-states "reference_parallel_selected_cycle_local_states.csv" \
    --cycles "$FINAL_CYCLE" \
    --out-dir "." \
    --prefix "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_compare.log"
COMPARE_RC=${PIPESTATUS[0]}
set -e

classification="scientific_failure"
if [[ "$COMPARE_RC" -eq 0 && -f "${JOB}_comparison_summary.csv" ]] && awk -F, 'NR == 2 && $2 == "pass" && $3+0 == 0 && $4+0 == 0 {ok=1} END {exit ok ? 0 : 1}' "${JOB}_comparison_summary.csv"; then
  classification="pass"
fi

{
  echo "# Stage 16N-R4K2B Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Job: \`$JOB\`"
  echo "- Purpose: \`$PURPOSE\`"
  echo "- Source: preserved R4E2 cycle-505 candidate"
  echo "- Restart read: \`STEP=$RESTART_CYCLE, INC=$RESTART_INC\`"
  echo "- First solved cycle: \`$FIRST_SOLVED_CYCLE\`"
  echo "- Final cycle: \`$FINAL_CYCLE\`"
  echo "- Classification: \`$classification\`"
  if [[ -f "${JOB}_comparison_summary.csv" ]]; then
    tail -n +2 "${JOB}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Heavy continuation cleanup: \`enabled\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4K2B_CASE_STATUS.md

copy_lightweight_evidence
cleanup_continuation_heavy
copy_lightweight_evidence

echo "[Stage16N-R4K2B] classification: $classification"
echo "[Stage16N-R4K2B] end: $(date '+%Y-%m-%d %H:%M:%S')"
