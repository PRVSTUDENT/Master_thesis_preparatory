#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r3e2_exact_overwrite_500_to_750_a2"
OLDJOB="stage16n_r1a_restart_ref_500cycles"
CHECKPOINT_CYCLE="500"
TARGET_CYCLE="750"
TARGET_STEP="501"

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

echo "[Stage16N-R3E] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R3E] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R3E] Abaqus job: $JOB"
echo "[Stage16N-R3E] oldjob: $OLDJOB"
echo "[Stage16N-R3E] checkpoint cycle: $CHECKPOINT_CYCLE"
echo "[Stage16N-R3E] target cycle: $TARGET_CYCLE"
echo "[Stage16N-R3E] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R3E] scratch=$ABAQUS_SCRATCH"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${OLDJOB}.${ext}" ]]; then
    echo "Missing native restart source: ${OLDJOB}.${ext}" >&2
    exit 2
  fi
done

if [[ ! -f state.bin ]]; then
  mkdir -p _overwrite_state
  abaqus python ../../../stage16n_extract_exact_state_for_reinjection.py \
    --odb "${OLDJOB}.odb" \
    --cycles "$CHECKPOINT_CYCLE" \
    --outdir _overwrite_state \
    2>&1 | tee "$LOG_DIR/${JOB}_extract_exact_state.log"
  cp "_overwrite_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").bin" state.bin
  cp "_overwrite_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" state.csv
fi

export STAGE16N_OVERWRITE_STATE_BIN="$PWD/state.bin"
export STAGE16N_OVERWRITE_TARGET_STEP="$TARGET_STEP"
export STAGE16N_OVERWRITE_CHECK_TIME="$CHECKPOINT_CYCLE"

abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_r3_exact_overwrite_umat.for \
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

abaqus job="$JOB" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_r3_exact_overwrite_umat.for \
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "$LOG_DIR/${JOB}.log"

grep "STAGE16N_R3E_OVERWRITE" "${JOB}.msg" \
  > "$LOG_DIR/${JOB}_overwrite_trace.txt" || true
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "$LOG_DIR/${JOB}_parallelism_check.log" || true

abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
  2>&1 | tee "$LOG_DIR/${JOB}_extract.log"

cd "${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
CASE_DIR="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_exact_overwrite_cases/R3E2_500_to_750_exact_overwrite"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_native_restart_against_1000ref.py \
  --restart-metrics "$CASE_DIR/${JOB}_cycle_metrics.csv" \
  --restart-local-states "$CASE_DIR/${JOB}_selected_cycle_local_states.csv" \
  --cycles "$TARGET_CYCLE" \
  --out-dir "$CASE_DIR" \
  --prefix stage16n_r3e_exact_overwrite \
  2>&1 | tee "$CASE_DIR/$LOG_DIR/${JOB}_compare.log"

cd "$CASE_DIR"
{
  echo "# Stage 16N-R3E Exact Overwrite Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`$JOB\`"
  echo "- Oldjob: \`$OLDJOB\`"
  echo "- Restart interval: \`$CHECKPOINT_CYCLE -> $TARGET_CYCLE\`"
  echo "- Overwrite trigger: \`JSTEP(1)=$TARGET_STEP, KINC=0, TIME(2)~=$CHECKPOINT_CYCLE\`"
  echo "- Overwritten variables: \`STATEV(1:25)\`"
  echo "- Derived/diagnostic variables not table-overwritten: \`STATEV(26:27)\`"
  if [[ -f "${JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
    echo "- Solver status: \`completed_successfully\`"
  else
    echo "- Solver status: \`check $JOB.sta\`"
  fi
  if [[ -f stage16n_r3e_exact_overwrite_comparison_summary.csv ]]; then
    tail -n +2 stage16n_r3e_exact_overwrite_comparison_summary.csv | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R3E_CASE_STATUS.md

echo "[Stage16N-R3E] end: $(date '+%Y-%m-%d %H:%M:%S')"
