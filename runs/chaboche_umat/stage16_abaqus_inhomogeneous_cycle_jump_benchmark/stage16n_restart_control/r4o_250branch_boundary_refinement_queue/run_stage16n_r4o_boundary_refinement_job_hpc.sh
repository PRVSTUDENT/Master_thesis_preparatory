#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="R4O_250branch_boundary_refinement_queue"
SOURCE_JOB="stage16n_r1b_restart_ref_250cycles"
CHECKPOINT_CYCLE="250"
PREVIOUS_CYCLE="100"
FINAL_CYCLE="500"
TRIGGER_STEP="251"

: "${R4O_CASE_ID:?R4O_CASE_ID is required}"
: "${R4O_TARGET:?R4O_TARGET is required}"
: "${R4O_SOLVED_START:?R4O_SOLVED_START is required}"
R4O_PREV_CASE="${R4O_PREV_CASE:-}"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
CLEAN_HEAVY_AFTER_CLASSIFICATION="${CLEAN_HEAVY_AFTER_CLASSIFICATION:-1}"
SCRATCH9_USER_LIMIT_TB="${SCRATCH9_USER_LIMIT_TB:-5}"
TARGET_JOB="stage16n_r4o_target${R4O_TARGET}_jump_250_to_${R4O_TARGET}_solve_${R4O_SOLVED_START}_to_500"
TARGET_INPUT="${TARGET_JOB}.inp"

mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH" "_source_state"

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
  if [[ -n "${HOME_RESULT_DIR:-}" && -d "${SCRATCH_CASE_DIR:-}" ]]; then
    mkdir -p "$HOME_RESULT_DIR"
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
      "$SCRATCH_CASE_DIR/" "$HOME_RESULT_DIR/"
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

