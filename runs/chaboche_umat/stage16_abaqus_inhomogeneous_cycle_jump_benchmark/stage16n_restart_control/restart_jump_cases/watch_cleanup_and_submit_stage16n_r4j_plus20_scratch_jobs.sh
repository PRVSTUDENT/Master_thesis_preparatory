#!/bin/bash
set -euo pipefail

# Stage and submit a two-case R4J true-skip refinement pair from scratch.
# Defaults are the original +20 pair; override CASE1_NAME, CASE2_NAME,
# and SCRATCH_ROOT for later branch-specific refinement pairs.
# Submit PBS wrappers from /home, but run Abaqus in /scratch.

USER_NAME="${USER:-pr21vyci}"

HOME_MAX_USED_PCT=75
SCRATCH_MAX_USED_PCT=90
SLEEP_SECONDS=300

PROJECT_ROOT="$HOME/master_thesis/Abaqus_trial"
STAGE_REL="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
STAGE_DIR="$PROJECT_ROOT/$STAGE_REL"
CASE_ROOT_REL="$STAGE_REL/stage16n_restart_control/restart_jump_cases"
CASE_ROOT_HOME="$PROJECT_ROOT/$CASE_ROOT_REL"

CASE1_NAME="${CASE1_NAME:-R4J3_250_to_270_solve_271_to_500}"
CASE2_NAME="${CASE2_NAME:-R4J4_500_to_520_solve_521_to_750}"

SCRATCH_ROOT="${SCRATCH_ROOT:-/scratch/$USER_NAME/stage16n_scratch_runs_r4j_plus20}"
SCRATCH_REPO="$SCRATCH_ROOT/Abaqus_trial"

MARKER="$CASE_ROOT_HOME/.scratch_auto_submit_${CASE1_NAME}_${CASE2_NAME}.done"
LOG="$CASE_ROOT_HOME/scratch_auto_submit_${CASE1_NAME}_${CASE2_NAME}.log"

log() {
    echo "$@" | tee -a "$LOG" >&2
}

wait_for_cleanup() {
    while true; do
        log "============================================================"
        log "Scratch auto-submit watchdog check: $(date)"

        local ACTIVE_JOBS
        ACTIVE_JOBS=$(qstat -u "$USER_NAME" 2>/dev/null | awk -v user="$USER_NAME" '$0 ~ user {print}' || true)
        if [ -n "$ACTIVE_JOBS" ]; then
            log "PBS jobs are active. Waiting..."
            log "$ACTIVE_JOBS"
            sleep "$SLEEP_SECONDS"
            continue
        fi

        local CLEANUP_RUNNING
        CLEANUP_RUNNING=$(pgrep -u "$USER_NAME" -af "offload_home_outputs.py|offload_r3j_finished_after_current.sh|offload_r3j5_r3j6_stt.py|rsync.*scratch|cp .*scratch|mv .*scratch" || true)
        if [ -n "$CLEANUP_RUNNING" ]; then
            log "Cleanup/offload process still running. Waiting..."
            log "$CLEANUP_RUNNING"
            sleep "$SLEEP_SECONDS"
            continue
        fi

        local HOME_USED SCRATCH_USED
        HOME_USED=$(df -P /home | awk 'NR==2 {gsub("%","",$5); print $5}')
        SCRATCH_USED=$(df -P /scratch | awk 'NR==2 {gsub("%","",$5); print $5}')
        log "/home usage = ${HOME_USED}%"
        log "/scratch usage = ${SCRATCH_USED}%"

        if [ "$HOME_USED" -gt "$HOME_MAX_USED_PCT" ]; then
            log "/home above ${HOME_MAX_USED_PCT}%. Waiting..."
            sleep "$SLEEP_SECONDS"
            continue
        fi

        if [ "$SCRATCH_USED" -gt "$SCRATCH_MAX_USED_PCT" ]; then
            log "/scratch above ${SCRATCH_MAX_USED_PCT}%. Waiting..."
            sleep "$SLEEP_SECONDS"
            continue
        fi

        break
    done
}

check_home_heavy_files() {
    log "Checking for Abaqus heavy files >10G in /home project tree..."
    local HEAVY
    HEAVY=$(find "$PROJECT_ROOT" -type f \( \
        -name "*.odb" -o -name "*.stt" -o -name "*.res" -o -name "*.sim" -o \
        -name "*.mdl" -o -name "*.prt" -o -name "state.bin" -o -name "state.csv" \
        \) -size +10G -print)

    if [ -n "$HEAVY" ]; then
        log "ERROR: heavy Abaqus files remain in /home:"
        log "$HEAVY"
        exit 1
    fi
}

