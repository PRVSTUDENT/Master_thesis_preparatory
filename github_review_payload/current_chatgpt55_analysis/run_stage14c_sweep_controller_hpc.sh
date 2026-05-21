#!/usr/bin/env bash
set -u -o pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE14C="$REPO_ROOT/runs/chaboche_umat/stage14c_adaptive_sweep_2000cycles"
LOG_DIR="$STAGE14C/_logs"
MASTER_LOG="$LOG_DIR/stage14c_sweep_controller_hpc.log"
STATUS_FILE="$LOG_DIR/stage14c_progress_status.txt"
FINAL_CYCLE=2000
SANITY_ONLY="${SANITY_ONLY:-1}"
MAX_CASES="${MAX_CASES:-999}"
START_EPOCH="$(date +%s)"
PROGRESS_DONE=0
PROGRESS_TOTAL=0
CURRENT_TASK="initializing"

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
        echo "sanity_only=$SANITY_ONLY"
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
    return "${PIPESTATUS[0]}"
}

read_meta_field() {
    python3 - "$1" "$2" <<'PY'
import csv
import sys
field = sys.argv[2]
with open(sys.argv[1], "r") as handle:
    row = next(csv.DictReader(handle))
print(row[field])
PY
}

append_failure_summary() {
    local case_id="$1"
    local stage="$2"
    local message="$3"
    python3 - "$STAGE14C" "$case_id" "$stage" "$message" <<'PY'
import csv
import os
import sys

stage_dir, case_id, stage, message = sys.argv[1:5]
path = os.path.join(stage_dir, "STAGE14C_SWEEP_CASE_SUMMARY.csv")
fields = [
    "case_id", "case_group", "config_name", "LOCAL_TOL", "SAFETY_FACTOR", "DN_MIN", "DN_MAX",
    "RECOVERY_WINDOW", "prediction_order", "deltaN_control_variables", "injection_mode",
    "rollback_enabled", "final_cycle", "final_STATEV1", "reference_STATEV1",
    "final_statev1_error_pct", "final_S11", "reference_S11", "final_s11_error_pct",
    "final_RIGHT_FACE_RF1_SUM", "reference_RIGHT_FACE_RF1_SUM", "final_rf1_error_pct",
    "outcome", "number_of_blocks", "solved_recovery_cycles", "skipped_cycles",
    "effective_speedup_estimate", "first_failed_block", "first_failed_base_cycle",
    "first_failed_target_cycle", "first_failed_recovery_end_cycle", "max_m_STATEV1",
    "max_c_STATEV1", "notes",
]
rows = []
if os.path.exists(path):
    with open(path, "r") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("case_id") != case_id]
row = dict((field, "") for field in fields)
row.update({
    "case_id": case_id,
    "case_group": case_id[:1],
    "config_name": case_id,
    "outcome": "runtime_error",
    "notes": "%s: %s" % (stage, message),
})
rows.append(row)
rows.sort(key=lambda item: item.get("case_id", ""))
for output in [path, os.path.join(stage_dir, "STAGE14C_SWEEP_MASTER_SUMMARY.csv")]:
    with open(output, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
PY
}

