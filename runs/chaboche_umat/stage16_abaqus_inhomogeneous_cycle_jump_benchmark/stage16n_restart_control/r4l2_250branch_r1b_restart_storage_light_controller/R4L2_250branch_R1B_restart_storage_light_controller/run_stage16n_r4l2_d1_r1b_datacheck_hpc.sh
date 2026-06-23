#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="stage16n_r4l2_d1_r1b_datacheck"
OLDJOB="stage16n_r1b_restart_ref_250cycles"
CHECKPOINT_CYCLE="250"
LABEL="R4L2_D1"
JOB="stage16n_r4l2_d1_r1b_jump_250_to_270_datacheck"
INPUT="stage16n_r4l2_1_r1b_jump_250_to_270_solve_271_to_500.inp"
JUMP_CYCLE="270"
TRIGGER_STEP="251"
SOLVED_CYCLE="271"

ABAQUS_CPUS="${ABAQUS_CPUS:-8}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
CLEAN_HEAVY_AFTER_CLASSIFICATION="${CLEAN_HEAVY_AFTER_CLASSIFICATION:-1}"
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
  return "$rc"
}

run_logged_phase() {
  local label="$1"
  local logfile="$2"
  shift 2
  set +e
  phase_time "$label" "$@" 2>&1 | tee "$logfile"
  local rc=${PIPESTATUS[0]}
  set -e
  return "$rc"
}

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${SCRATCH_CASE_DIR:-}" ]]; then
    mkdir -p "$HOME_CASE_DIR"
    rsync -av \
      --include='*/' \
      --exclude='state.bin' \
      --exclude='state.csv' \
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
      --exclude='*.023' \
      --exclude='*.cax' \
      --exclude='*.abq' \
      --exclude='*.pac' \
      --exclude='*.sel' \
      --exclude='*.lck' \
      --exclude='*' \
      "$SCRATCH_CASE_DIR/" "$HOME_CASE_DIR/"
  fi
}

cleanup_case_heavy() {
  if [[ "$CLEAN_HEAVY_AFTER_CLASSIFICATION" != "1" ]]; then
    return 0
  fi
  find . -maxdepth 1 -type f \( \
    -name "${JOB}*.odb" -o -name "${JOB}*.stt" -o -name "${JOB}*.res" -o \
    -name "${JOB}*.sim" -o -name "${JOB}*.mdl" -o -name "${JOB}*.prt" -o \
    -name "${JOB}*.dat" -o -name "${JOB}*.msg" -o -name "${JOB}*.023" -o \
    -name "${JOB}*.cax" -o -name "${JOB}*.abq" -o -name "${JOB}*.pac" -o \
    -name "${JOB}*.sel" -o -name "${JOB}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
  rm -f state.bin state.csv
}

write_evidence_tails() {
  local base="${JOB}_datacheck"
  [[ -f "${base}.dat" ]] && tail -n 220 "${base}.dat" > "${JOB}_datacheck_dat_tail.txt" || true
  [[ -f "${base}.msg" ]] && tail -n 220 "${base}.msg" > "${JOB}_datacheck_msg_tail.txt" || true
  [[ -f "${base}.log" ]] && cp "${base}.log" "${JOB}_datacheck.log.txt" || true
  [[ -f "${JOB}.dat" ]] && tail -n 220 "${JOB}.dat" > "${JOB}_dat_tail.txt" || true
  [[ -f "${JOB}.msg" ]] && tail -n 220 "${JOB}.msg" > "${JOB}_msg_tail.txt" || true
}

write_status() {
  local classification="$1"
  local failed_phase="$2"
  local rc="$3"
  export R4L2_D1_PBS_JOB="${PBS_JOBID:-manual}"
  export R4L2_D1_CONTROLLER="$CONTROLLER"
  export R4L2_D1_OLDJOB="$OLDJOB"
  export R4L2_D1_RESTART_ROW="STEP=$CHECKPOINT_CYCLE, INC=${R1B_RESTART_INC:-unknown}"
  export R4L2_D1_LABEL="$LABEL"
  export R4L2_D1_JOB="$JOB"
  export R4L2_D1_CLASSIFICATION="$classification"
  export R4L2_D1_FAILED_PHASE="$failed_phase"
  export R4L2_D1_EXIT_CODE="$rc"
  export R4L2_D1_JUMP_CYCLE="$JUMP_CYCLE"
  export R4L2_D1_TRIGGER_STEP="$TRIGGER_STEP"
  export R4L2_D1_SOLVED_CYCLE="$SOLVED_CYCLE"
  python3 - <<'PY'
import os
from datetime import datetime
from pathlib import Path

lines = [
    "# Stage 16N-R4L2-D1 Datacheck Diagnostic Status",
    "",
    f"- PBS job: `{os.environ['R4L2_D1_PBS_JOB']}`",
    f"- Controller: `{os.environ['R4L2_D1_CONTROLLER']}`",
    f"- Case: `{os.environ['R4L2_D1_LABEL']}`",
    f"- Job: `{os.environ['R4L2_D1_JOB']}`",
    f"- Oldjob: `{os.environ['R4L2_D1_OLDJOB']}`",
    "- Purpose: `R1B preflight plus target-270 input-processor datacheck only`",
    f"- Restart read: `{os.environ['R4L2_D1_RESTART_ROW']}`",
    f"- True-jump target: `{os.environ['R4L2_D1_JUMP_CYCLE']}`",
    f"- Overwrite trigger step: `{os.environ['R4L2_D1_TRIGGER_STEP']}`",
    f"- First solved cycle if later allowed: `{os.environ['R4L2_D1_SOLVED_CYCLE']}`",
    "- Continuation solve: `not_allowed_in_D1`",
    "- R1A usage: `disabled`",
    "- Source ODB dependency: `disabled`",
    f"- Classification: `{os.environ['R4L2_D1_CLASSIFICATION']}`",
    f"- Failed phase: `{os.environ['R4L2_D1_FAILED_PHASE']}`",
    f"- Exit code: `{os.environ['R4L2_D1_EXIT_CODE']}`",
    "- Scientific result: `none`",
    "- Evidence tails: `stage16n_r4l2_d1_r1b_jump_250_to_270_datacheck_dat_tail.txt`, `stage16n_r4l2_d1_r1b_jump_250_to_270_datacheck_msg_tail.txt`, logs if present",
    "- Heavy cleanup after classification: `enabled`",
    f"- Finished: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
    "",
]
Path("STAGE16N_R4L2_D1_DIAGNOSTIC_STATUS.md").write_text("\n".join(lines), encoding="utf-8")
PY
}

on_error() {
  local rc=$?
  write_evidence_tails
  write_status "controller_or_preflight_failure" "controller_error" "$rc"
  copy_lightweight_evidence
  cleanup_case_heavy
  copy_lightweight_evidence
  exit "$rc"
}
trap on_error ERR
trap copy_lightweight_evidence EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4L2-D1] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4L2-D1] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4L2-D1] oldjob: $OLDJOB"
echo "[Stage16N-R4L2-D1] datacheck only; continuation solve disabled"
echo "[Stage16N-R4L2-D1] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

