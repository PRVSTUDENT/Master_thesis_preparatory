#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="R4M_250branch_compact_restart_source_controller"
SOURCE_JOB="stage16n_r1b_restart_ref_250cycles"
TARGET_JOB="stage16n_r4m_target270_jump_250_to_270_solve_271_to_500"
TARGET_INPUT="stage16n_r4m_target270_jump_250_to_270_solve_271_to_500.inp"
CHECKPOINT_CYCLE="250"
FINAL_CYCLE="500"
JUMP_CYCLE="270"
TRIGGER_STEP="251"
SOLVED_CYCLE="271"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
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
      --include='*.log' \
      --include='*.out' \
      --include='*.pbs.out' \
      --exclude='*.sta' \
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

write_tails() {
  local job="$1"
  local suffix
  for suffix in "" "_datacheck"; do
    local base="${job}${suffix}"
    [[ -f "${base}.dat" ]] && tail -n 220 "${base}.dat" > "${base}_dat_tail.txt" || true
    [[ -f "${base}.msg" ]] && tail -n 220 "${base}.msg" > "${base}_msg_tail.txt" || true
    [[ -f "${base}.sta" ]] && tail -n 120 "${base}.sta" > "${base}_sta_tail.txt" || true
  done
}

cleanup_heavy_files() {
  if [[ "$CLEAN_HEAVY_AFTER_CLASSIFICATION" != "1" ]]; then
    return 0
  fi
  find . -maxdepth 1 -type f \( \
    -name "${SOURCE_JOB}*.odb" -o -name "${SOURCE_JOB}*.stt" -o -name "${SOURCE_JOB}*.res" -o \
    -name "${SOURCE_JOB}*.sim" -o -name "${SOURCE_JOB}*.mdl" -o -name "${SOURCE_JOB}*.prt" -o \
    -name "${SOURCE_JOB}*.dat" -o -name "${SOURCE_JOB}*.msg" -o -name "${SOURCE_JOB}*.sta" -o \
    -name "${SOURCE_JOB}*.023" -o -name "${SOURCE_JOB}*.cax" -o -name "${SOURCE_JOB}*.abq" -o \
    -name "${SOURCE_JOB}*.pac" -o -name "${SOURCE_JOB}*.sel" -o -name "${SOURCE_JOB}*.lck" -o \
    -name "${TARGET_JOB}*.odb" -o -name "${TARGET_JOB}*.stt" -o -name "${TARGET_JOB}*.res" -o \
    -name "${TARGET_JOB}*.sim" -o -name "${TARGET_JOB}*.mdl" -o -name "${TARGET_JOB}*.prt" -o \
    -name "${TARGET_JOB}*.dat" -o -name "${TARGET_JOB}*.msg" -o -name "${TARGET_JOB}*.sta" -o \
    -name "${TARGET_JOB}*.023" -o -name "${TARGET_JOB}*.cax" -o -name "${TARGET_JOB}*.abq" -o \
    -name "${TARGET_JOB}*.pac" -o -name "${TARGET_JOB}*.sel" -o -name "${TARGET_JOB}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
  rm -f state.bin state.csv
}

write_status() {
  local classification="$1"
  local phase="$2"
  local detail="$3"
  {
    echo "# Stage 16N-R4M Controller Status"
    echo
    echo "- PBS job: ${PBS_JOBID:-manual}"
    echo "- Controller: $CONTROLLER"
    echo "- Source job: $SOURCE_JOB"
    echo "- Target job: $TARGET_JOB"
    echo "- Source package basename: $SOURCE_JOB"
    echo "- Source package required files: .odb .stt .res .mdl .prt .sim .sta"
    echo "- Target: 250 -> 270 -> 500"
    echo "- Continuation restart writing: disabled"
    echo "- R4J9/R4J10: blocked"
    echo "- 505 branch: parked"
    echo "- Classification: $classification"
    echo "- Phase: $phase"
    echo "- Detail: $detail"
    echo "- Scientific result: none unless comparison CSV says pass/review/fail"
    echo "- Heavy copy-back: disabled"
    echo "- Heavy cleanup after classification: enabled"
    echo "- Scratch case dir: ${SCRATCH_CASE_DIR:-$PWD}"
    echo "- Finished: $(date '+%Y-%m-%d %H:%M:%S')"
  } > STAGE16N_R4M_CONTROLLER_STATUS.md
}

write_package_manifest() {
  {
    echo "# Stage 16N-R4M Source Package Manifest"
    echo
    echo "- Source basename: $SOURCE_JOB"
    echo "- Scratch case dir: ${SCRATCH_CASE_DIR:-$PWD}"
    echo "- Created: $(date '+%Y-%m-%d %H:%M:%S')"
    echo
    echo "| extension | size | path |"
    echo "| --- | ---: | --- |"
    for ext in odb stt res mdl prt sim sta; do
      local file="${SOURCE_JOB}.${ext}"
      if [[ -e "$file" ]]; then
        local size
        size="$(du -h "$file" | awk '{print $1}')"
        echo "| .$ext | $size | $file |"
      else
        echo "| .$ext | missing | $file |"
      fi
    done
    echo
    echo "This package is scratch-only for R4M. If retained after classification, record it in the heavy retention manifest with size and deletion condition."
  } > STAGE16N_R4M_SOURCE_PACKAGE_MANIFEST.md
}

csv_to_state_bin() {
  local csv_path="$1"
  local bin_path="$2"
  python3 - <<PY
import csv
import struct
from pathlib import Path
csv_path = Path("$csv_path")
bin_path = Path("$bin_path")
rows = []
with csv_path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        noel = int(row["NOEL"])
        npt = int(row["NPT"])
        values = [float(row.get(f"S{i}") or 0.0) for i in range(1, 7)]
        values.extend(float(row[f"SDV{i}"]) for i in range(1, 28))
        rows.append((noel, npt, values))
max_record = max((noel - 1) * 8 + npt for noel, npt, _ in rows)
with bin_path.open("wb") as handle:
    handle.truncate(max_record * 33 * 8)
    for noel, npt, values in rows:
        recno = (noel - 1) * 8 + npt
        handle.seek((recno - 1) * 33 * 8)
        handle.write(struct.pack("<33d", *values))
PY
}

use_cached_jump_state() {
  local cache_dir=""
  for candidate in \
    "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4J3_250_to_270_solve_271_to_500" \
    "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R3J5_250_to_270_to_500"; do
    if [[ -f "$candidate/state.csv" ]]; then
      cache_dir="$candidate"
      break
    fi
  done
  if [[ -z "$cache_dir" ]]; then
    echo "[Stage16N-R4M] missing cached target-270 jump state" >&2
    return 10
  fi
  rm -f state.bin state.csv
  cp "$cache_dir/state.csv" state.csv
  if [[ -f "$cache_dir/state.bin" ]]; then
    cp "$cache_dir/state.bin" state.bin
  else
    csv_to_state_bin state.csv state.bin
  fi
  echo "[Stage16N-R4M] using cached target-270 jump state from $cache_dir"
}

on_error() {
  local rc=$?
  write_tails "$SOURCE_JOB"
  write_tails "$TARGET_JOB"
  write_status "controller_failure" "trap" "exit code $rc"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit "$rc"
}
trap on_error ERR
trap copy_lightweight_evidence EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4M] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4M] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4M] controller: $CONTROLLER"
echo "[Stage16N-R4M] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R4M] scratch=${SCRATCH_CASE_DIR:-$PWD}"
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4m_storage_start_df.txt" || true
du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4m_storage_start_scratch9_user.txt" || true

