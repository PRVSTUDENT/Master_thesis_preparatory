#!/usr/bin/env bash
set -euo pipefail

: "${CONTROLLER:?CONTROLLER is required}"
: "${PREVIOUS_SCRATCH_DIR:?PREVIOUS_SCRATCH_DIR is required}"
: "${OLDJOB:?OLDJOB is required}"
: "${JOB:?JOB is required}"
: "${SOURCE_CYCLE:?SOURCE_CYCLE is required}"
: "${SOLVED_START:?SOLVED_START is required}"
: "${BLOCK_END:?BLOCK_END is required}"

START_EPOCH="$(date +%s)"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
MAIL_TO="${MAIL_TO:-${USER}@mailserver.tu-freiberg.de}"
MAIL_SUBJECT_PREFIX="${MAIL_SUBJECT_PREFIX:-Stage16N-${CONTROLLER}}"
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
  else
    echo "[mail] no mail/mailx command available; ${event} notification not sent"
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
    echo "classification_scope=exact_native_diagnostic_control"
    echo "parent_chain_classification_scope=feasibility_only_after_cycle1000_accuracy_fail"
    echo "previous_scratch_dir=$PREVIOUS_SCRATCH_DIR"
    echo "oldjob=$OLDJOB"
    echo "job=$JOB"
    echo "source_cycle=$SOURCE_CYCLE"
    echo "solved_start=$SOLVED_START"
    echo "block_end=$BLOCK_END"
    echo "restart_step=$RESTART_STEP"
    echo "restart_inc=$RESTART_INC"
    echo "abaqus_cpus=${ABAQUS_CPUS:-1}"
    echo "scratch_case_dir=${SCRATCH_CASE_DIR:-$PWD}"
    echo "elapsed_seconds=$(elapsed_seconds)"
    echo "updated_at=$(date '+%Y-%m-%d %H:%M:%S')"
  } > "${CONTROLLER}_STATUS.txt"
}

init_summary() {
  echo "case,source_cycle,solved_start,block_end,status,classification_scope,reference_available,comparison_status,job,oldjob,elapsed_seconds,detail" > "${CONTROLLER}_SUMMARY.csv"
}

append_summary() {
  local status="$1"
  local ref_available="$2"
  local comparison_status="$3"
  local detail="$4"
  echo "$CONTROLLER,$SOURCE_CYCLE,$SOLVED_START,$BLOCK_END,$status,exact_native_diagnostic_control,$ref_available,$comparison_status,$JOB,$OLDJOB,$(elapsed_seconds),\"$detail\"" >> "${CONTROLLER}_SUMMARY.csv"
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

verify_previous_source() {
  local ext status_file status
  for ext in sta res stt mdl prt sim odb; do
    if [[ ! -s "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}" ]]; then
      append_summary "previous_source_missing" "unknown" "not_run" "missing ${OLDJOB}.${ext}"
      write_status "previous_source_missing" "self_gate" "missing $PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}"
      copy_lightweight_evidence
      exit 0
    fi
  done
  status_file="$(find "$PREVIOUS_SCRATCH_DIR" -maxdepth 1 -type f -name '*_STATUS.txt' | sort | while read -r candidate; do
    if grep -q "^job=$OLDJOB$" "$candidate" 2>/dev/null || grep -q "^controller=R4Q2_continue_from_cycle500_1cpu$" "$candidate" 2>/dev/null; then
      printf '%s\n' "$candidate"
      break
    fi
  done)"
  if [[ -z "$status_file" && -s "$PREVIOUS_SCRATCH_DIR/R4Q2_CONTINUE_BLOCK_SUMMARY.csv" ]]; then
    if awk -F, -v oldjob="$OLDJOB" 'NR > 1 && $10 == oldjob && $6 == "completed" {found=1} END {exit(found ? 0 : 1)}' "$PREVIOUS_SCRATCH_DIR/R4Q2_CONTINUE_BLOCK_SUMMARY.csv"; then
      status_file="$PREVIOUS_SCRATCH_DIR/R4Q2_CONTINUE_STATUS.txt"
    fi
  fi
  if [[ -z "$status_file" ]]; then
    append_summary "previous_status_missing" "unknown" "not_run" "R4Q2 status file missing"
    write_status "previous_status_missing" "self_gate" "R4Q2 status file missing"
    copy_lightweight_evidence
    exit 0
  fi
  status="$(awk -F= '$1 == "status" {print $2; exit}' "$status_file")"
  if [[ "$status" != "completed" ]]; then
    append_summary "previous_not_completed" "unknown" "not_run" "previous status=$status"
    write_status "previous_not_completed" "self_gate" "previous status=$status"
    copy_lightweight_evidence
    exit 0
  fi
  read -r RESTART_STEP RESTART_INC < <(resolve_restart_from_sta "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.sta")
  for ext in sta res stt mdl prt sim odb; do
    ln -sfn "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}" "${OLDJOB}.${ext}"
  done
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle$(printf '%04d' "$SOURCE_CYCLE")_summary.md" _source_state/ || true
}

