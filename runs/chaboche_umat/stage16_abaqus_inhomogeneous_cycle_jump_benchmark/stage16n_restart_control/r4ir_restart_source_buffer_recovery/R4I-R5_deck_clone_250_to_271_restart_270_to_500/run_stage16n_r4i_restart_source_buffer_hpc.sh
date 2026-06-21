#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r4ir5_deck_clone_250_to_271_restart_270_to_500"
SOURCE_JOB="stage16n_r4ir5_deck_clone_250_to_271_restart_270_to_500_source_250_to_271"
BASE_OLDJOB="stage16n_r1a_restart_ref_500cycles"
CHECKPOINT_CYCLE="250"
SOURCE_END_CYCLE="271"
RESTART_CYCLE="270"
FIRST_SOLVED_CYCLE="271"
FINAL_CYCLE="500"
SOURCE_STYLE="deck_clone"
PURPOSE="R4I-R5 deck-clone confirmation: clone/truncate the clean direct replay deck shape, solve 250--271, restart interior 270, continue 271--500"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
KEEP_SCRATCH="${KEEP_SCRATCH:-1}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4I] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4I] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4I] job: $JOB"
echo "[Stage16N-R4I] source style: $SOURCE_STYLE"
echo "[Stage16N-R4I] first solved cycle: $FIRST_SOLVED_CYCLE"
echo "[Stage16N-R4I] purpose: $PURPOSE"

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${SCRATCH_CASE_DIR:-}" ]]; then
    mkdir -p "$HOME_CASE_DIR"
    rsync -av \
      --include='*/' \
      --include='*.csv' \
      --include='*.md' \
      --include='*.txt' \
      --include='*.sta' \
      --include='*.log' \
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

bash link_restart_sources.sh

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
path = Path("stage16n_r4ir5_deck_clone_250_to_271_restart_270_to_500.inp")
path.write_text(path.read_text().replace("INC=__R4I_RESTART_INC__", "INC=" + "$RESTART_INC"))
PY

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$SOURCE_JOB" \
  2>&1 | tee "$LOG_DIR/${SOURCE_JOB}_extract.log" || true

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${SOURCE_JOB}.${ext}" ]]; then
    echo "Missing generated source restart file: $SOURCE_JOB.$ext" >&2
    exit 2
  fi
done

echo "[Stage16N-R4I] restart read: oldjob=$SOURCE_JOB step=$RESTART_CYCLE inc=$RESTART_INC"

abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$SOURCE_JOB" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

abaqus job="$JOB" input="${JOB}.inp" oldjob="$SOURCE_JOB" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}.log"

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_extract.log"

copy_lightweight_evidence

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
  echo "# Stage 16N-R4I Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Job: \`$JOB\`"
  echo "- Source job: \`$SOURCE_JOB\`"
  echo "- Source style: \`$SOURCE_STYLE\`"
  echo "- Purpose: \`$PURPOSE\`"
  echo "- Restart read: \`STEP=$RESTART_CYCLE, INC=$RESTART_INC\`"
  echo "- First solved cycle: \`$FIRST_SOLVED_CYCLE\`"
  echo "- Final cycle: \`$FINAL_CYCLE\`"
  if [[ -f "${JOB}_comparison_summary.csv" ]]; then
    tail -n +2 "${JOB}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4I_CASE_STATUS.md

copy_lightweight_evidence

if [[ "$KEEP_SCRATCH" == "1" ]]; then
  echo "[Stage16N-R4I] keeping scratch directory: ${SCRATCH_CASE_DIR:-$PWD}"
fi
echo "[Stage16N-R4I] end: $(date '+%Y-%m-%d %H:%M:%S')"
