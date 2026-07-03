#!/usr/bin/env bash
set -euo pipefail

: "${CONTROLLER:?CONTROLLER is required}"
: "${BLOCK_INDEX:?BLOCK_INDEX is required}"
: "${SOURCE_CYCLE:?SOURCE_CYCLE is required}"
: "${PREVIOUS_CYCLE:?PREVIOUS_CYCLE is required}"
: "${JUMP_TARGET:?JUMP_TARGET is required}"
: "${SOLVED_START:?SOLVED_START is required}"
: "${BLOCK_END:?BLOCK_END is required}"
: "${PREVIOUS_SCRATCH_DIR:?PREVIOUS_SCRATCH_DIR is required}"
: "${OLDJOB:?OLDJOB is required}"
: "${JOB:?JOB is required}"

START_EPOCH="$(date +%s)"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
MAIL_TO="${MAIL_TO:-${USER}@mailserver.tu-freiberg.de}"
MAIL_SUBJECT_PREFIX="${MAIL_SUBJECT_PREFIX:-Stage16N-${CONTROLLER}}"
ALLOW_PREVIOUS_FEASIBILITY="${ALLOW_PREVIOUS_FEASIBILITY:-0}"
R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL="${R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL:-0}"
CLASSIFICATION_SCOPE_OVERRIDE="${CLASSIFICATION_SCOPE_OVERRIDE:-}"
RESTART_STEP=""
RESTART_INC=""
JOB_FINAL_STATUS="starting"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH" "_source_state"

exec > >(tee -a "${CONTROLLER}_CONTROLLER.log") 2>&1

elapsed_seconds() {
  echo $(( $(date +%s) - START_EPOCH ))
}

send_job_mail() {
  local event="$1"
  local status="${2:-unknown}"
  local subject="${MAIL_SUBJECT_PREFIX}: ${event} ${PBS_JOBID:-manual} (${status})"
  local body
  body="Controller: $CONTROLLER
Event: $event
Status: $status
PBS job: ${PBS_JOBID:-manual}
Host: $(hostname 2>/dev/null || echo unknown)
Workdir: $PWD
Previous scratch: $PREVIOUS_SCRATCH_DIR
Time: $(date '+%Y-%m-%d %H:%M:%S %Z')
Elapsed seconds: $(elapsed_seconds)
"
  if [[ -z "$MAIL_TO" ]]; then
    echo "[mail] MAIL_TO is empty; not sending ${event} notification"
    return 0
  fi
  if command -v mailx >/dev/null 2>&1; then
    printf '%s\n' "$body" | mailx -s "$subject" "$MAIL_TO" || echo "[mail] mailx failed for ${event}"
  elif command -v mail >/dev/null 2>&1; then
    printf '%s\n' "$body" | mail -s "$subject" "$MAIL_TO" || echo "[mail] mail failed for ${event}"
  elif command -v sendmail >/dev/null 2>&1; then
    {
      echo "To: $MAIL_TO"
      echo "Subject: $subject"
      echo
      printf '%s\n' "$body"
    } | sendmail -t || echo "[mail] sendmail failed for ${event}"
  else
    echo "[mail] no mail/mailx/sendmail command available; ${event} notification not sent"
  fi
}

write_status() {
  local status="$1"
  local phase="$2"
  local detail="$3"
  JOB_FINAL_STATUS="$status"
  {
    echo "status=$status"
    echo "phase=$phase"
    echo "detail=$detail"
    echo "controller=$CONTROLLER"
    echo "pbs_job_id=${PBS_JOBID:-manual}"
    echo "previous_scratch_dir=$PREVIOUS_SCRATCH_DIR"
    echo "oldjob=$OLDJOB"
    echo "job=$JOB"
    echo "source_cycle=$SOURCE_CYCLE"
    echo "jump_target=$JUMP_TARGET"
    echo "solved_start=$SOLVED_START"
    echo "block_end=$BLOCK_END"
    echo "restart_step=$RESTART_STEP"
    echo "restart_inc=$RESTART_INC"
    echo "allow_previous_feasibility=$ALLOW_PREVIOUS_FEASIBILITY"
    echo "R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=$R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL"
    echo "classification_scope=${CLASSIFICATION_SCOPE_OVERRIDE:-auto}"
    echo "abaqus_cpus=${ABAQUS_CPUS:-1}"
    echo "scratch_case_dir=${SCRATCH_CASE_DIR:-$PWD}"
    echo "elapsed_seconds=$(elapsed_seconds)"
    echo "updated_at=$(date '+%Y-%m-%d %H:%M:%S')"
  } > "${CONTROLLER}_STATUS.txt"
}

