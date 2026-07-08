#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r3j5_jump_250_to_270_to_500"
OLDJOB="stage16n_r1a_restart_ref_500cycles"
PREVIOUS_CYCLE="100"
CHECKPOINT_CYCLE="250"
JUMP_CYCLES="20"
JUMP_CYCLE="270"
TARGET_CYCLE="500"
TARGET_STEP="251"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${PBS_JOBDIR:-$PWD/_abaqus_scratch}"
mkdir -p "$LOG_DIR"
mkdir -p "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R3J] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R3J] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R3J] Abaqus job: $JOB"
echo "[Stage16N-R3J] oldjob: $OLDJOB"
echo "[Stage16N-R3J] restart checkpoint: $CHECKPOINT_CYCLE"
echo "[Stage16N-R3J] slope pair: $PREVIOUS_CYCLE -> $CHECKPOINT_CYCLE"
echo "[Stage16N-R3J] material jump: $CHECKPOINT_CYCLE -> $JUMP_CYCLE"
echo "[Stage16N-R3J] target cycle: $TARGET_CYCLE"
echo "[Stage16N-R3J] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R3J] scratch=$ABAQUS_SCRATCH"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${OLDJOB}.${ext}" ]]; then
    echo "Missing native restart source: ${OLDJOB}.${ext}" >&2
    exit 2
  fi
done

if [[ ! -f state.bin || ! -f STAGE16N_R3J_EXTRAPOLATED_STATE.md ]]; then
  rm -f state.bin state.csv STAGE16N_R3J_EXTRAPOLATED_STATE.md
  mkdir -p _jump_state
  abaqus python ../../../stage16n_extract_exact_state_for_reinjection.py \
    --odb "${OLDJOB}.odb" \
    --cycles "$PREVIOUS_CYCLE,$CHECKPOINT_CYCLE" \
    --outdir _jump_state \
    2>&1 | tee "$LOG_DIR/${JOB}_extract_slope_states.log"
  python3 ../../../stage16n_make_extrapolated_state.py \
    --previous-csv "_jump_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \
    --base-csv "_jump_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" \
    --previous-cycle "$PREVIOUS_CYCLE" \
    --base-cycle "$CHECKPOINT_CYCLE" \
    --jump-cycles "$JUMP_CYCLES" \
    --output-cycle "$JUMP_CYCLE" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary STAGE16N_R3J_EXTRAPOLATED_STATE.md \
    2>&1 | tee "$LOG_DIR/${JOB}_make_extrapolated_state.log"
fi

export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
export STAGE16N_JUMP_TARGET_STEP="$TARGET_STEP"
export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_r3_jump_umat.for \
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

abaqus job="$JOB" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_r3_jump_umat.for \
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "$LOG_DIR/${JOB}.log"

grep "STAGE16N_R3J_OVERWRITE" "${JOB}.dat" \
  > "$LOG_DIR/${JOB}_overwrite_trace.txt" || true
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "$LOG_DIR/${JOB}_parallelism_check.log" || true

abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_extract.log"

cd "${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
CASE_DIR="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R3J5_250_to_270_to_500"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_r3j_jump_against_reference.py \
  --jump-metrics "$CASE_DIR/${JOB}_cycle_metrics.csv" \
  --jump-local-states "$CASE_DIR/${JOB}_selected_cycle_local_states.csv" \
  --ref-metrics "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv" \
  --ref-local-states "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv" \
  --cycles "$TARGET_CYCLE" \
  --out-dir "$CASE_DIR" \
  --prefix "$JOB" \
  2>&1 | tee "$CASE_DIR/$LOG_DIR/${JOB}_compare.log"

cd "$CASE_DIR"
{
  echo "# Stage 16N-R3J Jump Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`$JOB\`"
  echo "- Oldjob: \`$OLDJOB\`"
  echo "- Restart checkpoint: \`$CHECKPOINT_CYCLE\`"
  echo "- Slope pair: \`$PREVIOUS_CYCLE -> $CHECKPOINT_CYCLE\`"
  echo "- Material-state jump: \`$CHECKPOINT_CYCLE -> $JUMP_CYCLE\`"
  echo "- Continuation target: \`$TARGET_CYCLE\`"
  echo "- Overwrite trigger: \`JSTEP(1)=$TARGET_STEP, KINC=0, TIME(2)~=$CHECKPOINT_CYCLE\`"
  echo "- Overwritten variables: \`STATEV(1:25)\`"
  echo "- Diagnostic/derived variables not table-overwritten: \`STATEV(26:27)\`"
  if [[ -f "${JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
    echo "- Solver status: \`completed_successfully\`"
  else
    echo "- Solver status: \`check $JOB.sta\`"
  fi
  if [[ -f "${JOB}_comparison_summary.csv" ]]; then
    tail -n +2 "${JOB}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R3J_CASE_STATUS.md

echo "[Stage16N-R3J] end: $(date '+%Y-%m-%d %H:%M:%S')"