stage_repo_to_scratch() {
    log "Staging minimal repository tree to scratch..."
    log "SCRATCH_REPO = $SCRATCH_REPO"

    rm -rf "$SCRATCH_REPO/$CASE_ROOT_REL/$CASE1_NAME"
    rm -rf "$SCRATCH_REPO/$CASE_ROOT_REL/$CASE2_NAME"
    mkdir -p "$SCRATCH_REPO/$STAGE_REL"
    mkdir -p "$SCRATCH_REPO/$CASE_ROOT_REL"

    rsync -a \
        "$STAGE_DIR/stage16n_extract_exact_state_for_reinjection.py" \
        "$STAGE_DIR/stage16n_make_extrapolated_state.py" \
        "$STAGE_DIR/stage16n_extract_hysteresis_and_local_states.py" \
        "$STAGE_DIR/stage16n_compare_r3j_jump_against_reference.py" \
        "$SCRATCH_REPO/$STAGE_REL/"

    mkdir -p "$SCRATCH_REPO/$STAGE_REL/stage16n_1000cycle_pilot"
    rsync -a \
        "$STAGE_DIR/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv" \
        "$STAGE_DIR/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv" \
        "$SCRATCH_REPO/$STAGE_REL/stage16n_1000cycle_pilot/"

    mkdir -p "$SCRATCH_REPO/$STAGE_REL/stage16n_parallel_max_reference"
    rsync -a \
        "$STAGE_DIR/stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv" \
        "$STAGE_DIR/stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv" \
        "$SCRATCH_REPO/$STAGE_REL/stage16n_parallel_max_reference/"

    rsync -a --delete "$CASE_ROOT_HOME/$CASE1_NAME/" "$SCRATCH_REPO/$CASE_ROOT_REL/$CASE1_NAME/"
    rsync -a --delete "$CASE_ROOT_HOME/$CASE2_NAME/" "$SCRATCH_REPO/$CASE_ROOT_REL/$CASE2_NAME/"
    rsync -a "$CASE_ROOT_HOME/stage16n_r3j_jump_cases.csv" "$SCRATCH_REPO/$CASE_ROOT_REL/"

    local HOME_R1A="$STAGE_DIR/stage16n_restart_control/R1A_restart_reference_500cycles"
    local SCRATCH_R1A="$SCRATCH_REPO/$STAGE_REL/stage16n_restart_control/R1A_restart_reference_500cycles"
    mkdir -p "$SCRATCH_R1A"
    for ext in odb res stt mdl sim prt; do
        ln -sfn "$HOME_R1A/stage16n_r1a_restart_ref_500cycles.$ext" \
            "$SCRATCH_R1A/stage16n_r1a_restart_ref_500cycles.$ext"
    done
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
    echo "$RUNNER"
}

write_scratch_pbs() {
    local CASE_NAME="$1"
    local SCRATCH_CASE="$2"
    local HOME_CASE="$CASE_ROOT_HOME/$CASE_NAME"
    local RUNNER="$3"
    local RUNNER_BASE
    RUNNER_BASE=$(basename "$RUNNER")
    local PBS_FILE="$HOME_CASE/submit_${CASE_NAME}_scratch.pbs"

    cat > "$PBS_FILE" <<EOF
#!/bin/bash
#PBS -N ${CASE_NAME}
#PBS -q entry_teachingq
#PBS -l select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
#PBS -l walltime=24:00:00
#PBS -j oe
#PBS -S /bin/bash
#PBS -o ${HOME_CASE}/${CASE_NAME}.pbs.out
#PBS -m abe
#PBS -M ${USER_NAME}@mailserver.tu-freiberg.de

set -uo pipefail

echo "PBS job started: \$(date)"
echo "Case: ${CASE_NAME}"
echo "Scratch case: ${SCRATCH_CASE}"
cd "${SCRATCH_CASE}"

export REPO_ROOT="${SCRATCH_REPO}"
export TMPDIR="${SCRATCH_CASE}/tmp"
mkdir -p "\$TMPDIR"

df -h /home /scratch || true

if [ -x ./link_restart_sources.sh ]; then
  bash ./link_restart_sources.sh
fi

bash "./${RUNNER_BASE}"
RUN_RC=\$?

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

    local RUNNER PBS_FILE
    RUNNER=$(find_case_runner "$SCRATCH_CASE")
    PBS_FILE=$(write_scratch_pbs "$CASE_NAME" "$SCRATCH_CASE" "$RUNNER")
    log "Submitting $CASE_NAME using PBS file: $PBS_FILE"
    qsub "$PBS_FILE"
}

log "Scratch auto-submit watchdog started: $(date)"
log "CASE1 = $CASE1_NAME"
log "CASE2 = $CASE2_NAME"

wait_for_cleanup
check_home_heavy_files
stage_repo_to_scratch

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
