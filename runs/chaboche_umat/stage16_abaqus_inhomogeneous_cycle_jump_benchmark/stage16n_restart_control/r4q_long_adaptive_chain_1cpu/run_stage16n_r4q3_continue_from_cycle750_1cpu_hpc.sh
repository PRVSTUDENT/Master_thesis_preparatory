#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="R4Q3_continue_from_cycle750_1cpu"
PREVIOUS_SCRATCH_DIR="${PREVIOUS_SCRATCH_DIR:-/scratch/$USER/stage16n_r4q2_continue_from_cycle500_1cpu/1362597.mmaster02}"
OLDJOB="stage16n_r4q2_block02_500_to_521_solve_522_to_750"
JOB="stage16n_r4q3_block03_750_to_771_solve_772_to_1000"
SOURCE_CYCLE=750
PREVIOUS_CYCLE=500
JUMP_TARGET=771
SOLVED_START=772
BLOCK_END=1000
RESTART_STEP=""
RESTART_INC=""
START_EPOCH="$(date +%s)"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
MAIL_TO="${MAIL_TO:-${USER}@mailserver.tu-freiberg.de}"
MAIL_SUBJECT_PREFIX="${MAIL_SUBJECT_PREFIX:-Stage16N-R4Q3 continue from cycle750}"
JOB_FINAL_STATUS="starting"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH" "_source_state"

exec > >(tee -a R4Q3_CONTINUE_CONTROLLER.log) 2>&1

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
    echo "source_cycle=$SOURCE_CYCLE"
    echo "jump_target=$JUMP_TARGET"
    echo "solved_start=$SOLVED_START"
    echo "block_end=$BLOCK_END"
    echo "restart_step=$RESTART_STEP"
    echo "restart_inc=$RESTART_INC"
    echo "abaqus_cpus=${ABAQUS_CPUS:-1}"
    echo "scratch_case_dir=${SCRATCH_CASE_DIR:-$PWD}"
    echo "elapsed_seconds=$(elapsed_seconds)"
    echo "updated_at=$(date '+%Y-%m-%d %H:%M:%S')"
  } > R4Q3_CONTINUE_STATUS.txt
}

write_preflight_status() {
  local status="$1"
  local detail="$2"
  {
    echo "status=$status"
    echo "detail=$detail"
    echo "controller=$CONTROLLER"
    echo "previous_scratch_dir=$PREVIOUS_SCRATCH_DIR"
    echo "oldjob=$OLDJOB"
    echo "job=$JOB"
    echo "source_cycle=$SOURCE_CYCLE"
    echo "jump_target=$JUMP_TARGET"
    echo "solved_start=$SOLVED_START"
    echo "block_end=$BLOCK_END"
    echo "restart_step=$RESTART_STEP"
    echo "restart_inc=$RESTART_INC"
    echo "deck=${JOB}.inp"
    if [[ -s "${JOB}.inp" ]]; then
      grep '^\*RESTART, READ' "${JOB}.inp" | head -n 1 | sed 's/^/restart_line=/'
    else
      echo "restart_line="
    fi
    echo "updated_at=$(date '+%Y-%m-%d %H:%M:%S')"
  } > R4Q3_PREFLIGHT_STATUS.txt
}

init_summary() {
  echo "block_index,source_cycle,jump_target,solved_start,block_end,status,classification_scope,reference_available,comparison_status,job,oldjob,elapsed_seconds,detail" > R4Q3_CONTINUE_BLOCK_SUMMARY.csv
}

