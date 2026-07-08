#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="R4P_boundary_reproducibility_and_diagnostics"
SOURCE_JOB="stage16n_r1b_restart_ref_250cycles"
CHECKPOINT_CYCLE="250"
PREVIOUS_CYCLE="100"
FINAL_CYCLE="500"
TRIGGER_STEP="251"

: "${R4P_CASE_ID:?R4P_CASE_ID is required}"
: "${R4P_TARGET:?R4P_TARGET is required}"
: "${R4P_SOLVED_START:?R4P_SOLVED_START is required}"
R4P_PREV_CASE="${R4P_PREV_CASE:-}"
R4P_MODE="${R4P_MODE:-jump}"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
CLEAN_HEAVY_AFTER_CLASSIFICATION="${CLEAN_HEAVY_AFTER_CLASSIFICATION:-1}"
SCRATCH9_USER_LIMIT_TB="${SCRATCH9_USER_LIMIT_TB:-5}"
TARGET_JOB="stage16n_r4p_target${R4P_TARGET}_jump_250_to_${R4P_TARGET}_solve_${R4P_SOLVED_START}_to_500"
TARGET_INPUT="${TARGET_JOB}.inp"
EXACT_SOURCE_JOB="stage16n_r4p_target272_exact_native_source_250_to_272"
EXACT_TARGET_JOB="stage16n_r4p_target272_exact_native_continue_273_to_500"
EXACT_TARGET_TEMPLATE="stage16n_r4p_target272_exact_native_continue_273_to_500.inp"

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
  cleanup_heavy_for_job "$EXACT_SOURCE_JOB"
  cleanup_heavy_for_job "$EXACT_TARGET_JOB"
  rm -f state.bin state.csv
}

write_status() {
  local classification="$1"
  local phase="$2"
  local detail="$3"
  {
    echo "# Stage 16N-R4P Job Status"
    echo
    echo "- PBS job: ${PBS_JOBID:-manual}"
    echo "- Controller: $CONTROLLER"
    echo "- Case: $R4P_CASE_ID"
    echo "- Target: $R4P_TARGET"
    echo "- Mode: $R4P_MODE"
    echo "- Continuation range: ${R4P_SOLVED_START}-500"
    echo "- Previous case recorded: ${R4P_PREV_CASE:-none}"
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
  } > "STAGE16N_R4P_${R4P_CASE_ID}_STATUS.md"
}

write_package_manifest() {
  {
    echo "# Stage 16N-R4P Source Package Manifest"
    echo
    echo "- Case: $R4P_CASE_ID"
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
    echo "This package is scratch-only for R4P and is deleted after classification unless a future manifest records a retention reason."
  } > "STAGE16N_R4P_${R4P_CASE_ID}_SOURCE_PACKAGE_MANIFEST.md"
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
    echo "$R4P_CASE_ID,$R4P_TARGET,$((R4P_TARGET - CHECKPOINT_CYCLE)),${R4P_SOLVED_START}-500,$status,$global,$localerr,$s11"
  } > "STAGE16N_R4P_${R4P_CASE_ID}_CASE_TABLE.csv"
}

scratch9_user_tb() {
  local raw value unit
  raw="$(du -sB1 /scratch9/pr21vyci 2>/dev/null | awk '{print $1}' || true)"
  [[ -n "$raw" ]] || return 1
  awk -v b="$raw" 'BEGIN {printf "%.3f", b/1000000000000.0}'
}

enforce_scratch_gate() {
  df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/R4P_storage_start_df.txt" || true
  du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/R4P_storage_start_scratch9_user.txt" || true
  local tb
  tb="$(scratch9_user_tb || true)"
  if [[ -n "$tb" ]] && awk -v used="$tb" -v limit="$SCRATCH9_USER_LIMIT_TB" 'BEGIN {exit used > limit ? 0 : 1}'; then
    write_status "storage_gate_blocked" "preflight" "/scratch9/pr21vyci ${tb}T exceeds ${SCRATCH9_USER_LIMIT_TB}T limit"
    copy_lightweight_evidence
    exit 0
  fi
}

