#!/bin/bash
set -euo pipefail

# Wait for /home cleanup, stage a lightweight repo-shaped tree into /scratch,
# submit two Abaqus restart-jump cases from /scratch, and copy back only
# lightweight evidence.

USER_NAME="${USER:-pr21vyci}"

HOME_MAX_USED_PCT=75
SCRATCH_MAX_USED_PCT=90
SLEEP_SECONDS=300

PROJECT_ROOT="$HOME/master_thesis/Abaqus_trial"
STAGE_REL="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
STAGE_DIR="$PROJECT_ROOT/$STAGE_REL"
CASE_ROOT_REL="$STAGE_REL/stage16n_restart_control/restart_jump_cases"
CASE_ROOT_HOME="$PROJECT_ROOT/$CASE_ROOT_REL"

CASE1_NAME="R4J1_250_to_300_solve_301_to_500"
CASE2_NAME="R4J2_500_to_550_solve_551_to_750"

SCRATCH_ROOT="/scratch/$USER_NAME/stage16n_scratch_runs"
SCRATCH_REPO="$SCRATCH_ROOT/Abaqus_trial"

MARKER="$CASE_ROOT_HOME/.scratch_auto_submit_${CASE1_NAME}_${CASE2_NAME}.done"
LOG="$CASE_ROOT_HOME/scratch_auto_submit_${CASE1_NAME}_${CASE2_NAME}.log"

log() {
    echo "$@" | tee -a "$LOG" >&2
}

log "============================================================"
log "Scratch auto-submit watchdog started: $(date)"
log "CASE1 = $CASE1_NAME"
log "CASE2 = $CASE2_NAME"
log "SCRATCH_REPO = $SCRATCH_REPO"
log "============================================================"

if [ -f "$MARKER" ]; then
    log "Marker already exists: $MARKER"
    log "These jobs were already auto-submitted. Exiting."
    exit 0
fi

wait_for_cleanup() {
    while true; do
        log ""
        log "Cleanup check: $(date)"

        CLEANUP_RUNNING=$(pgrep -u "$USER_NAME" -af "offload_home_outputs.py|offload_r3j_finished_after_current.sh|offload_r3j5_r3j6_stt.py|rsync.*scratch|cp .*scratch|mv .*scratch" || true)

        if [ -n "$CLEANUP_RUNNING" ]; then
            log "Cleanup/offload still running. Waiting..."
            log "$CLEANUP_RUNNING"
            sleep "$SLEEP_SECONDS"
            continue
        fi

        HOME_USED=$(df -P /home | awk 'NR==2 {gsub("%","",$5); print $5}')
        SCRATCH_USED=$(df -P /scratch | awk 'NR==2 {gsub("%","",$5); print $5}')

        log "/home usage    = ${HOME_USED}%"
        log "/scratch usage = ${SCRATCH_USED}%"

        if [ "$HOME_USED" -gt "$HOME_MAX_USED_PCT" ]; then
            log "/home still above ${HOME_MAX_USED_PCT}%. Waiting..."
            sleep "$SLEEP_SECONDS"
            continue
        fi

        if [ "$SCRATCH_USED" -gt "$SCRATCH_MAX_USED_PCT" ]; then
            log "/scratch above ${SCRATCH_MAX_USED_PCT}%. Waiting..."
            sleep "$SLEEP_SECONDS"
            continue
        fi

        ACTIVE_JOBS=$(qstat -u "$USER_NAME" 2>/dev/null | awk 'NR>5 {print $1, $5}' | grep -E " R$| Q$| H$| E$" || true)

        if [ -n "$ACTIVE_JOBS" ]; then
            log "Active/queued PBS jobs found. Waiting..."
            log "$ACTIVE_JOBS"
            sleep "$SLEEP_SECONDS"
            continue
        fi

        log "No cleanup process, storage limits OK, and no active jobs."
        break
    done
}

check_home_heavy_files() {
    log "Checking for remaining heavy Abaqus files in /home project tree..."

    HEAVY_FILES=$(find "$PROJECT_ROOT" -type f \( \
        -name "*.odb" -o -name "*.stt" -o -name "*.res" -o -name "*.sim" -o \
        -name "*.mdl" -o -name "*.prt" -o -name "state.bin" -o -name "state.csv" \
        \) -size +10G -print 2>/dev/null || true)

    if [ -n "$HEAVY_FILES" ]; then
        log "ERROR: heavy Abaqus files larger than 10 GB still exist in /home:"
        log "$HEAVY_FILES"
        log "Not submitting. Move these to /scratch first."
        exit 1
    fi

    log "No >10 GB Abaqus heavy files found in /home project tree."
}

stage_repo_to_scratch() {
    log ""
    log "Staging lightweight repository tree to scratch..."
    log "PROJECT_ROOT = $PROJECT_ROOT"
    log "SCRATCH_REPO = $SCRATCH_REPO"

    mkdir -p "$SCRATCH_REPO"

    rsync -a --delete \
        --exclude=".git/" \
        --exclude="*.odb" \
        --exclude="*.stt" \
        --exclude="*.res" \
        --exclude="*.sim" \
        --exclude="*.mdl" \
        --exclude="*.prt" \
        --exclude="*.lck" \
        --exclude="*.pac" \
        --exclude="*.abq" \
        --exclude="*.sel" \
        --exclude="*.jnl" \
        "$PROJECT_ROOT"/ "$SCRATCH_REPO"/
}