init_summary() {
  echo "block_index,source_cycle,jump_target,solved_start,block_end,status,classification_scope,reference_available,comparison_status,job,oldjob,elapsed_seconds,detail" > "${CONTROLLER}_BLOCK_SUMMARY.csv"
}

append_summary() {
  local status="$1"
  local scope="$2"
  local ref_available="$3"
  local comparison_status="$4"
  local detail="$5"
  echo "$BLOCK_INDEX,$SOURCE_CYCLE,$JUMP_TARGET,$SOLVED_START,$BLOCK_END,$status,$scope,$ref_available,$comparison_status,$JOB,$OLDJOB,$(elapsed_seconds),\"$detail\"" >> "${CONTROLLER}_BLOCK_SUMMARY.csv"
}

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${HOME_CASE_DIR:-}" ]]; then
    if [[ -n "${SCRATCH_BASE:-}" && -s "$SCRATCH_BASE/${CONTROLLER}.pbs.out" ]]; then
      cp "$SCRATCH_BASE/${CONTROLLER}.pbs.out" "$PWD/${CONTROLLER}.pbs.out" || true
    fi
    rsync -av \
      --include='*/' \
      --exclude='state.bin' \
      --exclude='state.csv' \
      --include="${CONTROLLER}*.txt" \
      --include="${CONTROLLER}*.csv" \
      --include="${CONTROLLER}*.log" \
      --include="qstat_${CONTROLLER,,}*.txt" \
      --include="${CONTROLLER}_SOURCE*.md" \
      --include="${JOB}.inp" \
      --include="${JOB}_comparison_*.csv" \
      --include="${JOB}_*_tail.txt" \
      --include="${JOB}_cycle_metrics.csv" \
      --include="${JOB}_selected_cycle_local_states.csv" \
      --include="${JOB}_selected_cycle_loops.csv" \
      --include="_source_state/stage16n_exact_state_cycle$(printf '%04d' "$BLOCK_END")_summary.md" \
      --include='_logs/*.log' \
      --include='_logs/*.txt' \
      --include='*.pbs.out' \
      --exclude='*.odb' --exclude='*.stt' --exclude='*.res' --exclude='*.sim' \
      --exclude='*.mdl' --exclude='*.prt' --exclude='*.dat' --exclude='*.msg' \
      --exclude='*.sta' --exclude='*.023' --exclude='*.cax' --exclude='*.abq' \
      --exclude='*.pac' --exclude='*.sel' --exclude='*.lck' \
      --exclude='*' \
      "$PWD/" "$HOME_CASE_DIR/"
  fi
}

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

write_tails() {
  local job="$1"
  local suffix base
  for suffix in "" "_datacheck"; do
    base="${job}${suffix}"
    [[ -f "${base}.dat" ]] && tail -n 220 "${base}.dat" > "${base}_dat_tail.txt" || true
    [[ -f "${base}.msg" ]] && tail -n 220 "${base}.msg" > "${base}_msg_tail.txt" || true
    [[ -f "${base}.sta" ]] && tail -n 160 "${base}.sta" > "${base}_sta_tail.txt" || true
  done
}

resolve_restart_from_sta() {
  local sta="$1"
  awk '
    /^[[:space:]]*[0-9]+[[:space:]]+[0-9]+/ {
      step=$1
      inc=$2
    }
    END {
      if (step != "" && inc != "") {
        print step " " inc
      } else {
        exit 3
      }
    }
  ' "$sta"
}

