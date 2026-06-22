#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r4k1_deck_clone_exact_250_to_280_to_500"
SOURCE_JOB="${JOB}_source_250_to_281"
BASE_OLDJOB="stage16n_r1a_restart_ref_500cycles"
RESTART_CYCLE="280"
FIRST_SOLVED_CYCLE="281"
FINAL_CYCLE="500"
PURPOSE="R4K1 exact control: deck-clone source 250--281, restart interior 280, continue 281--500"

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
trap copy_lightweight_evidence EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4K1] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4K1] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4K1] job: $JOB"
echo "[Stage16N-R4K1] purpose: $PURPOSE"

bash link_restart_sources.sh

phase_time "R4K1 source solve" \
  abaqus job="$SOURCE_JOB" input="${SOURCE_JOB}.inp" oldjob="$BASE_OLDJOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${SOURCE_JOB}.log"

if [[ ! -f "${SOURCE_JOB}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${SOURCE_JOB}.sta"; then
  echo "Source solve did not complete successfully; check $SOURCE_JOB.sta" >&2
  exit 2
fi

RESTART_INC="$(awk -v step="$RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${SOURCE_JOB}.sta")"
python3 - <<PY
from pathlib import Path
path = Path("${JOB}.inp")
path.write_text(path.read_text().replace("INC=__R4I_RESTART_INC__", "INC=" + "$RESTART_INC"))
PY

phase_time "R4K1 source extraction" \
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$SOURCE_JOB" \
  2>&1 | tee "$LOG_DIR/${SOURCE_JOB}_extract.log" || true

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${SOURCE_JOB}.${ext}" ]]; then
    echo "Missing generated source restart file: $SOURCE_JOB.$ext" >&2
    exit 2
  fi
done

echo "[Stage16N-R4K1] restart read: oldjob=$SOURCE_JOB step=$RESTART_CYCLE inc=$RESTART_INC"

phase_time "R4K1 continuation datacheck" \
  abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$SOURCE_JOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

phase_time "R4K1 continuation solve" \
  abaqus job="$JOB" input="${JOB}.inp" oldjob="$SOURCE_JOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}.log"

phase_time "R4K1 ODB extraction" \
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_extract.log"

copy_lightweight_evidence

phase_time "R4K1 comparison" \
  python3 stage16n_compare_r3j_jump_against_reference.py \
    --jump-metrics "${JOB}_cycle_metrics.csv" \
    --jump-local-states "${JOB}_selected_cycle_local_states.csv" \
    --ref-metrics "reference_1000_cycle_metrics.csv" \
    --ref-local-states "reference_1000_selected_cycle_local_states.csv" \
    --cycles "$FINAL_CYCLE" \
    --out-dir "." \
    --prefix "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_compare.log"

{
  echo "# Stage 16N-R4K1 Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Job: \`$JOB\`"
  echo "- Source job: \`$SOURCE_JOB\`"
  echo "- Purpose: \`$PURPOSE\`"
  echo "- Restart read: \`STEP=$RESTART_CYCLE, INC=$RESTART_INC\`"
  echo "- First solved cycle: \`$FIRST_SOLVED_CYCLE\`"
  echo "- Final cycle: \`$FINAL_CYCLE\`"
  if [[ -f "${JOB}_comparison_summary.csv" ]]; then
    tail -n +2 "${JOB}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4K_CASE_STATUS.md

copy_lightweight_evidence
echo "[Stage16N-R4K1] end: $(date '+%Y-%m-%d %H:%M:%S')"