check_previous_gate() {
  if [[ -z "$R4P_PREV_CASE" ]]; then
    echo "previous_case,previous_status,previous_summary" > "STAGE16N_R4P_${R4P_CASE_ID}_PREVIOUS_CASE_STATUS.csv"
    echo "none,none,none" >> "STAGE16N_R4P_${R4P_CASE_ID}_PREVIOUS_CASE_STATUS.csv"
    return 0
  fi
  local prev_dir="${HOME_CASE_DIR}/${R4P_PREV_CASE}"
  local prev_summary
  prev_summary="$(find "$prev_dir" -maxdepth 1 -type f -name '*_comparison_summary.csv' 2>/dev/null | head -n 1 || true)"
  local prev_status="missing"
  [[ -n "$prev_summary" ]] && prev_status="$(awk -F, 'NR == 2 {print $2; exit}' "$prev_summary")"
  echo "previous_case,previous_status,previous_summary" > "STAGE16N_R4P_${R4P_CASE_ID}_PREVIOUS_CASE_STATUS.csv"
  echo "$R4P_PREV_CASE,${prev_status:-unknown},${prev_summary:-missing}" >> "STAGE16N_R4P_${R4P_CASE_ID}_PREVIOUS_CASE_STATUS.csv"
  echo "[Stage16N-R4P] previous case recorded: $R4P_PREV_CASE status=${prev_status:-unknown}"
}

write_diagnostic_summary() {
  local job="$1"
  local out="STAGE16N_R4P_${R4P_CASE_ID}_DIAGNOSTIC_SUMMARY.csv"
  echo "case_id,mode,target_cycle,source_file,matched_line" > "$out"
  for file in "${job}_comparison_details.csv" "${job}_cycle_metrics.csv" "${job}_selected_cycle_local_states.csv"; do
    [[ -f "$file" ]] || continue
    awk -v case_id="$R4P_CASE_ID" -v mode="$R4P_MODE" -v target="$R4P_TARGET" -v src="$file" '
      BEGIN {IGNORECASE=1}
      /HOLE_RING_SDV8|HOLE_RING_S11|MISES|RF1|selected|local/ {
        gsub(/"/, "\"\"", $0);
        print case_id "," mode "," target "," src ",\"" $0 "\""
      }
    ' "$file" >> "$out"
  done
}

run_compare_and_classify() {
  local job="$1"
  local label="$2"
  if ! run_logged_phase "${label} ODB extraction" "$LOG_DIR/${job}_extract.log" \
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$job"; then
    write_status "${label}_extraction_failure" "${label}_extraction" "stop escalation"
    write_case_table "extraction_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$job"
    copy_lightweight_evidence
    return 0
  fi

  set +e
  phase_time "${label} comparison" \
    python3 stage16n_compare_r3j_jump_against_reference.py \
      --jump-metrics "${job}_cycle_metrics.csv" \
      --jump-local-states "${job}_selected_cycle_local_states.csv" \
      --ref-metrics "reference_1000_cycle_metrics.csv" \
      --ref-local-states "reference_1000_selected_cycle_local_states.csv" \
      --cycles "$FINAL_CYCLE" \
      --out-dir "." \
      --prefix "$job" \
    2>&1 | tee "$LOG_DIR/${job}_compare.log"
  local compare_rc=${PIPESTATUS[0]}
  set -e

  local classification="review_or_fail"
  if [[ "$compare_rc" -eq 0 && -f "${job}_comparison_summary.csv" ]]; then
    classification="$(awk -F, 'NR == 2 {print $2; exit}' "${job}_comparison_summary.csv")"
  fi
  tail -n +1 "${job}_comparison_summary.csv" > "STAGE16N_R4P_${R4P_CASE_ID}_TARGET${R4P_TARGET}_COMPARISON_SUMMARY.txt" || true
  TARGET_JOB="$job" write_case_table "$classification"
  write_diagnostic_summary "$job"
  write_status "target${R4P_TARGET}_${classification}" "${label}_comparison" "comparison completed with status ${classification}"
  copy_lightweight_evidence
  cleanup_heavy_for_job "$job"
  copy_lightweight_evidence
}

