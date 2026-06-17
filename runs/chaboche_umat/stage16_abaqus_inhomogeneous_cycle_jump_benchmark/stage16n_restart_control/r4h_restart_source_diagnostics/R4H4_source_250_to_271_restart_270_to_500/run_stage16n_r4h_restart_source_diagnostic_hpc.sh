#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r4h4_source_250_to_271_restart_270_to_500"
BASE_OLDJOB="stage16n_r1a_restart_ref_500cycles"
OLDJOB="stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271"
MODE="interior_source_split"
CHECKPOINT_CYCLE="250"
SOURCE_END_CYCLE="271"
RESTART_CYCLE="270"
FIRST_SOLVED_CYCLE="271"
FINAL_CYCLE="500"
PURPOSE="source solve 250--271, restart from interior cycle 270, then solve 271--500"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${PBS_JOBDIR:-$PWD/_abaqus_scratch}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4H] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4H] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4H] case: R4H4_source_250_to_271_restart_270_to_500"
echo "[Stage16N-R4H] mode: $MODE"
echo "[Stage16N-R4H] first solved cycle: $FIRST_SOLVED_CYCLE"
echo "[Stage16N-R4H] final cycle: $FINAL_CYCLE"
echo "[Stage16N-R4H] purpose: $PURPOSE"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${BASE_OLDJOB}.${ext}" ]]; then
    echo "Missing base native restart source: ${BASE_OLDJOB}.${ext}" >&2
    exit 2
  fi
done


if [[ ! -f "stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.odb" ]]; then
  abaqus job="stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271" input="stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.inp" oldjob="$BASE_OLDJOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.log"
fi

if [[ ! -f "stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.sta"; then
  echo "Source split solve did not complete successfully; check stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.sta" >&2
  exit 2
fi

RESTART_INC="$(awk -v step="$RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271.sta")"
python3 - <<PY
from pathlib import Path
text = Path("stage16n_r4h4_source_250_to_271_restart_270_to_500.inp").read_text()
Path("stage16n_r4h4_source_250_to_271_restart_270_to_500.inp").write_text(text.replace("INC=__R4H_RESTART_INC__", "INC=" + "$RESTART_INC"))
PY

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271" \
  2>&1 | tee "$LOG_DIR/stage16n_r4h4_source_250_to_271_restart_270_to_500_source_250_to_271_extract.log" || true


if [[ "$MODE" = "interior_source_split" ]]; then
  for ext in odb res stt mdl sim prt; do
    if [[ ! -e "${OLDJOB}.${ext}" ]]; then
      echo "Missing generated split restart source: ${OLDJOB}.${ext}" >&2
      exit 2
    fi
  done
fi

echo "[Stage16N-R4H] restart read: oldjob=$OLDJOB step=$RESTART_CYCLE inc=$RESTART_INC"

abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$OLDJOB" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

abaqus job="$JOB" input="${JOB}.inp" oldjob="$OLDJOB" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "$LOG_DIR/${JOB}_parallelism_check.log" || true

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_extract.log"

python3 stage16n_compare_r3j_jump_against_reference.py \
  --jump-metrics "${JOB}_cycle_metrics.csv" \
  --jump-local-states "${JOB}_selected_cycle_local_states.csv" \
  --ref-metrics "../../../stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv" \
  --ref-local-states "../../../stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv" \
  --cycles "$FINAL_CYCLE" \
  --out-dir "." \
  --prefix "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_compare.log"

{
  echo "# Stage 16N-R4H Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Case: \`R4H4_source_250_to_271_restart_270_to_500\`"
  echo "- Mode: \`$MODE\`"
  echo "- Purpose: \`$PURPOSE\`"
  echo "- Base oldjob: \`$BASE_OLDJOB\`"
  echo "- Continuation oldjob: \`$OLDJOB\`"
  echo "- Restart read: \`STEP=$RESTART_CYCLE, INC=$RESTART_INC\`"
  echo "- First solved cycle: \`$FIRST_SOLVED_CYCLE\`"
  echo "- Final cycle: \`$FINAL_CYCLE\`"
  echo "- UMAT overwrite: \`none\`"
  if [[ -f "${JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
    echo "- Continuation solver status: \`completed_successfully\`"
  else
    echo "- Continuation solver status: \`check $JOB.sta\`"
  fi
  if [[ -f "${JOB}_comparison_summary.csv" ]]; then
    tail -n +2 "${JOB}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4H_CASE_STATUS.md

echo "[Stage16N-R4H] end: $(date '+%Y-%m-%d %H:%M:%S')"