cleanup_heavy_for_job() {
  local job="$1"
  if [[ "$CLEAN_HEAVY_AFTER_CLASSIFICATION" != "1" ]]; then
    return 0
  fi
  find . -maxdepth 1 -type f \( \
    -name "${job}*.odb" -o -name "${job}*.stt" -o -name "${job}*.res" -o \
    -name "${job}*.sim" -o -name "${job}*.mdl" -o -name "${job}*.prt" -o \
    -name "${job}*.dat" -o -name "${job}*.msg" -o -name "${job}*.sta" -o \
    -name "${job}*.023" -o -name "${job}*.cax" -o -name "${job}*.abq" -o \
    -name "${job}*.pac" -o -name "${job}*.sel" -o -name "${job}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
}

cleanup_all_heavy() {
  cleanup_heavy_for_job "$SOURCE_JOB"
  cleanup_heavy_for_job "$TARGET_JOB"
  rm -f state.bin state.csv
}

write_status() {
  local classification="$1"
  local phase="$2"
  local detail="$3"
  {
    echo "# Stage 16N-R4O Job Status"
    echo
    echo "- PBS job: ${PBS_JOBID:-manual}"
    echo "- Controller: $CONTROLLER"
    echo "- Case: $R4O_CASE_ID"
    echo "- Target: $R4O_TARGET"
    echo "- Continuation range: ${R4O_SOLVED_START}-500"
    echo "- Previous case gate: ${R4O_PREV_CASE:-none}"
    echo "- Source job: $SOURCE_JOB"
    echo "- Source package required files: .odb .stt .res .mdl .prt .sim .sta"
    echo "- Continuation restart writing: disabled"
    echo "- R4J9/R4J10: blocked"
    echo "- 505 branch: parked"
    echo "- Classification: $classification"
    echo "- Phase: $phase"
    echo "- Detail: $detail"
    echo "- Heavy copy-back: disabled"
    echo "- Heavy cleanup after classification: enabled"
    echo "- Scratch case dir: ${SCRATCH_CASE_DIR:-$PWD}"
    echo "- Result dir: ${HOME_RESULT_DIR:-unset}"
    echo "- Finished: $(date '+%Y-%m-%d %H:%M:%S')"
  } > "STAGE16N_R4O_${R4O_CASE_ID}_STATUS.md"
}

write_package_manifest() {
  {
    echo "# Stage 16N-R4O Source Package Manifest"
    echo
    echo "- Case: $R4O_CASE_ID"
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
    echo "This package is scratch-only for R4O and is deleted after classification unless a future manifest records a retention reason."
  } > "STAGE16N_R4O_${R4O_CASE_ID}_SOURCE_PACKAGE_MANIFEST.md"
}

write_case_table() {
  local status="$1"
  local summary_file="${TARGET_JOB}_comparison_summary.csv"
  local global=""
  local localerr=""
  local s11=""
  if [[ -f "$summary_file" ]]; then
    IFS=, read -r _ _ global localerr s11 _ < <(awk 'NR==2 {print}' "$summary_file")
  fi
  {
    echo "case_id,target_cycle,skipped_cycles,continuation_range,status,max_global_error_pct,max_primary_local_error_pct,diagnostic_s11_error_pct"
    echo "$R4O_CASE_ID,$R4O_TARGET,$((R4O_TARGET - CHECKPOINT_CYCLE)),${R4O_SOLVED_START}-500,$status,$global,$localerr,$s11"
  } > "STAGE16N_R4O_${R4O_CASE_ID}_CASE_TABLE.csv"
}

scratch9_user_tb() {
  local raw value unit
  raw="$(du -sB1 /scratch9/pr21vyci 2>/dev/null | awk '{print $1}' || true)"
  [[ -n "$raw" ]] || return 1
  awk -v b="$raw" 'BEGIN {printf "%.3f", b/1000000000000.0}'
}

enforce_scratch_gate() {
  df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4o_storage_start_df.txt" || true
  du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4o_storage_start_scratch9_user.txt" || true
  local tb
  tb="$(scratch9_user_tb || true)"
  if [[ -n "$tb" ]] && awk -v used="$tb" -v limit="$SCRATCH9_USER_LIMIT_TB" 'BEGIN {exit used > limit ? 0 : 1}'; then
    write_status "storage_gate_blocked" "preflight" "/scratch9/pr21vyci ${tb}T exceeds ${SCRATCH9_USER_LIMIT_TB}T limit"
    copy_lightweight_evidence
    exit 0
  fi
}

check_previous_gate() {
  if [[ -z "$R4O_PREV_CASE" ]]; then
    return 0
  fi
  local prev_dir="${HOME_CASE_DIR}/${R4O_PREV_CASE}"
  local prev_summary
  prev_summary="$(find "$prev_dir" -maxdepth 1 -type f -name '*_comparison_summary.csv' 2>/dev/null | head -n 1 || true)"
  if [[ -z "$prev_summary" ]]; then
    write_status "skipped_missing_previous_result" "previous_gate" "missing comparison summary for $R4O_PREV_CASE"
    write_case_table "skipped_missing_previous_result"
    copy_lightweight_evidence
    exit 0
  fi
  if ! awk -F, 'NR == 2 && $2 == "pass" {ok=1} END {exit ok ? 0 : 1}' "$prev_summary"; then
    local prev_status
    prev_status="$(awk -F, 'NR == 2 {print $2; exit}' "$prev_summary")"
    write_status "skipped_due_prior_${prev_status:-nonpass}" "previous_gate" "$R4O_PREV_CASE status was ${prev_status:-unknown}"
    write_case_table "skipped_due_prior_${prev_status:-nonpass}"
    copy_lightweight_evidence
    exit 0
  fi
}

prepare_target_state() {
  local jump_cycles=$((R4O_TARGET - CHECKPOINT_CYCLE))
  rm -f state.bin state.csv "STAGE16N_R4O_${R4O_CASE_ID}_TARGET${R4O_TARGET}_EXTRAPOLATED_STATE.md"
  python3 stage16n_make_extrapolated_state.py \
    --previous-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \
    --base-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" \
    --previous-cycle "$PREVIOUS_CYCLE" \
    --base-cycle "$CHECKPOINT_CYCLE" \
    --jump-cycles "$jump_cycles" \
    --output-cycle "$R4O_TARGET" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary "STAGE16N_R4O_${R4O_CASE_ID}_TARGET${R4O_TARGET}_EXTRAPOLATED_STATE.md"
}

run_target_case() {
  prepare_target_state
  export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
  export STAGE16N_JUMP_TARGET_STEP="$TRIGGER_STEP"
  export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

  if ! run_logged_phase "target-${R4O_TARGET} continuation datacheck" "$LOG_DIR/${TARGET_JOB}_datacheck.log" \
    abaqus job="${TARGET_JOB}_datacheck" input="$TARGET_INPUT" oldjob="$SOURCE_JOB" \
      user=stage16n_r3_jump_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$TARGET_JOB"
    write_status "target${R4O_TARGET}_datacheck_failure" "target${R4O_TARGET}_datacheck" "stop escalation"
    write_case_table "datacheck_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  if ! run_logged_phase "target-${R4O_TARGET} continuation solve" "$LOG_DIR/${TARGET_JOB}.log" \
    abaqus job="$TARGET_JOB" input="$TARGET_INPUT" oldjob="$SOURCE_JOB" \
      user=stage16n_r3_jump_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$TARGET_JOB"
    write_status "target${R4O_TARGET}_solve_failure" "target${R4O_TARGET}_solve" "stop escalation"
    write_case_table "solve_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  write_tails "$TARGET_JOB"
  grep "STAGE16N_R3J_OVERWRITE" "${TARGET_JOB}.dat" > "$LOG_DIR/${TARGET_JOB}_overwrite_trace.txt" || true
  grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${TARGET_JOB}.msg" | tee "$LOG_DIR/${TARGET_JOB}_parallelism_check.log" || true

  if ! run_logged_phase "target-${R4O_TARGET} ODB extraction" "$LOG_DIR/${TARGET_JOB}_extract.log" \
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$TARGET_JOB"; then
    write_status "target${R4O_TARGET}_extraction_failure" "target${R4O_TARGET}_extraction" "stop escalation"
    write_case_table "extraction_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  set +e
  phase_time "target-${R4O_TARGET} comparison" \
    python3 stage16n_compare_r3j_jump_against_reference.py \
      --jump-metrics "${TARGET_JOB}_cycle_metrics.csv" \
      --jump-local-states "${TARGET_JOB}_selected_cycle_local_states.csv" \
      --ref-metrics "reference_1000_cycle_metrics.csv" \
      --ref-local-states "reference_1000_selected_cycle_local_states.csv" \
      --cycles "$FINAL_CYCLE" \
      --out-dir "." \
      --prefix "$TARGET_JOB" \
    2>&1 | tee "$LOG_DIR/${TARGET_JOB}_compare.log"
  local compare_rc=${PIPESTATUS[0]}
  set -e

  local classification="review_or_fail"
  if [[ "$compare_rc" -eq 0 && -f "${TARGET_JOB}_comparison_summary.csv" ]]; then
    classification="$(awk -F, 'NR == 2 {print $2; exit}' "${TARGET_JOB}_comparison_summary.csv")"
  fi
  tail -n +1 "${TARGET_JOB}_comparison_summary.csv" > "STAGE16N_R4O_${R4O_CASE_ID}_TARGET${R4O_TARGET}_COMPARISON_SUMMARY.txt" || true
  write_case_table "$classification"
  write_status "target${R4O_TARGET}_${classification}" "target${R4O_TARGET}_comparison" "comparison completed with status ${classification}"
  copy_lightweight_evidence
  cleanup_heavy_for_job "$TARGET_JOB"
  copy_lightweight_evidence
}

on_error() {
  local rc=$?
  write_tails "$SOURCE_JOB"
  write_tails "$TARGET_JOB"
  write_status "controller_failure" "trap" "exit code $rc"
  copy_lightweight_evidence
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
}
trap on_error ERR
trap copy_lightweight_evidence EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4O] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4O] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4O] case=$R4O_CASE_ID target=$R4O_TARGET solved_start=$R4O_SOLVED_START prev=${R4O_PREV_CASE:-none}"
echo "[Stage16N-R4O] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R4O] scratch=${SCRATCH_CASE_DIR:-$PWD}"