for required in \
  "${SOURCE_JOB}.inp" \
  "$TARGET_INPUT" \
  "stage16n_neml_equivalent_chaboche_umat.for" \
  "stage16n_r3_jump_umat.for" \
  "stage16n_extract_hysteresis_and_local_states.py" \
  "stage16n_compare_r3j_jump_against_reference.py"; do
  test -s "$required"
done

if ! run_logged_phase "source datacheck" "$LOG_DIR/${SOURCE_JOB}_datacheck.log" \
  abaqus job="${SOURCE_JOB}_datacheck" input="${SOURCE_JOB}.inp" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
  write_tails "$SOURCE_JOB"
  write_status "source_datacheck_failure" "source_datacheck" "source package was not generated"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

if ! run_logged_phase "source solve" "$LOG_DIR/${SOURCE_JOB}.log" \
  abaqus job="$SOURCE_JOB" input="${SOURCE_JOB}.inp" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
  write_tails "$SOURCE_JOB"
  write_status "source_solve_failure" "source_solve" "source package incomplete"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

write_tails "$SOURCE_JOB"
write_package_manifest
for ext in odb stt res mdl prt sim sta; do
  test -s "${SOURCE_JOB}.${ext}"
done
if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${SOURCE_JOB}.sta"; then
  write_status "source_package_invalid" "source_validation" "source sta does not show clean completion"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