find_case_runner() {
    local SCRATCH_CASE="$1"
    local RUNNER
    RUNNER=$(find "$SCRATCH_CASE" -maxdepth 1 -type f \( \
        -name "run*.sh" -o -name "*runner*.sh" -o -name "*execute*.sh" \
        \) | head -n 1 || true)

    if [ -z "$RUNNER" ]; then
        log "ERROR: no run script found in $SCRATCH_CASE"
        exit 1
    fi

    chmod +x "$RUNNER"
    echo "$RUNNER"
}

write_scratch_pbs() {
    local CASE_NAME="$1"
    local SCRATCH_CASE="$2"
    local HOME_CASE="$CASE_ROOT_HOME/$CASE_NAME"
    local RUNNER="$3"

    local PBS_FILE="$SCRATCH_CASE/submit_${CASE_NAME}_scratch.pbs"
    local RUNNER_BASE
    RUNNER_BASE=$(basename "$RUNNER")

    cat > "$PBS_FILE" <<EOF
#!/bin/bash
#PBS -N ${CASE_NAME}
#PBS -l select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
#PBS -l walltime=24:00:00
#PBS -j oe
#PBS -S /bin/bash
#PBS -o ${SCRATCH_CASE}/${CASE_NAME}.pbs.out

set -uo pipefail

echo "============================================================"
echo "PBS job started: \$(date)"
echo "Case: ${CASE_NAME}"
echo "Running in scratch case:"
echo "${SCRATCH_CASE}"
echo "============================================================"

cd "${SCRATCH_CASE}"

export REPO_ROOT="${SCRATCH_REPO}"
export TMPDIR="${SCRATCH_CASE}/tmp"
mkdir -p "\$TMPDIR"

echo "Disk usage before Abaqus:"
df -h /home /scratch || true

if [ -x ./link_restart_sources.sh ]; then
  echo "Linking native restart sources in scratch..."
  bash ./link_restart_sources.sh
fi

echo "Running case runner from scratch:"
echo "./${RUNNER_BASE}"
bash "./${RUNNER_BASE}"
RUN_RC=\$?

echo "Case runner return code: \$RUN_RC"

echo "Staging lightweight evidence back to /home..."
mkdir -p "${HOME_CASE}"

rsync -av \
  --include="*/" \
  --include="*.sta" \
  --include="*.log" \
  --include="*.txt" \
  --include="*.csv" \
  --include="*.md" \
  --include="*.out" \
  --include="*.o[0-9]*" \
  --include="_logs/***" \
  --exclude="*.odb" \
  --exclude="*.stt" \
  --exclude="*.res" \
  --exclude="*.sim" \
  --exclude="*.mdl" \
  --exclude="*.prt" \
  --exclude="state.bin" \
  --exclude="state.csv" \
  --exclude="*" \
  "${SCRATCH_CASE}/" "${HOME_CASE}/"

echo "Disk usage after run:"
df -h /home /scratch || true

echo "PBS job finished: \$(date)"
exit "\$RUN_RC"
EOF

    chmod +x "$PBS_FILE"
    echo "$PBS_FILE"
}

submit_case() {
    local CASE_NAME="$1"
    local SCRATCH_CASE="$SCRATCH_REPO/$CASE_ROOT_REL/$CASE_NAME"
    local HOME_CASE="$CASE_ROOT_HOME/$CASE_NAME"

    if [ ! -d "$HOME_CASE" ]; then
        log "ERROR: home case directory missing: $HOME_CASE"
        exit 1
    fi
    if [ ! -d "$SCRATCH_CASE" ]; then
        log "ERROR: scratch case directory missing after staging: $SCRATCH_CASE"
        exit 1
    fi

    local RUNNER
    RUNNER=$(find_case_runner "$SCRATCH_CASE")

    local PBS_FILE
    PBS_FILE=$(write_scratch_pbs "$CASE_NAME" "$SCRATCH_CASE" "$RUNNER")

    log "Submitting $CASE_NAME using PBS file: $PBS_FILE"
    qsub "$PBS_FILE"
}

wait_for_cleanup
check_home_heavy_files
stage_repo_to_scratch

log ""
log "Submitting two scratch-based Abaqus jobs..."

JOB1=$(submit_case "$CASE1_NAME")
sleep 2
JOB2=$(submit_case "$CASE2_NAME")

log "Submitted CASE1 $CASE1_NAME: $JOB1"
log "Submitted CASE2 $CASE2_NAME: $JOB2"

{
    echo "Scratch auto-submit completed."
    echo "Date: $(date)"
    echo "CASE1=$CASE1_NAME"
    echo "JOB1=$JOB1"
    echo "CASE2=$CASE2_NAME"
    echo "JOB2=$JOB2"
    echo "SCRATCH_REPO=$SCRATCH_REPO"
} > "$MARKER"

log "Marker written: $MARKER"
log "Done."