append_summary() {
  local status="$1"
  local scope="$2"
  local ref_available="$3"
  local comparison_status="$4"
  local detail="$5"
  echo "3,$SOURCE_CYCLE,$JUMP_TARGET,$SOLVED_START,$BLOCK_END,$status,$scope,$ref_available,$comparison_status,$JOB,$OLDJOB,$(elapsed_seconds),\"$detail\"" >> R4Q3_CONTINUE_BLOCK_SUMMARY.csv
}

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${HOME_CASE_DIR:-}" ]]; then
    if [[ -n "${SCRATCH_BASE:-}" && -s "$SCRATCH_BASE/r4q3_continue.pbs.out" ]]; then
      cp "$SCRATCH_BASE/r4q3_continue.pbs.out" "$PWD/r4q3_continue.pbs.out" || true
    fi
    rsync -av \
      --include='*/' \
      --exclude='state.bin' \
      --exclude='state.csv' \
      --include='R4Q3*.txt' \
      --include='R4Q3*.csv' \
      --include='R4Q3*.log' \
      --include='qstat_r4q3*.txt' \
      --include='R4Q3_SOURCE*.md' \
      --include="${JOB}.inp" \
      --include="${JOB}_comparison_*.csv" \
      --include="${JOB}_*_tail.txt" \
      --include="${JOB}_cycle_metrics.csv" \
      --include="${JOB}_selected_cycle_local_states.csv" \
      --include="${JOB}_selected_cycle_loops.csv" \
      --include='_source_state/stage16n_exact_state_cycle1000_summary.md' \
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
  local ext
  for ext in sta res stt mdl prt sim odb; do
    if [[ ! -s "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}" ]]; then
      write_status "previous_source_missing" "preflight" "missing $PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}"
      write_preflight_status "failed" "missing $PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}"
      copy_lightweight_evidence
      exit 0
    fi
  done
  read -r RESTART_STEP RESTART_INC < <(resolve_restart_from_sta "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.sta")
  if [[ -z "$RESTART_STEP" || -z "$RESTART_INC" ]]; then
    write_status "restart_record_missing" "preflight" "could not resolve step/inc from $PREVIOUS_SCRATCH_DIR/${OLDJOB}.sta"
    write_preflight_status "failed" "could not resolve restart step/inc"
    copy_lightweight_evidence
    exit 0
  fi
  for ext in sta res stt mdl prt sim odb; do
    ln -sfn "$PREVIOUS_SCRATCH_DIR/${OLDJOB}.${ext}" "${OLDJOB}.${ext}"
  done
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle0500.csv" _source_state/
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle0750.csv" _source_state/
  cp "$PREVIOUS_SCRATCH_DIR/_source_state/stage16n_exact_state_cycle0750_summary.md" _source_state/ || true
}

prepare_jump_state() {
  rm -f state.bin state.csv
  python3 stage16n_make_extrapolated_state.py \
    --previous-csv "_source_state/stage16n_exact_state_cycle0500.csv" \
    --base-csv "_source_state/stage16n_exact_state_cycle0750.csv" \
    --previous-cycle "$PREVIOUS_CYCLE" \
    --base-cycle "$SOURCE_CYCLE" \
    --jump-cycles "$((JUMP_TARGET - SOURCE_CYCLE))" \
    --output-cycle "$JUMP_TARGET" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary "R4Q3_SOURCE${SOURCE_CYCLE}_TARGET${JUMP_TARGET}_EXTRAPOLATED_STATE.md"
}