prepare_target_state() {
  local jump_cycles=$((R4P_TARGET - CHECKPOINT_CYCLE))
  rm -f state.bin state.csv "STAGE16N_R4P_${R4P_CASE_ID}_TARGET${R4P_TARGET}_EXTRAPOLATED_STATE.md"
  python3 stage16n_make_extrapolated_state.py \
    --previous-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \
    --base-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" \
    --previous-cycle "$PREVIOUS_CYCLE" \
    --base-cycle "$CHECKPOINT_CYCLE" \
    --jump-cycles "$jump_cycles" \
    --output-cycle "$R4P_TARGET" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary "STAGE16N_R4P_${R4P_CASE_ID}_TARGET${R4P_TARGET}_EXTRAPOLATED_STATE.md"
}

run_target_case() {
  prepare_target_state
  export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
  export STAGE16N_JUMP_TARGET_STEP="$TRIGGER_STEP"
  export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

  if ! run_logged_phase "target-${R4P_TARGET} continuation datacheck" "$LOG_DIR/${TARGET_JOB}_datacheck.log" \
    abaqus job="${TARGET_JOB}_datacheck" input="$TARGET_INPUT" oldjob="$SOURCE_JOB" \
      user=stage16n_r3_jump_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$TARGET_JOB"
    write_status "target${R4P_TARGET}_datacheck_failure" "target${R4P_TARGET}_datacheck" "stop escalation"
    write_case_table "datacheck_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  if ! run_logged_phase "target-${R4P_TARGET} continuation solve" "$LOG_DIR/${TARGET_JOB}.log" \
    abaqus job="$TARGET_JOB" input="$TARGET_INPUT" oldjob="$SOURCE_JOB" \
      user=stage16n_r3_jump_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$TARGET_JOB"
    write_status "target${R4P_TARGET}_solve_failure" "target${R4P_TARGET}_solve" "stop escalation"
    write_case_table "solve_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  write_tails "$TARGET_JOB"
  grep "STAGE16N_R3J_OVERWRITE" "${TARGET_JOB}.dat" > "$LOG_DIR/${TARGET_JOB}_overwrite_trace.txt" || true
  grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${TARGET_JOB}.msg" | tee "$LOG_DIR/${TARGET_JOB}_parallelism_check.log" || true

  run_compare_and_classify "$TARGET_JOB" "target-${R4P_TARGET}"
}