latest_previous_summary_line() {
  local summary
  summary="$(find "$PREVIOUS_SCRATCH_DIR" -maxdepth 1 -type f -name '*_BLOCK_SUMMARY.csv' | sort | tail -n 1 || true)"
  if [[ -z "$summary" || ! -s "$summary" ]]; then
    echo ""
    return 0
  fi
  tail -n 1 "$summary"
}

latest_previous_status() {
  local status_file
  status_file="$(find "$PREVIOUS_SCRATCH_DIR" -maxdepth 1 -type f -name '*_STATUS.txt' | sort | tail -n 1 || true)"
  if [[ -z "$status_file" || ! -s "$status_file" ]]; then
    echo ""
    return 0
  fi
  awk -F= '$1 == "status" {print $2; exit}' "$status_file"
}

cycle1000_accuracy_fail_override_allowed() {
  [[ "$R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL" == "1" ]] || return 1
  [[ "$SOURCE_CYCLE" == "1000" ]] || return 1
  [[ -s "R4Q3_REFERENCE_REPAIR_STATUS.txt" ]] || return 1
  grep -q '^status=accuracy_validation_fail$' R4Q3_REFERENCE_REPAIR_STATUS.txt || return 1
  grep -q '^max_primary_local_error_pct=6\.2795526$' R4Q3_REFERENCE_REPAIR_STATUS.txt || return 1
}

gate_previous_controller() {
  local prev_status line prev_block_status prev_scope prev_ref prev_compare prev_detail
  prev_status="$(latest_previous_status)"
  line="$(latest_previous_summary_line)"
  if [[ -z "$prev_status" || -z "$line" ]]; then
    append_summary "previous_status_missing" "self_gate" "unknown" "not_run" "previous status or summary missing"
    write_status "previous_status_missing" "self_gate" "previous status or summary missing"
    copy_lightweight_evidence
    exit 0
  fi

  IFS=, read -r _ _ _ _ _ prev_block_status prev_scope prev_ref prev_compare _ _ _ prev_detail <<< "$line"
  echo "[gate] previous status=$prev_status summary_status=$prev_block_status scope=$prev_scope ref=$prev_ref comparison=$prev_compare detail=$prev_detail"

  if [[ "$prev_status" != "completed" || "$prev_block_status" != "completed" ]]; then
    append_summary "previous_not_completed" "self_gate" "$prev_ref" "$prev_compare" "previous status=$prev_status block_status=$prev_block_status"
    write_status "previous_not_completed" "self_gate" "previous status=$prev_status block_status=$prev_block_status"
    copy_lightweight_evidence
    exit 0
  fi
  if [[ "$prev_detail" == *"state=failed"* || "$prev_detail" == *"state_extract_failed"* ]]; then
    append_summary "previous_state_extract_failed" "self_gate" "$prev_ref" "$prev_compare" "$prev_detail"
    write_status "previous_state_extract_failed" "self_gate" "$prev_detail"
    copy_lightweight_evidence
    exit 0
  fi
  if [[ "$prev_compare" == "fail" || "$prev_compare" == "review" || "$prev_compare" == "comparison_error" ]]; then
    if cycle1000_accuracy_fail_override_allowed; then
      echo "[gate] explicit feasibility override accepted after cycle1000 accuracy_validation_fail"
      return 0
    fi
    append_summary "previous_comparison_blocked" "self_gate" "$prev_ref" "$prev_compare" "previous comparison blocked continuation"
    write_status "previous_comparison_blocked" "self_gate" "previous comparison=$prev_compare"
    copy_lightweight_evidence
    exit 0
  fi
  if [[ "$prev_compare" == "not_available" && "$ALLOW_PREVIOUS_FEASIBILITY" != "1" ]]; then
    append_summary "previous_feasibility_not_allowed" "self_gate" "$prev_ref" "$prev_compare" "ALLOW_PREVIOUS_FEASIBILITY is not set"
    write_status "previous_feasibility_not_allowed" "self_gate" "previous comparison not available and feasibility not allowed"
    copy_lightweight_evidence
    exit 0
  fi
}