run_case() {
    local case_id="$1"
    local local_tol="$2"
    local safety="$3"
    local dn_min="$4"
    local dn_max="$5"
    local recovery="$6"
    local prediction_order="$7"
    local control_vars="$8"
    local injection_mode="$9"
    local stop_after_first_block="${10:-0}"

    log "Starting case $case_id: tol=$local_tol safety=$safety dn_min=$dn_min dn_max=$dn_max recovery=$recovery prediction=$prediction_order control=$control_vars injection=$injection_mode"
    local base_cycle=10
    local block_index=1
    local previous_route=""

    while [[ "$base_cycle" -lt "$FINAL_CYCLE" ]]; do
        local base_source="reference"
        local previous_arg=()
        if [[ "$block_index" -gt 1 ]]; then
            base_source="previous_block"
            previous_arg=(--previous-route-csv "$previous_route")
        fi

        start_task "$case_id block $block_index generation"
        if ! run_logged "${case_id}_block$(printf '%02d' "$block_index")_generate_console" \
            python3 "$STAGE14C/make_stage14c_block_job.py" \
                --case-id "$case_id" \
                --block-index "$block_index" \
                --base-cycle "$base_cycle" \
                --repo-root "$REPO_ROOT" \
                --base-source "$base_source" \
                --local-tol "$local_tol" \
                --safety-factor "$safety" \
                --dn-min "$dn_min" \
                --dn-max "$dn_max" \
                --recovery-window "$recovery" \
                --prediction-order "$prediction_order" \
                --delta-n-control-variables "$control_vars" \
                --injection-mode "$injection_mode" \
                "${previous_arg[@]}"; then
            append_failure_summary "$case_id" "generation" "block $block_index failed"
            return 1
        fi
        finish_task

        local metadata
        metadata="$(find "$STAGE14C/strategy_${case_id}" -path "*block$(printf '%02d' "$block_index")_*" -name "stage14c_${case_id}_block$(printf '%02d' "$block_index")_metadata.csv" | sort | tail -1)"
        if [[ -z "$metadata" || ! -f "$metadata" ]]; then
            append_failure_summary "$case_id" "metadata" "missing metadata for block $block_index"
            return 1
        fi

        local case_dir job inp user_sub post recovery_end route_csv
        case_dir="$(read_meta_field "$metadata" case_dir)"
        job="$(read_meta_field "$metadata" job)"
        inp="$(read_meta_field "$metadata" inp)"
        user_sub="$(read_meta_field "$metadata" user)"
        post="$(read_meta_field "$metadata" post)"
        recovery_end="$(read_meta_field "$metadata" recovery_end_cycle)"
        route_csv="$(read_meta_field "$metadata" route_csv)"

        start_task "$case_id block $block_index datacheck"
        (
            cd "$case_dir" || exit 1
            run_logged "${job}_datacheck_console" \
                abaqus job="${job}_datacheck" input="$inp" user="$user_sub" datacheck interactive ask_delete=OFF scratch=.
        )
        local rc=$?
        finish_task
        if [[ "$rc" -ne 0 || ! -f "$case_dir/${job}_datacheck.dat" ]] || ! grep -q "ANALYSIS DATACHECK COMPLETE" "$case_dir/${job}_datacheck.dat"; then
            append_failure_summary "$case_id" "datacheck" "block $block_index datacheck failed"
            return 1
        fi

        start_task "$case_id block $block_index full analysis"
        (
            cd "$case_dir" || exit 1
            run_logged "${job}_full_console" \
                abaqus job="$job" input="$inp" user="$user_sub" interactive ask_delete=OFF scratch=.
        )
        rc=$?
        finish_task
        if [[ "$rc" -ne 0 || ! -f "$case_dir/${job}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "$case_dir/${job}.sta"; then
            append_failure_summary "$case_id" "analysis" "block $block_index analysis failed"
            return 1
        fi

        start_task "$case_id block $block_index postprocess"
        (
            cd "$case_dir" || exit 1
            run_logged "${job}_postprocess_console" abaqus python "$post"
        )
        rc=$?
        finish_task
        if [[ "$rc" -ne 0 ]]; then
            append_failure_summary "$case_id" "postprocess" "block $block_index postprocess failed"
            return 1
        fi

        start_task "$case_id block $block_index summary update"
        run_logged "${case_id}_block$(printf '%02d' "$block_index")_summary_console" \
            python3 "$STAGE14C/stage14c_update_summary.py" \
                --stage-dir "$STAGE14C" \
                --metadata "$metadata"
        rc=$?
        finish_task
        if [[ "$rc" -ne 0 ]]; then
            append_failure_summary "$case_id" "summary" "block $block_index summary update failed"
            return 1
        fi

        if [[ "$stop_after_first_block" == "1" ]]; then
            log "Case $case_id sanity mode completed one full block successfully."
            return 0
        fi

        base_cycle="$recovery_end"
        previous_route="$route_csv"
        block_index=$((block_index + 1))
    done

    log "Case $case_id finished."
    return 0
}

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

log "Starting Stage 14C adaptive sweep controller."
log "Host: $(hostname)"
log "Repo root: $REPO_ROOT"
log "Stage dir: $STAGE14C"
log "SANITY_ONLY: $SANITY_ONLY"
log "GCC: $(gcc --version | head -1)"
log "Fortran: $(ifort --version | head -1)"
log "Abaqus: $(command -v abaqus)"
write_status

if [[ "$SANITY_ONLY" == "1" ]]; then
    PROGRESS_TOTAL=5
    run_case "S00" "0.001" "0.70" "1" "25" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "1"
    log "Stage 14C sanity-only controller finished."
    exit $?
fi

PROGRESS_TOTAL=999
case_count=0
run_case "B1" "0.001" "0.70" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "B2" "0.001" "0.70" "1" "150" "25" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "B3" "0.001" "0.70" "1" "150" "50" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "C1" "0.001" "0.70" "1" "25" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "C2" "0.001" "0.70" "1" "50" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "C5" "0.001" "0.70" "1" "25" "25" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "C6" "0.001" "0.70" "1" "50" "25" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "D2" "0.0005" "0.70" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0
run_case "D4" "0.001" "0.50" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "0"; case_count=$((case_count + 1)); [[ "$case_count" -ge "$MAX_CASES" ]] && exit 0

log "Stage 14C sweep controller finished selected priority cases."