run_exact_native_control_case() {
  if [[ "$R4P_TARGET" != "272" ]]; then
    write_status "exact_native_invalid_target" "exact_native_preflight" "exact-native control is defined only for target272"
    write_case_table "exact_native_invalid_target"
    copy_lightweight_evidence
    return 0
  fi

  if ! run_logged_phase "target-272 exact-native source datacheck" "$LOG_DIR/${EXACT_SOURCE_JOB}_datacheck.log" \
    abaqus job="${EXACT_SOURCE_JOB}_datacheck" input="${EXACT_SOURCE_JOB}.inp" oldjob="$SOURCE_JOB" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$EXACT_SOURCE_JOB"
    write_status "exact_native_source_datacheck_failure" "exact_native_source_datacheck" "native replay source failed before target continuation"
    write_case_table "exact_native_source_datacheck_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$EXACT_SOURCE_JOB"
    copy_lightweight_evidence
    return 0
  fi

  if ! run_logged_phase "target-272 exact-native source solve" "$LOG_DIR/${EXACT_SOURCE_JOB}.log" \
    abaqus job="$EXACT_SOURCE_JOB" input="${EXACT_SOURCE_JOB}.inp" oldjob="$SOURCE_JOB" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$EXACT_SOURCE_JOB"
    write_status "exact_native_source_solve_failure" "exact_native_source_solve" "native replay source incomplete"
    write_case_table "exact_native_source_solve_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$EXACT_SOURCE_JOB"
    copy_lightweight_evidence
    return 0
  fi

  write_tails "$EXACT_SOURCE_JOB"
  for ext in odb stt res mdl prt sim sta; do
    test -s "${EXACT_SOURCE_JOB}.${ext}"
  done
  local exact_inc
  exact_inc="$(awk -v step="$R4P_TARGET" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${EXACT_SOURCE_JOB}.sta")"
  cp "$EXACT_TARGET_TEMPLATE" "${EXACT_TARGET_JOB}_resolved.inp"
  sed -i "s/INC=__R4P_RESTART_INC__/INC=${exact_inc}/" "${EXACT_TARGET_JOB}_resolved.inp"

  if ! run_logged_phase "target-272 exact-native continuation datacheck" "$LOG_DIR/${EXACT_TARGET_JOB}_datacheck.log" \
    abaqus job="${EXACT_TARGET_JOB}_datacheck" input="${EXACT_TARGET_JOB}_resolved.inp" oldjob="$EXACT_SOURCE_JOB" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$EXACT_TARGET_JOB"
    write_status "exact_native_target_datacheck_failure" "exact_native_target_datacheck" "STEP=$R4P_TARGET INC=$exact_inc"
    write_case_table "exact_native_target_datacheck_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$EXACT_TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  if ! run_logged_phase "target-272 exact-native continuation solve" "$LOG_DIR/${EXACT_TARGET_JOB}.log" \
    abaqus job="$EXACT_TARGET_JOB" input="${EXACT_TARGET_JOB}_resolved.inp" oldjob="$EXACT_SOURCE_JOB" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$EXACT_TARGET_JOB"
    write_status "exact_native_target_solve_failure" "exact_native_target_solve" "STEP=$R4P_TARGET INC=$exact_inc"
    write_case_table "exact_native_target_solve_failure"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$EXACT_TARGET_JOB"
    copy_lightweight_evidence
    return 0
  fi

  write_tails "$EXACT_TARGET_JOB"
  grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${EXACT_TARGET_JOB}.msg" | tee "$LOG_DIR/${EXACT_TARGET_JOB}_parallelism_check.log" || true
  echo "restart_step,restart_inc,oldjob" > "STAGE16N_R4P_${R4P_CASE_ID}_EXACT_NATIVE_RESTART_READ.csv"
  echo "$R4P_TARGET,$exact_inc,$EXACT_SOURCE_JOB" >> "STAGE16N_R4P_${R4P_CASE_ID}_EXACT_NATIVE_RESTART_READ.csv"
  run_compare_and_classify "$EXACT_TARGET_JOB" "target-272-exact-native"
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

echo "[Stage16N-R4P] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4P] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4P] case=$R4P_CASE_ID target=$R4P_TARGET solved_start=$R4P_SOLVED_START mode=$R4P_MODE prev=${R4P_PREV_CASE:-none}"
echo "[Stage16N-R4P] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R4P] scratch=${SCRATCH_CASE_DIR:-$PWD}"

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
if [[ "$R4P_MODE" == "exact_native_control" ]]; then
  test -s "${EXACT_SOURCE_JOB}.inp"
  test -s "$EXACT_TARGET_TEMPLATE"
fi

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
echo "[Stage16N-R4P] source restart row: STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"

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

if [[ "$R4P_MODE" == "exact_native_control" ]]; then
  run_exact_native_control_case
else
  run_target_case
fi
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/R4P_storage_end_df.txt" || true
du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/R4P_storage_end_scratch9_user.txt" || true
cleanup_all_heavy
copy_lightweight_evidence
echo "[Stage16N-R4P] end: $(date '+%Y-%m-%d %H:%M:%S')"