verify_previous_source() {
  local ext
  gate_previous_controller
  for ext in sta res stt mdl prt sim odb; do
    if [[ ! -s "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}" ]]; then
      append_summary "previous_source_missing" "self_gate" "unknown" "not_run" "missing ${OLDJOB}.${ext}"
      write_status "previous_source_missing" "self_gate" "missing $PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}"
      copy_lightweight_evidence
      exit 0
    fi
  done
  read -r RESTART_STEP RESTART_INC < <(resolve_restart_from_sta "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.sta")
  if [[ -z "$RESTART_STEP" || -z "$RESTART_INC" ]]; then
    append_summary "restart_record_missing" "self_gate" "unknown" "not_run" "could not parse restart step/inc"
    write_status "restart_record_missing" "self_gate" "could not resolve step/inc from $PREVIOUS_SCRATCH_DIR/${OLDJOB}.sta"
    copy_lightweight_evidence
    exit 0
  fi
  for ext in sta res stt mdl prt sim odb; do
    ln -sfn "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}" "${OLDJOB}.${ext}"
  done
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" _source_state/
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle$(printf '%04d' "$SOURCE_CYCLE").csv" _source_state/
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle$(printf '%04d' "$SOURCE_CYCLE")_summary.md" _source_state/ || true
}

prepare_jump_state() {
  rm -f state.bin state.csv
  python3 stage16n_make_extrapolated_state.py \
    --previous-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \
    --base-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$SOURCE_CYCLE").csv" \
    --previous-cycle "$PREVIOUS_CYCLE" \
    --base-cycle "$SOURCE_CYCLE" \
    --jump-cycles "$((JUMP_TARGET - SOURCE_CYCLE))" \
    --output-cycle "$JUMP_TARGET" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary "${CONTROLLER}_SOURCE${SOURCE_CYCLE}_TARGET${JUMP_TARGET}_EXTRAPOLATED_STATE.md"
}

make_deck() {
  python3 stage16n_make_r4q_restart_deck.py \
    --output "${JOB}.inp" \
    --old-step "$RESTART_STEP" \
    --old-inc "$RESTART_INC" \
    --solved-start "$SOLVED_START" \
    --block-end "$BLOCK_END" \
    --title "Stage 16N-${CONTROLLER}: ${SOURCE_CYCLE} to ${JUMP_TARGET}, solve ${SOLVED_START} to ${BLOCK_END}"
  grep -q "^\*RESTART, READ, STEP=${RESTART_STEP}, INC=${RESTART_INC}$" "${JOB}.inp"
}

reference_available_for() {
  local cycle="$1"
  [[ -s "reference_${cycle}_cycle_metrics.csv" && -s "reference_${cycle}_selected_cycle_local_states.csv" ]]
}

run_comparison_if_available() {
  local job="$1"
  local block_end="$2"
  if ! reference_available_for "$block_end"; then
    echo "not_available"
    return 0
  fi
  set +e
  phase_time "compare block end ${block_end}" \
    python3 stage16n_compare_r3j_jump_against_reference.py \
      --jump-metrics "${job}_cycle_metrics.csv" \
      --jump-local-states "${job}_selected_cycle_local_states.csv" \
      --ref-metrics "reference_${block_end}_cycle_metrics.csv" \
      --ref-local-states "reference_${block_end}_selected_cycle_local_states.csv" \
      --cycles "$block_end" \
      --out-dir "." \
      --prefix "$job" \
    2>&1 | tee "$LOG_DIR/${job}_compare_${block_end}.log" >&2
  local rc=${PIPESTATUS[0]}
  set -e
  if [[ "$rc" -eq 0 && -s "${job}_comparison_summary.csv" ]]; then
    awk -F, 'NR == 2 {print $2; exit}' "${job}_comparison_summary.csv"
  else
    echo "comparison_error"
  fi
}

