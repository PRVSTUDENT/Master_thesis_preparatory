#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE14B="$REPO_ROOT/runs/chaboche_umat/stage14b_adaptive_deltaN_2000cycles"
LOG_DIR="$STAGE14B/_logs"
MASTER_LOG="$LOG_DIR/stage14b_adaptive_controller_hpc.log"
STATUS_FILE="$LOG_DIR/stage14b_progress_status.txt"
FINAL_CYCLE=2000
PROGRESS_TOTAL=0
PROGRESS_DONE=0
CURRENT_TASK="initializing"
START_EPOCH="$(date +%s)"

mkdir -p "$LOG_DIR"

log() {
    local stamp
    stamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$stamp] $*" | tee -a "$MASTER_LOG"
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

start_task() {
    CURRENT_TASK="$1"
    log "Task: $CURRENT_TASK"
    write_status
}

finish_task() {
    PROGRESS_DONE=$((PROGRESS_DONE + 1))
    write_status
}

run_logged() {
    local label="$1"
    shift
    log "Running: $label"
    "$@" 2>&1 | tee "$LOG_DIR/${label}.log"
}

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

log "Starting Stage 14B adaptive DeltaN controller."
log "Host: $(hostname)"
log "Repo root: $REPO_ROOT"
log "Stage dir: $STAGE14B"
log "GCC: $(gcc --version | head -1)"
log "Fortran: $(ifort --version | head -1)"
log "Abaqus: $(command -v abaqus)"
write_status

BASE_CYCLE=10
BLOCK_INDEX=1
PREVIOUS_ROUTE=""

while [[ "$BASE_CYCLE" -lt "$FINAL_CYCLE" ]]; do
    BASE_SOURCE="reference"
    PREVIOUS_ARG=()
    if [[ "$BLOCK_INDEX" -gt 1 ]]; then
        BASE_SOURCE="previous_block"
        PREVIOUS_ARG=(--previous-route-csv "$PREVIOUS_ROUTE")
    fi

    start_task "block ${BLOCK_INDEX} adaptive generation"
    run_logged "block$(printf '%02d' "$BLOCK_INDEX")_generate_console" \
        python3 "$STAGE14B/make_stage14b_block_job.py" \
            --block-index "$BLOCK_INDEX" \
            --base-cycle "$BASE_CYCLE" \
            --repo-root "$REPO_ROOT" \
            --base-source "$BASE_SOURCE" \
            "${PREVIOUS_ARG[@]}"
    finish_task

    METADATA="$(find "$STAGE14B/strategy_adaptive" -path "*block$(printf '%02d' "$BLOCK_INDEX")_*" -name "stage14b_adaptive_block$(printf '%02d' "$BLOCK_INDEX")_metadata.csv" | sort | tail -1)"
    if [[ -z "$METADATA" || ! -f "$METADATA" ]]; then
        echo "Missing metadata for block $BLOCK_INDEX" >&2
        exit 1
    fi

    CASE_DIR="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["case_dir"])
PY
)"
    JOB="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["job"])
PY
)"
    INP="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["inp"])
PY
)"
    USER_SUB="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["user"])
PY
)"
    POST="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["post"])
PY
)"
    RECOVERY_END="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["recovery_end_cycle"])
PY
)"
    ROUTE_CSV="$(python3 - "$METADATA" <<'PY'
import csv, sys
row = next(csv.DictReader(open(sys.argv[1])))
print(row["route_csv"])
PY
)"

    if [[ ! -f "$CASE_DIR/${JOB}_datacheck.dat" ]] || ! grep -q "ANALYSIS DATACHECK COMPLETE" "$CASE_DIR/${JOB}_datacheck.dat"; then
        start_task "block ${BLOCK_INDEX} datacheck"
        (
            cd "$CASE_DIR"
            run_logged "${JOB}_datacheck_console" \
                abaqus job="${JOB}_datacheck" input="$INP" user="$USER_SUB" datacheck interactive ask_delete=OFF scratch=.
        )
    fi
    finish_task

    if [[ ! -f "$CASE_DIR/${JOB}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "$CASE_DIR/${JOB}.sta"; then
        start_task "block ${BLOCK_INDEX} full analysis"
        (
            cd "$CASE_DIR"
            run_logged "${JOB}_full_console" \
                abaqus job="$JOB" input="$INP" user="$USER_SUB" interactive ask_delete=OFF scratch=.
        )
    fi
    finish_task

    start_task "block ${BLOCK_INDEX} postprocess"
    (
        cd "$CASE_DIR"
        run_logged "${JOB}_postprocess_console" abaqus python "$POST"
    )
    finish_task

    start_task "block ${BLOCK_INDEX} summary update"
    run_logged "block$(printf '%02d' "$BLOCK_INDEX")_summary_console" \
        python3 "$STAGE14B/stage14b_update_summary.py" \
            --stage-dir "$STAGE14B" \
            --metadata "$METADATA"
    finish_task

    BASE_CYCLE="$RECOVERY_END"
    PREVIOUS_ROUTE="$ROUTE_CSV"
    BLOCK_INDEX=$((BLOCK_INDEX + 1))
done

log "Stage 14B adaptive DeltaN controller finished."
log "Summary CSV: $STAGE14B/STAGE14B_ADAPTIVE_SUMMARY.csv"
log "Block history: $STAGE14B/STAGE14B_ADAPTIVE_BLOCK_HISTORY.csv"
log "Report: $STAGE14B/STAGE14B_ADAPTIVE_REPORT.md"
