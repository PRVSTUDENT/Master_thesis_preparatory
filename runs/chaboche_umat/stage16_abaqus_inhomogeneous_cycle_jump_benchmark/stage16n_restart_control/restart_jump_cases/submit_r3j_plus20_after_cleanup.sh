#!/bin/bash
set -euo pipefail

USER_NAME="pr21vyci"
HOME_MAX_USED_PCT=75
SCRATCH_MAX_USED_PCT=90
SLEEP_SECONDS=300

PROJECT_ROOT="$HOME/master_thesis/Abaqus_trial"
STAGE_DIR="$PROJECT_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
JUMP_CASE_DIR="$STAGE_DIR/stage16n_restart_control/restart_jump_cases"

R3J5_DIR="$JUMP_CASE_DIR/R3J5_250_to_270_to_500"
R3J6_DIR="$JUMP_CASE_DIR/R3J6_500_to_520_to_750"
R3J5_PBS="$R3J5_DIR/submit_stage16n_r3j5_jump_250_to_270_to_500.pbs"
R3J6_PBS="$R3J6_DIR/submit_stage16n_r3j6_jump_500_to_520_to_750.pbs"

MARKER="$JUMP_CASE_DIR/.r3j_plus20_auto_submitted"
LOG="$JUMP_CASE_DIR/r3j_plus20_auto_submit_watchdog.log"

mkdir -p "$JUMP_CASE_DIR"

echo "============================================================" | tee -a "$LOG"
echo "R3J +20 auto-submit watchdog started: $(date)" | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"

if [ -f "$MARKER" ]; then
    echo "Marker already exists: $MARKER" | tee -a "$LOG"
    echo "This means the jobs were already submitted once. Exiting." | tee -a "$LOG"
    exit 0
fi

while true; do
    echo "" | tee -a "$LOG"
    echo "Check time: $(date)" | tee -a "$LOG"

    CLEANUP_RUNNING=$(pgrep -u "$USER_NAME" -af "offload_home_outputs.py|offload_r3j_finished_after_current.sh|rsync.*scratch" || true)

    if [ -n "$CLEANUP_RUNNING" ]; then
        echo "Cleanup/offload still running. Waiting..." | tee -a "$LOG"
        echo "$CLEANUP_RUNNING" | tee -a "$LOG"
        sleep "$SLEEP_SECONDS"
        continue
    fi

    echo "Cleanup/offload processes are no longer running." | tee -a "$LOG"

    ACTIVE_JOBS=$(qstat -u "$USER_NAME" 2>/dev/null | awk 'NR>5 && ($5=="R" || $5=="Q") {print $1, $5}' || true)

    if [ -n "$ACTIVE_JOBS" ]; then
        echo "There are still active/queued jobs. Waiting..." | tee -a "$LOG"
        echo "$ACTIVE_JOBS" | tee -a "$LOG"
        sleep "$SLEEP_SECONDS"
        continue
    fi

    echo "No active or queued PBS jobs found for $USER_NAME." | tee -a "$LOG"

    HOME_USED=$(df -P /home | awk 'NR==2 {gsub("%","",$5); print $5}')
    SCRATCH_USED=$(df -P /scratch | awk 'NR==2 {gsub("%","",$5); print $5}')

    echo "/home usage: ${HOME_USED}%" | tee -a "$LOG"
    echo "/scratch usage: ${SCRATCH_USED}%" | tee -a "$LOG"

    if [ "$HOME_USED" -gt "$HOME_MAX_USED_PCT" ]; then
        echo "/home usage is still above ${HOME_MAX_USED_PCT}%. Waiting..." | tee -a "$LOG"
        sleep "$SLEEP_SECONDS"
        continue
    fi

    if [ "$SCRATCH_USED" -gt "$SCRATCH_MAX_USED_PCT" ]; then
        echo "/scratch usage is above ${SCRATCH_MAX_USED_PCT}%. Not submitting." | tee -a "$LOG"
        sleep "$SLEEP_SECONDS"
        continue
    fi

    echo "Checking for remaining heavy Abaqus files in /home..." | tee -a "$LOG"
    HEAVY_FILES=$(find "$PROJECT_ROOT" -type f \( -name "*.odb" -o -name "*.stt" -o -name "*.res" -o -name "*.sim" -o -name "*.mdl" -o -name "*.prt" -o -name "state.bin" -o -name "state.csv" \) -size +10G -print 2>/dev/null || true)

    if [ -n "$HEAVY_FILES" ]; then
        echo "Heavy Abaqus files larger than 10 GB still exist in /home. Waiting..." | tee -a "$LOG"
        echo "$HEAVY_FILES" | tee -a "$LOG"
        sleep "$SLEEP_SECONDS"
        continue
    fi

    echo "No heavy Abaqus files larger than 10 GB found in /home project tree." | tee -a "$LOG"

    if [ ! -f "$R3J5_PBS" ]; then
        echo "ERROR: R3J5 PBS script not found:" | tee -a "$LOG"
        echo "$R3J5_PBS" | tee -a "$LOG"
        exit 1
    fi

    if [ ! -f "$R3J6_PBS" ]; then
        echo "ERROR: R3J6 PBS script not found:" | tee -a "$LOG"
        echo "$R3J6_PBS" | tee -a "$LOG"
        exit 1
    fi

    echo "All checks passed. Submitting R3J +20 jobs..." | tee -a "$LOG"

    JOB1=$(qsub "$R3J5_PBS")
    sleep 2
    JOB2=$(qsub "$R3J6_PBS")

    echo "Submitted R3J5: $JOB1" | tee -a "$LOG"
    echo "Submitted R3J6: $JOB2" | tee -a "$LOG"

    {
        echo "R3J +20 jobs auto-submitted after cleanup."
        echo "Date: $(date)"
        echo "R3J5 job: $JOB1"
        echo "R3J6 job: $JOB2"
        echo "/home usage at submit: ${HOME_USED}%"
        echo "/scratch usage at submit: ${SCRATCH_USED}%"
    } > "$MARKER"

    echo "Marker written: $MARKER" | tee -a "$LOG"
    echo "Auto-submit complete." | tee -a "$LOG"

    exit 0
done
