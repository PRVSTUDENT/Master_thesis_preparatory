#!/usr/bin/env bash
set -u -o pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE14D="$REPO_ROOT/runs/chaboche_umat/stage14d_24h_controller_sweep_2000cycles"
LOG_DIR="$STAGE14D/_logs"
MASTER_LOG="$LOG_DIR/stage14d_24h_controller_hpc.log"
STATUS_FILE="$LOG_DIR/stage14d_progress_status.txt"
RUNTIME_DIAG="$STAGE14D/STAGE14D_24H_RUNTIME_ERROR_DIAGNOSTICS.csv"
FINAL_CYCLE=2000
SKIP_COMPLETED="${SKIP_COMPLETED:-1}"
MAX_CASES="${MAX_CASES:-9999}"
PARALLEL_LANES="${PARALLEL_LANES:-3}"
CPUS_PER_CASE="${CPUS_PER_CASE:-8}"
WALLTIME_STOP_SECONDS="${WALLTIME_STOP_SECONDS:-84000}"
START_EPOCH="$(date +%s)"
PROGRESS_DONE=0
PROGRESS_TOTAL=97
CURRENT_TASK="initializing"
case_count=0

mkdir -p "$LOG_DIR"

log() {
    local stamp
    stamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$stamp] $*" | tee -a "$MASTER_LOG"
}

elapsed_seconds() {
    echo $(( $(date +%s) - START_EPOCH ))
}

walltime_allows_new_case() {
    [[ "$(elapsed_seconds)" -lt "$WALLTIME_STOP_SECONDS" ]]
}

