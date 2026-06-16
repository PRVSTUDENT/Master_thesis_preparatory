#!/usr/bin/env bash
set -euo pipefail

SOURCE_JOB="stage16n_r4f2_source_500_to_505"
CONT_JOB="stage16n_r4f2_fullrestart_505_solve_506_to_750"
OLDJOB="stage16n_r1a_restart_ref_500cycles"
CHECKPOINT_CYCLE="500"
TARGET_RESTART_CYCLE="505"
FIRST_CONT_CYCLE="506"
FINAL_CYCLE="750"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${PBS_JOBDIR:-$PWD/_abaqus_scratch}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4F] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4F] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4F] source solve: $SOURCE_JOB ($CHECKPOINT_CYCLE -> $TARGET_RESTART_CYCLE)"
echo "[Stage16N-R4F] continuation: $CONT_JOB ($FIRST_CONT_CYCLE -> $FINAL_CYCLE)"
echo "[Stage16N-R4F] no UMAT overwrite; full Abaqus target restart is used"
echo "[Stage16N-R4F] scratch=$ABAQUS_SCRATCH"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${OLDJOB}.${ext}" ]]; then
    echo "Missing base native restart source: ${OLDJOB}.${ext}" >&2
    exit 2
  fi
done

if [[ ! -f "${SOURCE_JOB}.odb" ]]; then
  abaqus job="$SOURCE_JOB" input="${SOURCE_JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${SOURCE_JOB}.log"
fi

if [[ ! -f "${SOURCE_JOB}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${SOURCE_JOB}.sta"; then
  echo "Source solve did not complete successfully; check $SOURCE_JOB.sta" >&2
  exit 2
fi

target_inc="$(awk -v step="$TARGET_RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${SOURCE_JOB}.sta")"
echo "[Stage16N-R4F] restart read target: STEP=$TARGET_RESTART_CYCLE INC=$target_inc"

cat > "${CONT_JOB}.inp" <<EOF
** Stage 16N-R4F continuation: R4F2_500_to_505_fullrestart_solve_506_to_750
** Full native restart from target cycle; no SDVINI/SIGINI and no UMAT overwrite.
*HEADING
Stage 16N-R4F continuation 505 to 750
*RESTART, READ, STEP=${TARGET_RESTART_CYCLE}, INC=${target_inc}
EOF

for cycle in $(seq "$FIRST_CONT_CYCLE" "$FINAL_CYCLE"); do
  cat >> "${CONT_JOB}.inp" <<EOF
*STEP, NAME=CYCLE_$(printf '%04d' "$cycle"), NLGEOM=NO, INC=160
*STATIC
0.005, 1.0, 1.0E-08, 0.025
*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE
RIGHT_EDGE, 1, 1, 0.10
*OUTPUT, HISTORY, FREQUENCY=1
*NODE OUTPUT, NSET=RIGHT_EDGE
U1, RF1
EOF
  if [[ "$cycle" = "$FINAL_CYCLE" ]]; then
    cat >> "${CONT_JOB}.inp" <<EOF
*OUTPUT, FIELD, NUMBER INTERVAL=4
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, SDV
EOF
  fi
  echo "*END STEP" >> "${CONT_JOB}.inp"
done

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${SOURCE_JOB}.${ext}" ]]; then
    echo "Missing generated target restart source: ${SOURCE_JOB}.${ext}" >&2
    exit 2
  fi
done

abaqus job="${CONT_JOB}_datacheck" input="${CONT_JOB}.inp" oldjob="$SOURCE_JOB" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${CONT_JOB}_datacheck.log"

abaqus job="$CONT_JOB" input="${CONT_JOB}.inp" oldjob="$SOURCE_JOB" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
  2>&1 | tee "$LOG_DIR/${CONT_JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${CONT_JOB}.msg" \
  | tee "$LOG_DIR/${CONT_JOB}_parallelism_check.log" || true

abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py --job "$CONT_JOB" \
  2>&1 | tee "$LOG_DIR/${CONT_JOB}_extract.log"

cd "${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
CASE_DIR="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_r3j_jump_against_reference.py \
  --jump-metrics "$CASE_DIR/${CONT_JOB}_cycle_metrics.csv" \
  --jump-local-states "$CASE_DIR/${CONT_JOB}_selected_cycle_local_states.csv" \
  --ref-metrics "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv" \
  --ref-local-states "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv" \
  --cycles "$FINAL_CYCLE" \
  --out-dir "$CASE_DIR" \
  --prefix "$CONT_JOB" \
  2>&1 | tee "$CASE_DIR/$LOG_DIR/${CONT_JOB}_compare.log"

cd "$CASE_DIR"
{
  echo "# Stage 16N-R4F Full-Target Restart Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Base oldjob: \`$OLDJOB\`"
  echo "- Source solve: \`$SOURCE_JOB\`, cycles \`$((CHECKPOINT_CYCLE + 1)) -> $TARGET_RESTART_CYCLE\`"
  echo "- Continuation solve: \`$CONT_JOB\`, cycles \`$FIRST_CONT_CYCLE -> $FINAL_CYCLE\`"
  echo "- Restart read: \`oldjob=$SOURCE_JOB, STEP=$TARGET_RESTART_CYCLE, INC=$target_inc\`"
  echo "- UMAT overwrite: \`none\`"
  if [[ -f "${SOURCE_JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${SOURCE_JOB}.sta"; then
    echo "- Source solver status: \`completed_successfully\`"
  else
    echo "- Source solver status: \`check $SOURCE_JOB.sta\`"
  fi
  if [[ -f "${CONT_JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${CONT_JOB}.sta"; then
    echo "- Continuation solver status: \`completed_successfully\`"
  else
    echo "- Continuation solver status: \`check $CONT_JOB.sta\`"
  fi
  if [[ -f "${CONT_JOB}_comparison_summary.csv" ]]; then
    tail -n +2 "${CONT_JOB}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4F_CASE_STATUS.md

echo "[Stage16N-R4F] end: $(date '+%Y-%m-%d %H:%M:%S')"