bash link_r1b_restart_sources.sh
for ext in stt res mdl prt sim sta; do
  test -e "${OLDJOB}.${ext}"
done

R1B_RESTART_INC="$(awk -v step="$CHECKPOINT_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${OLDJOB}.sta")"
echo "[Stage16N-R4L2-D1] R1B restart row: STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"

rm -f state.bin state.csv STAGE16N_R3J_EXTRAPOLATED_STATE.md
CACHE_DIR=""
for candidate in \
  "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4J3_250_to_270_solve_271_to_500" \
  "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R3J5_250_to_270_to_500"; do
  if [[ -f "$candidate/state.csv" ]]; then
    CACHE_DIR="$candidate"
    break
  fi
done
if [[ -z "$CACHE_DIR" ]]; then
  echo "[Stage16N-R4L2-D1] no cached jump state available for target $JUMP_CYCLE" >&2
  write_status "blocked_missing_cached_jump_state" "pre_datacheck_cache_lookup" "10"
  copy_lightweight_evidence
  exit 0
fi

cp "$CACHE_DIR/state.csv" state.csv
if [[ -f "$CACHE_DIR/state.bin" ]]; then
  cp "$CACHE_DIR/state.bin" state.bin
else
  python3 - <<'PY'
import csv
import struct
from pathlib import Path

rows = []
with Path("state.csv").open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        noel = int(row["NOEL"])
        npt = int(row["NPT"])
        values = [float(row.get(f"S{i}") or 0.0) for i in range(1, 7)]
        values.extend(float(row[f"SDV{i}"]) for i in range(1, 28))
        rows.append((noel, npt, values))
max_record = max((noel - 1) * 8 + npt for noel, npt, _ in rows)
with Path("state.bin").open("wb") as handle:
    handle.truncate(max_record * 33 * 8)
    for noel, npt, values in rows:
        recno = (noel - 1) * 8 + npt
        handle.seek((recno - 1) * 33 * 8)
        handle.write(struct.pack("<33d", *values))
PY
fi

export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
export STAGE16N_JUMP_TARGET_STEP="$TRIGGER_STEP"
export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

echo "[Stage16N-R4L2-D1] cached jump state: $CACHE_DIR"
echo "[Stage16N-R4L2-D1] restart read: oldjob=$OLDJOB STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"
echo "[Stage16N-R4L2-D1] overwrite trigger: JSTEP(1)=$TRIGGER_STEP KINC=0 TIME(2)=$CHECKPOINT_CYCLE"

if run_logged_phase "$LABEL continuation datacheck" "$LOG_DIR/${JOB}_datacheck.log" \
  abaqus job="${JOB}_datacheck" input="$INPUT" oldjob="$OLDJOB" \
    user=stage16n_r3_jump_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
  write_evidence_tails
  write_status "datacheck_passed_solve_not_run" "none" "0"
  copy_lightweight_evidence
  cleanup_case_heavy
  copy_lightweight_evidence
  echo "[Stage16N-R4L2-D1] datacheck passed; production solve remains blocked pending explicit approval."
else
  rc=$?
  write_evidence_tails
  write_status "infrastructure_input_processor_failure" "continuation_datacheck" "$rc"
  copy_lightweight_evidence
  cleanup_case_heavy
  copy_lightweight_evidence
  echo "[Stage16N-R4L2-D1] datacheck failed; production solve remains blocked."
fi

echo "[Stage16N-R4L2-D1] end: $(date '+%Y-%m-%d %H:%M:%S')"