extract_state_cycle_end() {
  run_logged_phase "extract source state cycle ${BLOCK_END} from ${JOB}" "$LOG_DIR/${JOB}_extract_state_${BLOCK_END}.log" \
    abaqus python stage16n_extract_exact_state_for_reinjection.py \
      --odb "${JOB}.odb" \
      --cycles "$BLOCK_END" \
      --outdir _source_state
}

on_error() {
  local rc=$?
  write_status "controller_failure" "trap" "exit code $rc"
  copy_lightweight_evidence
  exit 0
}

on_exit() {
  local rc=$?
  copy_lightweight_evidence
  send_job_mail "END" "$JOB_FINAL_STATUS"
  exit "$rc"
}

trap on_error ERR
trap on_exit EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-${CONTROLLER}] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-${CONTROLLER}] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-${CONTROLLER}] scratch: ${SCRATCH_CASE_DIR:-$PWD}"
echo "[Stage16N-${CONTROLLER}] previous source: $PREVIOUS_SCRATCH_DIR/$OLDJOB"
send_job_mail "BEGIN" "started"
init_summary
write_status "starting" "self_gate" "checking previous block and source"
verify_previous_source
write_status "running" "prepare" "source=$SOURCE_CYCLE target=$JUMP_TARGET solve=$SOLVED_START-$BLOCK_END restart=$RESTART_STEP/$RESTART_INC"
prepare_jump_state
make_deck
copy_lightweight_evidence

export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
export STAGE16N_JUMP_TARGET_STEP="$((SOURCE_CYCLE + 1))"
export STAGE16N_JUMP_CHECK_TIME="$SOURCE_CYCLE"

if ! run_logged_phase "${CONTROLLER} datacheck" "$LOG_DIR/${JOB}_datacheck.log" \
  abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_r3_jump_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
  write_tails "$JOB"
  append_summary "datacheck_failure" "feasibility" "unknown" "not_run" "datacheck failed"
  write_status "datacheck_failure" "datacheck" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

if ! run_logged_phase "${CONTROLLER} solve" "$LOG_DIR/${JOB}.log" \
  abaqus job="$JOB" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_r3_jump_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
  write_tails "$JOB"
  append_summary "solve_failure" "feasibility" "unknown" "not_run" "solve failed"
  write_status "solve_failure" "solve" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

write_tails "$JOB"
if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
  append_summary "sta_not_successful" "feasibility" "unknown" "not_run" "sta lacks successful completion line"
  write_status "sta_not_successful" "sta_check" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

grep "STAGE16N_R3J_OVERWRITE" "${JOB}.dat" > "$LOG_DIR/${JOB}_overwrite_trace.txt" || true
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" > "$LOG_DIR/${JOB}_parallelism_check.log" || true

extraction_status="not_run"
if run_logged_phase "${CONTROLLER} ODB extraction" "$LOG_DIR/${JOB}_extract.log" \
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB"; then
  extraction_status="ok"
else
  extraction_status="failed"
fi

end_state="not_run"
if extract_state_cycle_end; then
  end_state="ok"
else
  end_state="failed"
fi

ref_available="no"
scope="${CLASSIFICATION_SCOPE_OVERRIDE:-feasibility}"
comparison_status="not_available"
if reference_available_for "$BLOCK_END"; then
  ref_available="yes"
  scope="${CLASSIFICATION_SCOPE_OVERRIDE:-accuracy_validation}"
  comparison_status="$(run_comparison_if_available "$JOB" "$BLOCK_END")"
fi

append_summary "completed" "$scope" "$ref_available" "$comparison_status" "extraction=${extraction_status}; cycle${BLOCK_END}_state=${end_state}"
write_status "completed" "controller_end" "block_end=$BLOCK_END scope=$scope comparison=$comparison_status cycle${BLOCK_END}_state=$end_state"
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/${CONTROLLER}_storage_df_after.txt" || true
du -sh /scratch9/"$USER" 2>/dev/null | tee "$LOG_DIR/${CONTROLLER}_storage_scratch9_user_after.txt" || true
copy_lightweight_evidence
echo "[Stage16N-${CONTROLLER}] end: $(date '+%Y-%m-%d %H:%M:%S')"
