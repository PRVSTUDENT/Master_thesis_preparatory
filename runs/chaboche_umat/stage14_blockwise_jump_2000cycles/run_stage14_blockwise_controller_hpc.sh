#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE14="$REPO_ROOT/runs/chaboche_umat/stage14_blockwise_jump_2000cycles"
REF_DIR="$STAGE14/reference_2000cycles"
LOG_DIR="$STAGE14/_logs"
MASTER_LOG="$LOG_DIR/stage14_blockwise_controller_hpc.log"
STATUS_FILE="$LOG_DIR/stage14_progress_status.txt"
MAIL_TO="${MAIL_TO:-pr21vyci@mailserver.tu-freiberg.de}"
PROGRESS_TOTAL=59
PROGRESS_DONE=0
CURRENT_TASK="initializing"
START_EPOCH="$(date +%s)"
PROGRESS_MAIL_PID=""

mkdir -p "$REF_DIR" "$LOG_DIR"

log() {
    local stamp
    stamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$stamp] $*" | tee -a "$MASTER_LOG"
}

run_logged() {
    local label="$1"
    shift
    log "Running: $label"
    "$@" 2>&1 | tee "$LOG_DIR/${label}.log"
}

write_status() {
    {
        printf 'job_id=%q\n' "${PBS_JOBID:-manual}"
        printf 'host=%q\n' "$(hostname)"
        printf 'started=%q\n' "$(date -d "@$START_EPOCH" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date)"
        printf 'updated=%q\n' "$(date '+%Y-%m-%d %H:%M:%S')"
        echo "progress_done=$PROGRESS_DONE"
        echo "progress_total=$PROGRESS_TOTAL"
        printf 'current_task=%q\n' "$CURRENT_TASK"
    } > "$STATUS_FILE"
}

progress_bar() {
    local done="$1"
    local total="$2"
    local width=24
    local filled=0
    if [[ "$total" -gt 0 ]]; then
        filled=$(( done * width / total ))
    fi
    local empty=$(( width - filled ))
    printf '[%*s%*s] %d/%d' "$filled" '' "$empty" '' "$done" "$total" | tr ' ' '#'
}

send_progress_mail() {
    local reason="${1:-3-hour update}"
    local elapsed=$(( ($(date +%s) - START_EPOCH) / 60 ))
    local bar
    bar="$(progress_bar "$PROGRESS_DONE" "$PROGRESS_TOTAL")"
    {
        echo "Stage 14 HPC progress update"
        echo
        echo "Reason: $reason"
        echo "PBS job: ${PBS_JOBID:-manual}"
        echo "Host: $(hostname)"
        echo "Elapsed minutes: $elapsed"
        echo "Progress: $bar"
        echo "Current task: $CURRENT_TASK"
        echo
        echo "Last controller log lines:"
        tail -40 "$MASTER_LOG" 2>/dev/null || true
        echo
        echo "Summary so far:"
        if [[ -f "$STAGE14/STAGE14_BLOCKWISE_SUMMARY.csv" ]]; then
            tail -20 "$STAGE14/STAGE14_BLOCKWISE_SUMMARY.csv"
        else
            echo "No summary CSV yet."
        fi
    } | mail -s "Stage 14 ${PBS_JOBID:-manual}: $reason" "$MAIL_TO" || true
}

start_progress_mailer() {
    (
        while true; do
            sleep 10800
            if [[ -f "$STATUS_FILE" ]]; then
                # shellcheck disable=SC1090
                source "$STATUS_FILE" 2>/dev/null || true
                PROGRESS_DONE="${progress_done:-$PROGRESS_DONE}"
                PROGRESS_TOTAL="${progress_total:-$PROGRESS_TOTAL}"
                CURRENT_TASK="${current_task:-$CURRENT_TASK}"
            fi
            send_progress_mail "3-hour update"
        done
    ) &
    PROGRESS_MAIL_PID="$!"
}

finish_task() {
    PROGRESS_DONE=$((PROGRESS_DONE + 1))
    write_status
}

start_task() {
    CURRENT_TASK="$1"
    log "Task: $CURRENT_TASK"
    write_status
}