make_deck() {
  python3 stage16n_make_r4q_restart_deck.py \
    --output "${JOB}.inp" \
    --old-step "$RESTART_STEP" \
    --old-inc "$RESTART_INC" \
    --solved-start "$SOLVED_START" \
    --block-end "$BLOCK_END" \
    --title "Stage 16N-R4Q3: ${SOURCE_CYCLE} to ${JUMP_TARGET}, solve ${SOLVED_START} to ${BLOCK_END}"
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

extract_state_cycle_1000() {
  run_logged_phase "extract source state cycle 1000 from ${JOB}" "$LOG_DIR/${JOB}_extract_state_1000.log" \
    abaqus python stage16n_extract_exact_state_for_reinjection.py \
      --odb "${JOB}.odb" \
      --cycles "$BLOCK_END" \
      --outdir _source_state
}

on_error() {
  local rc=$?
  write_status "controller_failure" "trap" "exit code $rc"
  write_preflight_status "failed" "controller trap exit code $rc"
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

echo "[Stage16N-R4Q3] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4Q3] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4Q3] scratch: ${SCRATCH_CASE_DIR:-$PWD}"
echo "[Stage16N-R4Q3] previous source: $PREVIOUS_SCRATCH_DIR/$OLDJOB"
send_job_mail "BEGIN" "started"
init_summary
write_status "starting" "preflight" "checking previous cycle750 source"
verify_previous_source
write_status "running" "prepare" "source=$SOURCE_CYCLE target=$JUMP_TARGET solve=$SOLVED_START-$BLOCK_END"
prepare_jump_state
make_deck
write_preflight_status "passed" "deck generated with parsed restart step/inc"
copy_lightweight_evidence

if [[ "${R4Q3_PREFLIGHT_ONLY:-0}" == "1" ]]; then
  write_status "preflight_passed" "preflight_only" "deck generated; no Abaqus submitted"
  append_summary "preflight_passed" "preflight" "unknown" "not_run" "deck=${JOB}.inp restart_step=${RESTART_STEP} restart_inc=${RESTART_INC}"
  echo "[Stage16N-R4Q3] preflight-only end: $(date '+%Y-%m-%d %H:%M:%S')"
  exit 0
fi

export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
export STAGE16N_JUMP_TARGET_STEP="$((SOURCE_CYCLE + 1))"
export STAGE16N_JUMP_CHECK_TIME="$SOURCE_CYCLE"

if ! run_logged_phase "R4Q3 datacheck" "$LOG_DIR/${JOB}_datacheck.log" \
  abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_r3_jump_umat.for \
    datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
  write_tails "$JOB"
  append_summary "datacheck_failure" "accuracy_validation_candidate" "unknown" "not_run" "datacheck failed"
  write_status "datacheck_failure" "datacheck" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

if ! run_logged_phase "R4Q3 solve" "$LOG_DIR/${JOB}.log" \
  abaqus job="$JOB" input="${JOB}.inp" oldjob="$OLDJOB" \
    user=stage16n_r3_jump_umat.for \
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
    cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
  write_tails "$JOB"
  append_summary "solve_failure" "accuracy_validation_candidate" "unknown" "not_run" "solve failed"
  write_status "solve_failure" "solve" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

write_tails "$JOB"
if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
  append_summary "sta_not_successful" "accuracy_validation_candidate" "unknown" "not_run" "sta lacks successful completion line"
  write_status "sta_not_successful" "sta_check" "$JOB"
  copy_lightweight_evidence
  exit 0
fi

grep "STAGE16N_R3J_OVERWRITE" "${JOB}.dat" > "$LOG_DIR/${JOB}_overwrite_trace.txt" || true
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" > "$LOG_DIR/${JOB}_parallelism_check.log" || true

extraction_status="not_run"
if run_logged_phase "R4Q3 ODB extraction" "$LOG_DIR/${JOB}_extract.log" \
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB"; then
  extraction_status="ok"
else
  extraction_status="failed"
fi

cycle1000_state="not_run"
if extract_state_cycle_1000; then
  cycle1000_state="ok"
else
  cycle1000_state="failed"
fi

ref_available="no"
scope="feasibility"
comparison_status="not_available"
if reference_available_for "$BLOCK_END"; then
  ref_available="yes"
  scope="accuracy_validation"
  comparison_status="$(run_comparison_if_available "$JOB" "$BLOCK_END")"
fi

append_summary "completed" "$scope" "$ref_available" "$comparison_status" "extraction=${extraction_status}; cycle1000_state=${cycle1000_state}"
write_status "completed" "controller_end" "block_end=$BLOCK_END scope=$scope comparison=$comparison_status cycle1000_state=$cycle1000_state"
df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/R4Q3_storage_df_after.txt" || true
du -sh /scratch9/"$USER" 2>/dev/null | tee "$LOG_DIR/R4Q3_storage_scratch9_user_after.txt" || true
copy_lightweight_evidence
echo "[Stage16N-R4Q3] end: $(date '+%Y-%m-%d %H:%M:%S')"