for required in \
  "${SOURCE_JOB}.inp" \
  "$TARGET_INPUT" \
  "reference_1000_cycle_metrics.csv" \
  "reference_1000_selected_cycle_local_states.csv" \
  "stage16n_neml_equivalent_chaboche_umat.for" \
  "stage16n_r3_jump_umat.for" \
  "stage16n_extract_hysteresis_and_local_states.py" \
  "stage16n_extract_exact_state_for_reinjection.py" \
  "stage16n_make_extrapolated_state.py" \
  "stage16n_compare_r3j_jump_against_reference.py"; do
  test -s "$required"
done

enforce_scratch_gate
check_previous_gate

if ! run_logged_phase "source datacheck" "$LOG_DIR/${SOURCE_JOB}_datacheck.log" \
  abaqus job="${SOURCE_JOB}_datacheck" input="${SOURCE_JOB}.inp" \
    user=stage16n_neml_equivalent_chaboche_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
  write_tails "$SOURCE_JOB"
  write_status "source_datacheck_failure" "source_datacheck" "source package was not generated"
  write_case_table "source_datacheck_failure"
  copy_lightweight_evidence
  cleanup_all_heavy
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
  write_case_table "source_solve_failure"
  copy_lightweight_evidence
  cleanup_all_heavy
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
  write_case_table "source_package_invalid"
  copy_lightweight_evidence
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
fi

R1B_RESTART_INC="$(awk -v step="$CHECKPOINT_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${SOURCE_JOB}.sta")"
echo "[Stage16N-R4O] source restart row: STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"

if ! run_logged_phase "source state extraction" "$LOG_DIR/${SOURCE_JOB}_extract_state_100_250.log" \
  abaqus python stage16n_extract_exact_state_for_reinjection.py \
    --odb "${SOURCE_JOB}.odb" \
    --cycles "${PREVIOUS_CYCLE},${CHECKPOINT_CYCLE}" \
    --outdir _source_state; then
  write_status "source_state_extraction_failure" "source_state_extraction" "cannot prepare target states"
  write_case_table "source_state_extraction_failure"
  copy_lightweight_evidence
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
fi

run_target_case
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4o_storage_end_df.txt" || true
du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4o_storage_end_scratch9_user.txt" || true
cleanup_all_heavy
copy_lightweight_evidence
echo "[Stage16N-R4O] end: $(date '+%Y-%m-%d %H:%M:%S')"