cleanup() {
    if [[ -n "$PROGRESS_MAIL_PID" ]]; then
        kill "$PROGRESS_MAIL_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT

assert_file() {
    if [[ ! -f "$1" ]]; then
        echo "Missing required file: $1" >&2
        exit 1
    fi
}

module purge
module load intel/2024.2.0
module load abaqus/2023

log "Starting Stage 14 HPC blockwise controller."
log "Host: $(hostname)"
log "Repo root: $REPO_ROOT"
log "Stage dir: $STAGE14"
log "Abaqus: $(command -v abaqus)"
write_status
start_progress_mailer

REF_JOB="chaboche_vp_v1_cyclic_eps005_2000cycles"
REF_CSV="$REF_DIR/${REF_JOB}_cycle_history.csv"

if [[ ! -f "$REF_DIR/${REF_JOB}.inp" || ! -f "$REF_DIR/umat_chaboche_v1_with_sdvini_sigini.f" || ! -f "$REF_DIR/extract_2000cycle_reference_history.py" ]]; then
    start_task "reference deck generation"
    run_logged "stage14_reference_generate" python3 "$STAGE14/make_2000cycle_reference_deck.py"
fi
finish_task

assert_file "$REF_DIR/${REF_JOB}.inp"
assert_file "$REF_DIR/umat_chaboche_v1_with_sdvini_sigini.f"
assert_file "$REF_DIR/extract_2000cycle_reference_history.py"

if [[ ! -f "$REF_DIR/${REF_JOB}_datacheck.dat" ]] || ! grep -q "ANALYSIS DATACHECK COMPLETE" "$REF_DIR/${REF_JOB}_datacheck.dat"; then
    start_task "reference datacheck"
    (
        cd "$REF_DIR"
        run_logged "${REF_JOB}_datacheck_console" \
            abaqus job="${REF_JOB}_datacheck" input="${REF_JOB}.inp" user=umat_chaboche_v1_with_sdvini_sigini.f datacheck interactive ask_delete=OFF scratch=.
    )
fi
finish_task

if [[ ! -f "$REF_DIR/${REF_JOB}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "$REF_DIR/${REF_JOB}.sta"; then
    start_task "reference full 2000-cycle analysis"
    (
        cd "$REF_DIR"
        run_logged "${REF_JOB}_full_console" \
            abaqus job="$REF_JOB" input="${REF_JOB}.inp" user=umat_chaboche_v1_with_sdvini_sigini.f interactive ask_delete=OFF scratch=.
    )
fi
finish_task

if [[ ! -f "$REF_CSV" ]]; then
    start_task "reference cycle-history extraction"
    (
        cd "$REF_DIR"
        run_logged "${REF_JOB}_extract_console" abaqus python extract_2000cycle_reference_history.py
    )
fi
finish_task

assert_file "$REF_CSV"
python3 - "$REF_CSV" <<'PY'
import csv
import sys
path = sys.argv[1]
rows = list(csv.DictReader(open(path)))
if len(rows) != 2000:
    raise SystemExit("Expected 2000 reference rows, got %d" % len(rows))
if int(rows[0]["cycle"]) != 1 or int(rows[-1]["cycle"]) != 2000:
    raise SystemExit("Reference cycle range is not 1..2000")
print("Reference CSV validated: 2000 rows")
PY

run_block() {
    local strategy="$1"
    local block="$2"
    local base="$3"
    local target="$4"
    local continue_to="$5"
    local source="reference"
    if [[ "$block" != "1" ]]; then
        source="previous_block"
    fi

    local block2
    block2="$(printf "%02d" "$block")"
    local case_dir="$STAGE14/strategy_${strategy}/block${block2}_base${base}_target${target}_to${continue_to}"
    local job="chaboche_stage14_${strategy}_block${block2}_target${target}_to${continue_to}"
    local inp="${job}.inp"
    local user="umat_chaboche_v1_with_sdvini_sigini_predicted_cycle${target}.f"
    local post="postprocess_${job}.py"

    log "Preparing ${strategy} block ${block2}: base=${base}, target=${target}, continue=${continue_to}, source=${source}"
    start_task "${strategy} block ${block2} generation"
    run_logged "${strategy}_block${block2}_generate_console" \
        python3 "$STAGE14/make_stage14_block_job.py" \
            --strategy-label "$strategy" \
            --block-index "$block" \
            --base-cycle "$base" \
            --target-cycle "$target" \
            --continue-to-cycle "$continue_to" \
            --repo-root "$REPO_ROOT" \
            --base-source "$source"
    finish_task

    if [[ ! -f "$case_dir/${job}_datacheck.dat" ]] || ! grep -q "ANALYSIS DATACHECK COMPLETE" "$case_dir/${job}_datacheck.dat"; then
        start_task "${strategy} block ${block2} datacheck"
        (
            cd "$case_dir"
            run_logged "${job}_datacheck_console" \
                abaqus job="${job}_datacheck" input="$inp" user="$user" datacheck interactive ask_delete=OFF scratch=.
        )
    fi
    finish_task

    if [[ ! -f "$case_dir/${job}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "$case_dir/${job}.sta"; then
        start_task "${strategy} block ${block2} full analysis"
        (
            cd "$case_dir"
            run_logged "${job}_full_console" \
                abaqus job="$job" input="$inp" user="$user" interactive ask_delete=OFF scratch=.
        )
    fi
    finish_task

    start_task "${strategy} block ${block2} postprocess"
    (
        cd "$case_dir"
        run_logged "${job}_postprocess_console" abaqus python "$post"
    )
    finish_task

    start_task "${strategy} block ${block2} summary update"
    run_logged "${strategy}_block${block2}_summary_console" \
        python3 "$STAGE14/stage14_update_summary.py" \
            --stage-dir "$STAGE14" \
            --strategy "$strategy" \
            --block-index "$block" \
            --base-cycle "$base" \
            --target-cycle "$target" \
            --continue-to-cycle "$continue_to" \
            --case-dir "$case_dir"
    finish_task
}

run_block jump25 1 10 500 510
run_block jump25 2 510 1000 1010
run_block jump25 3 1010 1500 1510
run_block jump25 4 1510 1990 2000

run_block jump37 1 10 740 750
run_block jump37 2 750 1480 1490
run_block jump37 3 1490 1990 2000

run_block jump50 1 10 1000 1010
run_block jump50 2 1010 1990 2000

run_block jump65 1 10 1300 1310
run_block jump65 2 1310 1990 2000

log "Stage 14 HPC blockwise controller finished."
log "Summary CSV: $STAGE14/STAGE14_BLOCKWISE_SUMMARY.csv"
log "Report: $STAGE14/STAGE14_BLOCKWISE_REPORT.md"
