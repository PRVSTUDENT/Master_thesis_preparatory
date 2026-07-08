#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="R4N_250branch_refinement_storage_light_controller"
SOURCE_JOB="stage16n_r1b_restart_ref_250cycles"
CHECKPOINT_CYCLE="250"
PREVIOUS_CYCLE="100"
FINAL_CYCLE="500"
TRIGGER_STEP="251"
START_EPOCH="$(date +%s)"
OPTIONAL_TARGET_MAX_ELAPSED_SECONDS="${OPTIONAL_TARGET_MAX_ELAPSED_SECONDS:-72000}"

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
  cleanup_heavy_for_job "stage16n_r4n_target275_jump_250_to_275_solve_276_to_500"
  cleanup_heavy_for_job "stage16n_r4n_target280_jump_250_to_280_solve_281_to_500"
  cleanup_heavy_for_job "stage16n_r4n_target285_jump_250_to_285_solve_286_to_500"
  rm -f state.bin state.csv
}

write_status() {
  local classification="$1"
  local phase="$2"
  local detail="$3"
  {
    echo "# Stage 16N-R4N Controller Status"
    echo
    echo "- PBS job: ${PBS_JOBID:-manual}"
    echo "- Controller: $CONTROLLER"
    echo "- Source job: $SOURCE_JOB"
    echo "- Source package basename: $SOURCE_JOB"
    echo "- Source package required files: .odb .stt .res .mdl .prt .sim .sta"
    echo "- Mandatory targets: 275, 280"
    echo "- Optional target: 285 if target280 passes and walltime remains"
    echo "- Continuation restart writing: disabled"
    echo "- R4J9/R4J10: blocked"
    echo "- 505 branch: parked"
    echo "- Classification: $classification"
    echo "- Phase: $phase"
    echo "- Detail: $detail"
    echo "- Heavy copy-back: disabled"
    echo "- Heavy cleanup after classification: enabled"
    echo "- Scratch case dir: ${SCRATCH_CASE_DIR:-$PWD}"
    echo "- Finished: $(date '+%Y-%m-%d %H:%M:%S')"
  } > STAGE16N_R4N_CONTROLLER_STATUS.md
}

write_package_manifest() {
  {
    echo "# Stage 16N-R4N Source Package Manifest"
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
    echo "This package is scratch-only for R4N and is deleted after final classification unless a future manifest explicitly records a retention reason."
  } > STAGE16N_R4N_SOURCE_PACKAGE_MANIFEST.md
}

append_case_table() {
  local target="$1"
  local skipped="$2"
  local range="$3"
  local status="$4"
  local summary_file="$5"
  local global=""
  local localerr=""
  local s11=""
  if [[ -f "$summary_file" ]]; then
    IFS=, read -r _ status global localerr s11 _ < <(awk 'NR==2 {print}' "$summary_file")
  fi
  if [[ ! -f STAGE16N_R4N_CASE_TABLE.csv ]]; then
    echo "target_cycle,skipped_cycles,continuation_range,status,max_global_error_pct,max_primary_local_error_pct,diagnostic_s11_error_pct" > STAGE16N_R4N_CASE_TABLE.csv
  fi
  echo "$target,$skipped,$range,$status,$global,$localerr,$s11" >> STAGE16N_R4N_CASE_TABLE.csv
}

prepare_target_state() {
  local target="$1"
  local jump_cycles=$((target - CHECKPOINT_CYCLE))
  rm -f state.bin state.csv STAGE16N_R4N_TARGET${target}_EXTRAPOLATED_STATE.md
  python3 stage16n_make_extrapolated_state.py \
    --previous-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \
    --base-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" \
    --previous-cycle "$PREVIOUS_CYCLE" \
    --base-cycle "$CHECKPOINT_CYCLE" \
    --jump-cycles "$jump_cycles" \
    --output-cycle "$target" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary "STAGE16N_R4N_TARGET${target}_EXTRAPOLATED_STATE.md"
}