make_native_deck() {
  python3 stage16n_make_r4q_restart_deck.py \
    --output "${JOB}.inp" \
    --old-step "$RESTART_STEP" \
    --old-inc "$RESTART_INC" \
    --solved-start "$SOLVED_START" \
    --block-end "$BLOCK_END" \
    --title "Stage 16N-${CONTROLLER}: exact/native continuation ${SOURCE_CYCLE} to ${BLOCK_END}"
  grep -q "^\*RESTART, READ, STEP=${RESTART_STEP}, INC=${RESTART_INC}$" "${JOB}.inp"
}

reference_available() {
  [[ -s "R4Q3_REFERENCE_REPAIR_reference_1000_cycle_metrics.csv" && -s "R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv" ]]
}

run_comparison() {
  set +e
  phase_time "compare exact/native control at cycle ${BLOCK_END}" \
    python3 stage16n_compare_r3j_jump_against_reference.py \
      --jump-metrics "${JOB}_cycle_metrics.csv" \
      --jump-local-states "${JOB}_selected_cycle_local_states.csv" \
      --ref-metrics "R4Q3_REFERENCE_REPAIR_reference_1000_cycle_metrics.csv" \
      --ref-local-states "R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv" \
      --cycles "$BLOCK_END" \
      --out-dir "." \
      --prefix "$JOB" \
    2>&1 | tee "$LOG_DIR/${JOB}_compare_${BLOCK_END}.log" >&2
  local rc=${PIPESTATUS[0]}
  set -e
  if [[ "$rc" -eq 0 && -s "${JOB}_comparison_summary.csv" ]]; then
    awk -F, 'NR == 2 {print $2; exit}' "${JOB}_comparison_summary.csv"
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

unset STAGE16N_JUMP_STATE_BIN
unset STAGE16N_JUMP_TARGET_STEP
unset STAGE16N_JUMP_CHECK_TIME

echo "[Stage16N-${CONTROLLER}] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-${CONTROLLER}] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-${CONTROLLER}] scratch: ${SCRATCH_CASE_DIR:-$PWD}"
echo "[Stage16N-${CONTROLLER}] previous source: $PREVIOUS_SCRATCH_DIR/$OLDJOB"
send_job_mail "BEGIN" "started"
init_summary
write_status "starting" "self_gate" "checking R4Q2 cycle750 exact source"
verify_previous_source
write_status "running" "prepare" "native continuation source=$SOURCE_CYCLE solve=$SOLVED_START-$BLOCK_END restart=$RESTART_STEP/$RESTART_INC"
make_native_deck
copy_lightweight_evidence

if ! run_logged_phase "${CONTROLLER} datacheck" "$LOG_DIR/${JOB}_datacheck.log" \
  abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_r3_jump_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
  write_tails "$JOB"
  append_summary "datacheck_failure" "unknown" "not_run" "datacheck failed"
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
  append_summary "solve_failure" "unknown" "not_run" "solve failed"
  write_status "solve_failure" "solve" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

write_tails "$JOB"
if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
  append_summary "sta_not_successful" "unknown" "not_run" "sta lacks successful completion line"
  write_status "sta_not_successful" "sta_check" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

if grep -q "STAGE16N_R3J_OVERWRITE" "${JOB}.dat"; then
  append_summary "unexpected_overwrite_marker" "unknown" "not_run" "native control dat contains overwrite marker"
  write_status "unexpected_overwrite_marker" "overwrite_check" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

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
comparison_status="not_available"
if reference_available; then
  ref_available="yes"
  comparison_status="$(run_comparison)"
fi

append_summary "completed" "$ref_available" "$comparison_status" "extraction=${extraction_status}; cycle${BLOCK_END}_state=${end_state}; no_extrapolated_overwrite=confirmed"
write_status "completed" "controller_end" "block_end=$BLOCK_END comparison=$comparison_status cycle${BLOCK_END}_state=$end_state no_extrapolated_overwrite=confirmed"
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/${CONTROLLER}_storage_df_after.txt" || true
du -sh /scratch9/"$USER" 2>/dev/null | tee "$LOG_DIR/${CONTROLLER}_storage_scratch9_user_after.txt" || true
copy_lightweight_evidence
echo "[Stage16N-${CONTROLLER}] end: $(date '+%Y-%m-%d %H:%M:%S')"