write_status() {
    {
        printf 'job_id=%q\n' "${PBS_JOBID:-manual}"
        printf 'host=%q\n' "$(hostname)"
        printf 'started=%q\n' "$(date -d "@$START_EPOCH" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date)"
        printf 'updated=%q\n' "$(date '+%Y-%m-%d %H:%M:%S')"
        echo "elapsed_seconds=$(elapsed_seconds)"
        echo "walltime_stop_seconds=$WALLTIME_STOP_SECONDS"
        echo "parallel_lanes=$PARALLEL_LANES"
        echo "cpus_per_case=$CPUS_PER_CASE"
        echo "progress_done=$PROGRESS_DONE"
        echo "progress_total=$PROGRESS_TOTAL"
        echo "case_count=$case_count"
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

init_outputs() {
    if [[ ! -f "$RUNTIME_DIAG" ]]; then
        printf 'case_id,case_group,stage,block_id,base_cycle,target_cycle,recovery_end_cycle,case_dir,job,reason,sta_tail,msg_tail,dat_error_extract,console_tail\n' > "$RUNTIME_DIAG"
    fi
}

append_failure_summary() {
    local case_id="$1"
    local group="$2"
    local local_tol="$3"
    local safety="$4"
    local dn_min="$5"
    local dn_max="$6"
    local recovery="$7"
    local prediction_order="$8"
    local control_vars="$9"
    local injection_mode="${10}"
    local rollback_enabled="${11}"
    local stage="${12}"
    local message="${13}"
    python3 - "$STAGE14D" "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "$stage" "$message" <<'PY'
import csv
import os
import sys

stage_dir, case_id, group = sys.argv[1:4]
local_tol, safety, dn_min, dn_max, recovery = sys.argv[4:9]
prediction_order, control_vars, injection_mode, rollback_enabled, stage, message = sys.argv[9:15]
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
path = os.path.join(stage_dir, "STAGE14D_24H_CASE_SUMMARY.csv")
if os.path.exists(path):
    with open(path, "r") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("case_id") != case_id]
row = dict((field, "") for field in fields)
row.update({
    "case_id": case_id,
    "case_group": group,
    "config_name": case_id,
    "LOCAL_TOL": local_tol,
    "SAFETY_FACTOR": safety,
    "DN_MIN": dn_min,
    "DN_MAX": dn_max,
    "RECOVERY_WINDOW": recovery,
    "prediction_order": prediction_order,
    "deltaN_control_variables": control_vars,
    "injection_mode": injection_mode,
    "rollback_enabled": rollback_enabled,
    "outcome": "runtime_error",
    "notes": "%s: %s" % (stage, message),
})
rows.append(row)
rows.sort(key=lambda item: item.get("case_id", ""))
for output in [path, os.path.join(stage_dir, "STAGE14D_24H_MASTER_SUMMARY.csv")]:
    with open(output, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
PY
}

extract_failure_tails() {
    local case_id="$1"
    local group="$2"
    local stage="$3"
    local block_index="$4"
    local metadata="${5:-}"
    local console_label="${6:-}"
    local reason="$7"
    local case_dir=""
    local job=""
    local base_cycle=""
    local target_cycle=""
    local recovery_end=""
    if [[ -n "$metadata" && -f "$metadata" ]]; then
        case_dir="$(read_meta_field "$metadata" case_dir)"
        job="$(read_meta_field "$metadata" job)"
        base_cycle="$(read_meta_field "$metadata" base_cycle)"
        target_cycle="$(read_meta_field "$metadata" target_cycle)"
        recovery_end="$(read_meta_field "$metadata" recovery_end_cycle)"
    fi
    local prefix="$STAGE14D/${case_id}"
    local sta_tail="$STAGE14D/${case_id}_STA_TAIL.txt"
    local msg_tail="$STAGE14D/${case_id}_MSG_TAIL.txt"
    local dat_extract="$STAGE14D/${case_id}_DAT_ERROR_EXTRACT.txt"
    local console_tail="$STAGE14D/${case_id}_CONSOLE_TAIL.txt"
    : > "$sta_tail"
    : > "$msg_tail"
    : > "$dat_extract"
    : > "$console_tail"
    if [[ -n "$case_dir" && -n "$job" ]]; then
        [[ -f "$case_dir/${job}.sta" ]] && tail -120 "$case_dir/${job}.sta" > "$sta_tail"
        [[ -f "$case_dir/${job}.msg" ]] && tail -160 "$case_dir/${job}.msg" > "$msg_tail"
        if [[ -f "$case_dir/${job}.dat" ]]; then
            grep -i -A4 -B4 -E "error|abort|fatal|too many attempts|excessive|zero pivot|numerical singularity" "$case_dir/${job}.dat" > "$dat_extract" || tail -160 "$case_dir/${job}.dat" > "$dat_extract"
        fi
        if [[ -f "$case_dir/${job}_datacheck.dat" && ! -s "$dat_extract" ]]; then
            grep -i -A4 -B4 -E "error|abort|fatal|too many attempts|excessive|zero pivot|numerical singularity" "$case_dir/${job}_datacheck.dat" > "$dat_extract" || tail -160 "$case_dir/${job}_datacheck.dat" > "$dat_extract"
        fi
    fi
    [[ -n "$console_label" && -f "$LOG_DIR/${console_label}.log" ]] && tail -200 "$LOG_DIR/${console_label}.log" > "$console_tail"
    python3 - "$RUNTIME_DIAG" "$case_id" "$group" "$stage" "$block_index" "$base_cycle" "$target_cycle" "$recovery_end" "$case_dir" "$job" "$reason" "$sta_tail" "$msg_tail" "$dat_extract" "$console_tail" <<'PY'
import csv
import os
import sys
path = sys.argv[1]
row = {
    "case_id": sys.argv[2],
    "case_group": sys.argv[3],
    "stage": sys.argv[4],
    "block_id": sys.argv[5],
    "base_cycle": sys.argv[6],
    "target_cycle": sys.argv[7],
    "recovery_end_cycle": sys.argv[8],
    "case_dir": sys.argv[9],
    "job": sys.argv[10],
    "reason": sys.argv[11],
    "sta_tail": sys.argv[12],
    "msg_tail": sys.argv[13],
    "dat_error_extract": sys.argv[14],
    "console_tail": sys.argv[15],
}
fields = ["case_id","case_group","stage","block_id","base_cycle","target_cycle","recovery_end_cycle","case_dir","job","reason","sta_tail","msg_tail","dat_error_extract","console_tail"]
exists = os.path.exists(path)
with open(path, "a", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    if not exists:
        writer.writeheader()
    writer.writerow(row)
PY
}

case_already_recorded() {
    local case_id="$1"
    local summary="$STAGE14D/STAGE14D_24H_CASE_SUMMARY.csv"
    if [[ "$SKIP_COMPLETED" != "1" || ! -f "$summary" ]]; then
        return 1
    fi
    python3 - "$summary" "$case_id" <<'PY'
import csv
import sys
summary, case_id = sys.argv[1:3]
with open(summary, "r") as handle:
    for row in csv.DictReader(handle):
        if row.get("case_id") == case_id:
            outcome = row.get("outcome", "")
            final_cycle = row.get("final_cycle", "")
            if outcome == "runtime_error" or final_cycle == "2000":
                sys.exit(0)
sys.exit(1)
PY
}

run_sweep_case() {
    local case_id="$1"
    shift
    if ! walltime_allows_new_case; then
        log "Walltime guard reached at $(elapsed_seconds)s; not launching $case_id."
        return 2
    fi
    if case_already_recorded "$case_id"; then
        log "Skipping already recorded case $case_id."
        return 0
    fi
    run_case "$case_id" "$@" || true
    case_count=$((case_count + 1))
    if [[ "$case_count" -ge "$MAX_CASES" ]]; then
        log "MAX_CASES=$MAX_CASES reached."
        return 2
    fi
    return 0
}

run_case() {
    local case_id="$1"
    local group="$2"
    local local_tol="$3"
    local safety="$4"
    local dn_min="$5"
    local dn_max="$6"
    local recovery="$7"
    local prediction_order="$8"
    local control_vars="$9"
    local injection_mode="${10}"
    local rollback_enabled="${11}"
    local stop_after_first_block="${12:-0}"

    log "Starting case $case_id [$group]: tol=$local_tol safety=$safety dn_min=$dn_min dn_max=$dn_max recovery=$recovery prediction=$prediction_order control=$control_vars injection=$injection_mode rollback=$rollback_enabled"
    local base_cycle=10
    local block_index=1
    local previous_route=""

    while [[ "$base_cycle" -lt "$FINAL_CYCLE" ]]; do
        if ! walltime_allows_new_case; then
            log "Walltime guard reached during $case_id; summary remains checkpointed through block $((block_index - 1))."
            return 0
        fi

        local base_source="reference"
        local previous_arg=()
        if [[ "$block_index" -gt 1 ]]; then
            base_source="previous_block"
            previous_arg=(--previous-route-csv "$previous_route")
        fi

        local block_tag
        block_tag="${case_id}_block$(printf '%02d' "$block_index")"
        start_task "$case_id block $block_index generation"
        if ! run_logged "${block_tag}_generate_console" \
            python3 "$STAGE14D/make_stage14d_block_job.py" \
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
                --rollback-enabled "$rollback_enabled" \
                "${previous_arg[@]}"; then
            append_failure_summary "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "generation" "block $block_index failed"
            extract_failure_tails "$case_id" "$group" "generation" "$block_index" "" "${block_tag}_generate_console" "generation failed"
            return 1
        fi
        finish_task

        local metadata
        metadata="$(find "$STAGE14D/strategy_${case_id}" -path "*block$(printf '%02d' "$block_index")_*" -name "stage14d_${case_id}_block$(printf '%02d' "$block_index")_metadata.csv" | sort | tail -1)"
        if [[ -z "$metadata" || ! -f "$metadata" ]]; then
            append_failure_summary "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "metadata" "missing metadata for block $block_index"
            extract_failure_tails "$case_id" "$group" "metadata" "$block_index" "" "${block_tag}_generate_console" "missing metadata"
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
            append_failure_summary "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "datacheck" "block $block_index datacheck failed"
            extract_failure_tails "$case_id" "$group" "datacheck" "$block_index" "$metadata" "${job}_datacheck_console" "datacheck failed"
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
            if [[ "$rollback_enabled" == "true" && "$dn_max" -gt 10 ]]; then
                local retry_dn=$(( dn_max / 2 ))
                log "Rollback requested for $case_id block $block_index after analysis failure; retrying with DN_MAX=$retry_dn."
                dn_max="$retry_dn"
                continue
            fi
            append_failure_summary "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "analysis" "block $block_index analysis failed"
            extract_failure_tails "$case_id" "$group" "analysis" "$block_index" "$metadata" "${job}_full_console" "analysis failed"
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
            append_failure_summary "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "postprocess" "block $block_index postprocess failed"
            extract_failure_tails "$case_id" "$group" "postprocess" "$block_index" "$metadata" "${job}_postprocess_console" "postprocess failed"
            return 1
        fi

        start_task "$case_id block $block_index summary update"
        run_logged "${block_tag}_summary_console" \
            python3 "$STAGE14D/stage14d_update_summary.py" \
                --stage-dir "$STAGE14D" \
                --metadata "$metadata"
        rc=$?
        finish_task
        if [[ "$rc" -ne 0 ]]; then
            append_failure_summary "$case_id" "$group" "$local_tol" "$safety" "$dn_min" "$dn_max" "$recovery" "$prediction_order" "$control_vars" "$injection_mode" "$rollback_enabled" "summary" "block $block_index summary update failed"
            extract_failure_tails "$case_id" "$group" "summary" "$block_index" "$metadata" "${block_tag}_summary_console" "summary failed"
            return 1
        fi

        if [[ "$stop_after_first_block" == "1" ]]; then
            log "Debug case $case_id completed one block."
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

init_outputs
log "Starting Stage 14D 24-hour high-density controller sweep."
log "Host: $(hostname)"
log "Repo root: $REPO_ROOT"
log "Stage dir: $STAGE14D"
log "PARALLEL_LANES requested: $PARALLEL_LANES"
log "CPUS_PER_CASE requested: $CPUS_PER_CASE"
if [[ "$PARALLEL_LANES" != "1" ]]; then
    log "Using serialized case execution for lock-safe summary updates; set PARALLEL_LANES=1 explicitly to silence this note."
fi
log "GCC: $(gcc --version | head -1)"
log "Fortran: $(ifort --version | head -1)"
log "Abaqus: $(command -v abaqus)"
write_status

for safety in 0.45 0.50 0.55 0.60; do
    for dnmax in 50 75 100 125 150 175 200 250; do
        case_id="SB_s${safety/./}_d${dnmax}"
        run_sweep_case "$case_id" "SPEED_BOUNDARY" "0.001" "$safety" "1" "$dnmax" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || break 2
    done
done

run_sweep_case "D4F01" "D4_FINE" "0.001" "0.46" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F02" "D4_FINE" "0.001" "0.47" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F03" "D4_FINE" "0.001" "0.48" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F04" "D4_FINE" "0.001" "0.49" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F05" "D4_FINE" "0.001" "0.50" "1" "175" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F06" "D4_FINE" "0.001" "0.50" "1" "200" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F07" "D4_FINE" "0.001" "0.52" "1" "125" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F08" "D4_FINE" "0.001" "0.52" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F09" "D4_FINE" "0.001" "0.54" "1" "100" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "D4F10" "D4_FINE" "0.001" "0.54" "1" "125" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true

run_sweep_case "RW01" "RECOVERY_WINDOW_SHORT" "0.001" "0.60" "1" "15" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW02" "RECOVERY_WINDOW_SHORT" "0.001" "0.60" "1" "20" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW03" "RECOVERY_WINDOW_SHORT" "0.0005" "0.60" "1" "25" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW04" "RECOVERY_WINDOW_SHORT" "0.00025" "0.60" "1" "25" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW05" "RECOVERY_WINDOW_SHORT" "0.001" "0.50" "1" "150" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW06" "RECOVERY_WINDOW_SHORT" "0.001" "0.50" "1" "150" "7" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW07" "RECOVERY_WINDOW_SHORT" "0.001" "0.50" "1" "100" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW08" "RECOVERY_WINDOW_SHORT" "0.001" "0.50" "1" "100" "7" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW09" "RECOVERY_WINDOW_SHORT" "0.001" "0.55" "1" "75" "5" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "RW10" "RECOVERY_WINDOW_SHORT" "0.001" "0.55" "1" "75" "7" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true

run_sweep_case "T01" "TOLERANCE" "0.002" "0.50" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T02" "TOLERANCE" "0.0015" "0.50" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T03" "TOLERANCE" "0.001" "0.50" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T04" "TOLERANCE" "0.00075" "0.50" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T05" "TOLERANCE" "0.0005" "0.50" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T06" "TOLERANCE" "0.002" "0.55" "1" "100" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T07" "TOLERANCE" "0.0015" "0.55" "1" "100" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T08" "TOLERANCE" "0.001" "0.55" "1" "100" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T09" "TOLERANCE" "0.00075" "0.55" "1" "100" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "T10" "TOLERANCE" "0.0005" "0.55" "1" "100" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true

run_sweep_case "SO01" "SECOND_ORDER" "0.001" "0.60" "1" "25" "10" "second_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "SO02" "SECOND_ORDER" "0.001" "0.60" "1" "50" "10" "second_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "SO03" "SECOND_ORDER" "0.001" "0.55" "1" "75" "10" "second_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "SO04" "SECOND_ORDER" "0.001" "0.50" "1" "100" "10" "second_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "SO05" "SECOND_ORDER" "0.001" "0.50" "1" "150" "10" "second_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "SO06" "SECOND_ORDER" "0.001" "0.45" "1" "200" "10" "second_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "0" || true

run_sweep_case "MV01" "MULTIVARIABLE" "0.001" "0.60" "1" "50" "10" "first_order" "STATEV1_plus_S11_RF1" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV02" "MULTIVARIABLE" "0.001" "0.55" "1" "100" "10" "first_order" "STATEV1_plus_S11_RF1" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV03" "MULTIVARIABLE" "0.001" "0.50" "1" "150" "10" "first_order" "STATEV1_plus_S11_RF1" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV04" "MULTIVARIABLE" "0.001" "0.60" "1" "50" "10" "first_order" "active_STATEVs" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV05" "MULTIVARIABLE" "0.001" "0.55" "1" "100" "10" "first_order" "active_STATEVs" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV06" "MULTIVARIABLE" "0.001" "0.50" "1" "150" "10" "first_order" "active_STATEVs" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV07" "MULTIVARIABLE" "0.001" "0.60" "1" "50" "10" "first_order" "active_STATEVs_plus_S11_RF1" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV08" "MULTIVARIABLE" "0.001" "0.55" "1" "100" "10" "first_order" "active_STATEVs_plus_S11_RF1" "full_STATEV_plus_predicted_stress" "false" "0" || true
run_sweep_case "MV09" "MULTIVARIABLE" "0.001" "0.50" "1" "150" "10" "first_order" "active_STATEVs_plus_S11_RF1" "full_STATEV_plus_predicted_stress" "false" "0" || true

run_sweep_case "RB01" "ROLLBACK" "0.001" "0.70" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "true" "0" || true
run_sweep_case "RB02" "ROLLBACK" "0.001" "0.65" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "true" "0" || true
run_sweep_case "RB03" "ROLLBACK" "0.001" "0.60" "1" "200" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "true" "0" || true
run_sweep_case "RB04" "ROLLBACK" "0.001" "0.55" "1" "250" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "true" "0" || true
run_sweep_case "RB05" "ROLLBACK" "0.001" "0.50" "1" "300" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "true" "0" || true

run_sweep_case "DBG01" "DEBUG_RUNTIME_ERRORS" "0.001" "0.70" "1" "150" "25" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "1" || true
run_sweep_case "DBG02" "DEBUG_RUNTIME_ERRORS" "0.001" "0.70" "1" "150" "50" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "1" || true
run_sweep_case "DBG03" "DEBUG_RUNTIME_ERRORS" "0.001" "0.70" "1" "25" "25" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "1" || true
run_sweep_case "DBG04" "DEBUG_RUNTIME_ERRORS" "0.001" "0.70" "1" "50" "25" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "1" || true
run_sweep_case "DBG05" "DEBUG_RUNTIME_ERRORS" "0.00025" "0.70" "1" "150" "10" "first_order" "STATEV1_only" "full_STATEV_plus_predicted_stress" "false" "1" || true

log "Stage 14D 24-hour high-density controller sweep finished queue or reached walltime guard."
write_status