R1B_RESTART_INC="$(awk -v step="$CHECKPOINT_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${SOURCE_JOB}.sta")"
echo "[Stage16N-R4M] source restart row: STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"

if ! use_cached_jump_state; then
  write_status "blocked_missing_cached_jump_state" "pre_target_datacheck" "target-270 cached state missing"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
export STAGE16N_JUMP_TARGET_STEP="$TRIGGER_STEP"
export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

if ! run_logged_phase "target-270 continuation datacheck" "$LOG_DIR/${TARGET_JOB}_datacheck.log" \
  abaqus job="${TARGET_JOB}_datacheck" input="$TARGET_INPUT" oldjob="$SOURCE_JOB" \
    user=stage16n_r3_jump_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
  write_tails "$TARGET_JOB"
  write_status "target270_datacheck_failure" "target270_datacheck" "source package generated but continuation datacheck failed"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

if ! run_logged_phase "target-270 continuation solve" "$LOG_DIR/${TARGET_JOB}.log" \
  abaqus job="$TARGET_JOB" input="$TARGET_INPUT" oldjob="$SOURCE_JOB" \
    user=stage16n_r3_jump_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
  write_tails "$TARGET_JOB"
  write_status "target270_solve_failure" "target270_solve" "continuation failed before comparison"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

write_tails "$TARGET_JOB"
grep "STAGE16N_R3J_OVERWRITE" "${TARGET_JOB}.dat" > "$LOG_DIR/${TARGET_JOB}_overwrite_trace.txt" || true
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${TARGET_JOB}.msg" | tee "$LOG_DIR/${TARGET_JOB}_parallelism_check.log" || true

if ! run_logged_phase "target-270 ODB extraction" "$LOG_DIR/${TARGET_JOB}_extract.log" \
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$TARGET_JOB"; then
  write_status "target270_extraction_failure" "target270_extraction" "continuation solved but extraction failed"
  copy_lightweight_evidence
  cleanup_heavy_files
  copy_lightweight_evidence
  exit 0
fi

set +e
phase_time "target-270 comparison" \
  python3 stage16n_compare_r3j_jump_against_reference.py \
    --jump-metrics "${TARGET_JOB}_cycle_metrics.csv" \
    --jump-local-states "${TARGET_JOB}_selected_cycle_local_states.csv" \
    --ref-metrics "reference_1000_cycle_metrics.csv" \
    --ref-local-states "reference_1000_selected_cycle_local_states.csv" \
    --cycles "$FINAL_CYCLE" \
    --out-dir "." \
    --prefix "$TARGET_JOB" \
  2>&1 | tee "$LOG_DIR/${TARGET_JOB}_compare.log"
compare_rc=${PIPESTATUS[0]}
set -e

classification="review_or_fail"
if [[ "$compare_rc" -eq 0 && -f "${TARGET_JOB}_comparison_summary.csv" ]] && awk -F, 'NR == 2 && $2 == "pass" {ok=1} END {exit ok ? 0 : 1}' "${TARGET_JOB}_comparison_summary.csv"; then
  classification="pass"
elif [[ "$compare_rc" -eq 0 && -f "${TARGET_JOB}_comparison_summary.csv" ]]; then
  classification="$(awk -F, 'NR == 2 {print $2; exit}' "${TARGET_JOB}_comparison_summary.csv")"
fi

write_status "target270_${classification}" "target270_comparison" "comparison completed with status ${classification}"
if [[ -f "${TARGET_JOB}_comparison_summary.csv" ]]; then
  tail -n +1 "${TARGET_JOB}_comparison_summary.csv" > STAGE16N_R4M_TARGET270_COMPARISON_SUMMARY.txt
fi
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4m_storage_end_df.txt" || true
du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4m_storage_end_scratch9_user.txt" || true
copy_lightweight_evidence
cleanup_heavy_files
copy_lightweight_evidence
echo "[Stage16N-R4M] target-270 classification: $classification"
echo "[Stage16N-R4M] end: $(date '+%Y-%m-%d %H:%M:%S')"