run_target_case() {
  local target="$1"
  local solved_start="$2"
  local optional="$3"
  local job="stage16n_r4n_target${target}_jump_250_to_${target}_solve_${solved_start}_to_500"
  local inp="${job}.inp"
  local label="target-${target}"
  local skipped=$((target - CHECKPOINT_CYCLE))
  local range="${solved_start}-500"

  prepare_target_state "$target"
  export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
  export STAGE16N_JUMP_TARGET_STEP="$TRIGGER_STEP"
  export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

  if ! run_logged_phase "${label} continuation datacheck" "$LOG_DIR/${job}_datacheck.log" \
    abaqus job="${job}_datacheck" input="$inp" oldjob="$SOURCE_JOB" \
      user=stage16n_r3_jump_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$job"
    write_status "target${target}_datacheck_failure" "target${target}_datacheck" "stop escalation"
    append_case_table "$target" "$skipped" "$range" "datacheck_failure" "${job}_comparison_summary.csv"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$job"
    copy_lightweight_evidence
    return 20
  fi

  if ! run_logged_phase "${label} continuation solve" "$LOG_DIR/${job}.log" \
    abaqus job="$job" input="$inp" oldjob="$SOURCE_JOB" \
      user=stage16n_r3_jump_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE"; then
    write_tails "$job"
    write_status "target${target}_solve_failure" "target${target}_solve" "stop escalation"
    append_case_table "$target" "$skipped" "$range" "solve_failure" "${job}_comparison_summary.csv"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$job"
    copy_lightweight_evidence
    return 21
  fi

  write_tails "$job"
  grep "STAGE16N_R3J_OVERWRITE" "${job}.dat" > "$LOG_DIR/${job}_overwrite_trace.txt" || true
  grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${job}.msg" | tee "$LOG_DIR/${job}_parallelism_check.log" || true

  if ! run_logged_phase "${label} ODB extraction" "$LOG_DIR/${job}_extract.log" \
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$job"; then
    write_status "target${target}_extraction_failure" "target${target}_extraction" "stop escalation"
    append_case_table "$target" "$skipped" "$range" "extraction_failure" "${job}_comparison_summary.csv"
    copy_lightweight_evidence
    cleanup_heavy_for_job "$job"
    copy_lightweight_evidence
    return 22
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
  if [[ "$compare_rc" -eq 0 && -f "${job}_comparison_summary.csv" ]] && awk -F, 'NR == 2 && $2 == "pass" {ok=1} END {exit ok ? 0 : 1}' "${job}_comparison_summary.csv"; then
    classification="pass"
  elif [[ "$compare_rc" -eq 0 && -f "${job}_comparison_summary.csv" ]]; then
    classification="$(awk -F, 'NR == 2 {print $2; exit}' "${job}_comparison_summary.csv")"
  fi

  tail -n +1 "${job}_comparison_summary.csv" > "STAGE16N_R4N_TARGET${target}_COMPARISON_SUMMARY.txt" || true
  append_case_table "$target" "$skipped" "$range" "$classification" "${job}_comparison_summary.csv"
  write_status "target${target}_${classification}" "target${target}_comparison" "comparison completed with status ${classification}"
  copy_lightweight_evidence
  cleanup_heavy_for_job "$job"
  copy_lightweight_evidence

  if [[ "$classification" == "pass" ]]; then
    return 0
  fi
  if [[ "$optional" == "1" ]]; then
    return 30
  fi
  return 23
}

on_error() {
  local rc=$?
  write_tails "$SOURCE_JOB"
  write_tails "stage16n_r4n_target275_jump_250_to_275_solve_276_to_500"
  write_tails "stage16n_r4n_target280_jump_250_to_280_solve_281_to_500"
  write_tails "stage16n_r4n_target285_jump_250_to_285_solve_286_to_500"
  write_status "controller_failure" "trap" "exit code $rc"
  copy_lightweight_evidence
  cleanup_all_heavy
  copy_lightweight_evidence
  exit "$rc"
}
trap on_error ERR
trap copy_lightweight_evidence EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4N] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4N] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4N] controller: $CONTROLLER"
echo "[Stage16N-R4N] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R4N] scratch=${SCRATCH_CASE_DIR:-$PWD}"
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4n_storage_start_df.txt" || true
du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4n_storage_start_scratch9_user.txt" || true

for required in \
  "${SOURCE_JOB}.inp" \
  "stage16n_r4n_target275_jump_250_to_275_solve_276_to_500.inp" \
  "stage16n_r4n_target280_jump_250_to_280_solve_281_to_500.inp" \
  "stage16n_r4n_target285_jump_250_to_285_solve_286_to_500.inp" \
  "stage16n_neml_equivalent_chaboche_umat.for" \
  "stage16n_r3_jump_umat.for" \
  "stage16n_extract_hysteresis_and_local_states.py" \
  "stage16n_extract_exact_state_for_reinjection.py" \
  "stage16n_make_extrapolated_state.py" \
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
  copy_lightweight_evidence
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
fi

R1B_RESTART_INC="$(awk -v step="$CHECKPOINT_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${SOURCE_JOB}.sta")"
echo "[Stage16N-R4N] source restart row: STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"

if ! run_logged_phase "source state extraction" "$LOG_DIR/${SOURCE_JOB}_extract_state_100_250.log" \
  abaqus python stage16n_extract_exact_state_for_reinjection.py \
    --odb "${SOURCE_JOB}.odb" \
    --cycles "${PREVIOUS_CYCLE},${CHECKPOINT_CYCLE}" \
    --outdir _source_state; then
  write_status "source_state_extraction_failure" "source_state_extraction" "cannot prepare target states"
  copy_lightweight_evidence
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
fi

if ! run_target_case 275 276 0; then
  echo "[Stage16N-R4N] target275 did not pass; stopping escalation."
  df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4n_storage_end_df.txt" || true
  du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4n_storage_end_scratch9_user.txt" || true
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
fi

if ! run_target_case 280 281 0; then
  echo "[Stage16N-R4N] target280 did not pass; stopping escalation."
  df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4n_storage_end_df.txt" || true
  du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4n_storage_end_scratch9_user.txt" || true
  cleanup_all_heavy
  copy_lightweight_evidence
  exit 0
fi

elapsed=$(( $(date +%s) - START_EPOCH ))
if [[ "$elapsed" -lt "$OPTIONAL_TARGET_MAX_ELAPSED_SECONDS" ]]; then
  echo "[Stage16N-R4N] target280 passed and elapsed=${elapsed}s; running optional target285."
  run_target_case 285 286 1 || true
else
  echo "[Stage16N-R4N] target280 passed but elapsed=${elapsed}s; skipping optional target285."
  write_status "target280_pass_optional285_skipped" "optional_gate" "elapsed ${elapsed}s exceeded threshold ${OPTIONAL_TARGET_MAX_ELAPSED_SECONDS}s"
fi

df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/r4n_storage_end_df.txt" || true
du -sh /scratch9/pr21vyci 2>/dev/null | tee "$LOG_DIR/r4n_storage_end_scratch9_user.txt" || true
cleanup_all_heavy
copy_lightweight_evidence
echo "[Stage16N-R4N] end: $(date '+%Y-%m-%d %H:%M:%S')"
