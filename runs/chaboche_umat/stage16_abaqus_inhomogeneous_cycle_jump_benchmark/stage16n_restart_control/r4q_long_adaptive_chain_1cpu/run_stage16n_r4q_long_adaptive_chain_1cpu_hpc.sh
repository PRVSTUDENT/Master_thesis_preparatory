#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="R4Q_long_adaptive_chain_1cpu"
SOURCE_CYCLE_START=250
SAFE_JUMP=21
BLOCK_SIZE=250
CHECKPOINTS="1000 2000 5000"
WALLTIME_SECONDS="${WALLTIME_SECONDS:-86400}"
WALLTIME_STOP_MARGIN_SECONDS="${WALLTIME_STOP_MARGIN_SECONDS:-3600}"
SCRATCH9_USER_LIMIT_TB="${SCRATCH9_USER_LIMIT_TB:-5}"
START_EPOCH="$(date +%s)"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH" "_source_state"

exec > >(tee -a R4Q_LONG_CHAIN_CONTROLLER.log) 2>&1

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

elapsed_seconds() {
  echo $(( $(date +%s) - START_EPOCH ))
}

remaining_seconds() {
  echo $(( WALLTIME_SECONDS - $(elapsed_seconds) ))
}

walltime_low() {
  [[ "$(remaining_seconds)" -lt "$WALLTIME_STOP_MARGIN_SECONDS" ]]
}

write_status() {
  local status="$1"
  local phase="$2"
  local detail="$3"
  {
    echo "status=$status"
    echo "phase=$phase"
    echo "detail=$detail"
    echo "controller=$CONTROLLER"
    echo "pbs_job_id=${PBS_JOBID:-manual}"
    echo "source_cycle_start=$SOURCE_CYCLE_START"
    echo "safe_jump=$SAFE_JUMP"
    echo "block_size=$BLOCK_SIZE"
    echo "checkpoints=$CHECKPOINTS"
    echo "abaqus_cpus=${ABAQUS_CPUS:-1}"
    echo "classification_scope=restart-chain feasibility unless matching reference CSV exists"
    echo "scratch_case_dir=${SCRATCH_CASE_DIR:-$PWD}"
    echo "elapsed_seconds=$(elapsed_seconds)"
    echo "remaining_seconds=$(remaining_seconds)"
    echo "updated_at=$(date '+%Y-%m-%d %H:%M:%S')"
  } > R4Q_LONG_CHAIN_STATUS.txt
}

init_summary() {
  if [[ ! -f R4Q_LONG_CHAIN_BLOCK_SUMMARY.csv ]]; then
    echo "block_index,source_cycle,jump_target,solved_start,block_end,checkpoint,status,classification_scope,reference_available,comparison_status,job,oldjob,elapsed_seconds,detail" > R4Q_LONG_CHAIN_BLOCK_SUMMARY.csv
  fi
}

append_summary() {
  local block_index="$1"
  local source_cycle="$2"
  local jump_target="$3"
  local solved_start="$4"
  local block_end="$5"
  local checkpoint="$6"
  local status="$7"
  local scope="$8"
  local ref_available="$9"
  local comparison_status="${10}"
  local job="${11}"
  local oldjob="${12}"
  local detail="${13}"
  echo "$block_index,$source_cycle,$jump_target,$solved_start,$block_end,$checkpoint,$status,$scope,$ref_available,$comparison_status,$job,$oldjob,$(elapsed_seconds),\"$detail\"" >> R4Q_LONG_CHAIN_BLOCK_SUMMARY.csv
}

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${HOME_CASE_DIR:-}" ]]; then
    if [[ -n "${SCRATCH_BASE:-}" && -s "$SCRATCH_BASE/r4q_long_chain.pbs.out" ]]; then
      cp "$SCRATCH_BASE/r4q_long_chain.pbs.out" "$PWD/r4q_long_chain.pbs.out" || true
    fi
    rsync -av \
      --include='*/' \
      --exclude='state.bin' \
      --exclude='state.csv' \
      --include='*.md' \
      --include='*.csv' \
      --include='*.txt' \
      --include='*.log' \
      --include='*.out' \
      --include='*.pbs.out' \
      --exclude='*.odb' --exclude='*.stt' --exclude='*.res' --exclude='*.sim' \
      --exclude='*.mdl' --exclude='*.prt' --exclude='*.dat' --exclude='*.msg' \
      --exclude='*.sta' --exclude='*.023' --exclude='*.cax' --exclude='*.abq' \
      --exclude='*.pac' --exclude='*.sel' --exclude='*.lck' \
      --exclude='*' \
      "$PWD/" "$HOME_CASE_DIR/"
  fi
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

cleanup_job_heavy() {
  local job="$1"
  find . -maxdepth 1 -type f \( \
    -name "${job}*.odb" -o -name "${job}*.stt" -o -name "${job}*.res" -o \
    -name "${job}*.sim" -o -name "${job}*.mdl" -o -name "${job}*.prt" -o \
    -name "${job}*.dat" -o -name "${job}*.msg" -o -name "${job}*.sta" -o \
    -name "${job}*.023" -o -name "${job}*.cax" -o -name "${job}*.abq" -o \
    -name "${job}*.pac" -o -name "${job}*.sel" -o -name "${job}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
}

cleanup_previous_source_heavy() {
  local previous_source="$1"
  local current_source="$2"
  if [[ "$previous_source" != "$current_source" ]]; then
    cleanup_job_heavy "$previous_source"
  fi
}

scratch9_user_tb() {
  local raw
  raw="$(du -sB1 /scratch9/"$USER" 2>/dev/null | awk '{print $1}' || true)"
  [[ -n "$raw" ]] || return 1
  awk -v b="$raw" 'BEGIN {printf "%.3f", b/1000000000000.0}'
}

enforce_storage_gate() {
  qstat -u "$USER" | tee "$LOG_DIR/R4Q_storage_qstat_before.txt" || true
  df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/R4Q_storage_df_before.txt" || df -h /scratch /home | tee "$LOG_DIR/R4Q_storage_df_before.txt" || true
  du -sh /scratch9/"$USER" 2>/dev/null | tee "$LOG_DIR/R4Q_storage_scratch9_user_before.txt" || true
  du -h --max-depth=2 /scratch9/"$USER" 2>/dev/null | sort -hr | head -80 > "$LOG_DIR/R4Q_storage_scratch9_top80_before.txt" || true
  local tb
  tb="$(scratch9_user_tb || true)"
  if [[ -n "$tb" ]] && awk -v used="$tb" -v limit="$SCRATCH9_USER_LIMIT_TB" 'BEGIN {exit used > limit ? 0 : 1}'; then
    write_status "storage_gate_blocked" "preflight" "/scratch9/$USER ${tb}T exceeds ${SCRATCH9_USER_LIMIT_TB}T"
    copy_lightweight_evidence
    exit 0
  fi
}

find_restart_inc() {
  local sta="$1"
  local step="$2"
  awk -v step="$step" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "$sta"
}

checkpoint_for() {
  local block_end="$1"
  local cp
  for cp in 1000 2000 5000; do
    if [[ "$block_end" -le "$cp" ]]; then
      echo "$cp"
      return 0
    fi
  done
  echo "5000"
}

reference_available_for() {
  local cycle="$1"
  [[ -s "reference_${cycle}_cycle_metrics.csv" && -s "reference_${cycle}_selected_cycle_local_states.csv" ]]
}

copy_1000_reference_aliases() {
  if [[ -s reference_1000_cycle_metrics.csv && -s reference_1000_selected_cycle_local_states.csv ]]; then
    return 0
  fi
  if [[ -s stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv ]]; then
    cp stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv reference_1000_cycle_metrics.csv
  fi
  if [[ -s stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv ]]; then
    cp stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv reference_1000_selected_cycle_local_states.csv
  fi
}

extract_state_cycle() {
  local job="$1"
  local cycle="$2"
  if [[ -s "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$cycle").csv" ]]; then
    return 0
  fi
  run_logged_phase "extract source state cycle ${cycle} from ${job}" "$LOG_DIR/${job}_extract_state_${cycle}.log" \
    abaqus python stage16n_extract_exact_state_for_reinjection.py \
      --odb "${job}.odb" \
      --cycles "$cycle" \
      --outdir _source_state
}

prepare_jump_state() {
  local previous_cycle="$1"
  local source_cycle="$2"
  local jump_target="$3"
  local jump_cycles=$((jump_target - source_cycle))
  rm -f state.bin state.csv
  python3 stage16n_make_extrapolated_state.py \
    --previous-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$previous_cycle").csv" \
    --base-csv "_source_state/stage16n_exact_state_cycle$(printf '%04d' "$source_cycle").csv" \
    --previous-cycle "$previous_cycle" \
    --base-cycle "$source_cycle" \
    --jump-cycles "$jump_cycles" \
    --output-cycle "$jump_target" \
    --output-csv state.csv \
    --output-bin state.bin \
    --output-summary "R4Q_SOURCE${source_cycle}_TARGET${jump_target}_EXTRAPOLATED_STATE.md"
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

run_source_250() {
  local source_job="stage16n_r1b_restart_ref_250cycles"
  if ! run_logged_phase "initial source datacheck" "$LOG_DIR/${source_job}_datacheck.log" \
    abaqus job="${source_job}_datacheck" input="${source_job}.inp" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
    write_tails "$source_job"
    write_status "source_datacheck_failure" "source250_datacheck" "initial source package was not generated"
    copy_lightweight_evidence
    exit 0
  fi
  if ! run_logged_phase "initial source solve" "$LOG_DIR/${source_job}.log" \
    abaqus job="$source_job" input="${source_job}.inp" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
    write_tails "$source_job"
    write_status "source_solve_failure" "source250_solve" "initial source package incomplete"
    copy_lightweight_evidence
    exit 0
  fi
  write_tails "$source_job"
  for ext in odb stt res mdl prt sim sta; do
    test -s "${source_job}.${ext}"
  done
  extract_state_cycle "$source_job" 100
  extract_state_cycle "$source_job" 250
}

run_block() {
  local block_index="$1"
  local previous_cycle="$2"
  local source_cycle="$3"
  local oldjob="$4"
  local block_end=$((source_cycle + BLOCK_SIZE))
  local jump_target=$((source_cycle + SAFE_JUMP))
  local solved_start=$((jump_target + 1))
  local checkpoint
  checkpoint="$(checkpoint_for "$block_end")"
  local job="stage16n_r4q_block$(printf '%02d' "$block_index")_${source_cycle}_to_${jump_target}_solve_${solved_start}_to_${block_end}"
  local inp="${job}.inp"
  local restart_inc
  restart_inc="$(find_restart_inc "${oldjob}.sta" "$source_cycle")"

  write_status "running" "block_${block_index}_prepare" "source=$source_cycle target=$jump_target end=$block_end"
  prepare_jump_state "$previous_cycle" "$source_cycle" "$jump_target"
  python3 stage16n_make_r4q_restart_deck.py \
    --output "$inp" \
    --old-step "$source_cycle" \
    --old-inc "$restart_inc" \
    --solved-start "$solved_start" \
    --block-end "$block_end" \
    --title "Stage 16N-R4Q block ${block_index}: ${source_cycle} to ${jump_target}, solve ${solved_start} to ${block_end}"

  export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
  export STAGE16N_JUMP_TARGET_STEP="$((source_cycle + 1))"
  export STAGE16N_JUMP_CHECK_TIME="$source_cycle"

  if ! run_logged_phase "block ${block_index} datacheck" "$LOG_DIR/${job}_datacheck.log" \
    abaqus job="${job}_datacheck" input="$inp" oldjob="$oldjob" \
      user=stage16n_r3_jump_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
    write_tails "$job"
    append_summary "$block_index" "$source_cycle" "$jump_target" "$solved_start" "$block_end" "$checkpoint" "datacheck_failure" "feasibility" "unknown" "not_run" "$job" "$oldjob" "datacheck failed"
    write_status "datacheck_failure" "block_${block_index}_datacheck" "source=$source_cycle target=$jump_target"
    copy_lightweight_evidence
    return 20
  fi

  if ! run_logged_phase "block ${block_index} solve" "$LOG_DIR/${job}.log" \
    abaqus job="$job" input="$inp" oldjob="$oldjob" \
      user=stage16n_r3_jump_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="${ABAQUS_CPUS:-1}" mp_mode="${ABAQUS_MP_MODE:-threads}"; then
    write_tails "$job"
    append_summary "$block_index" "$source_cycle" "$jump_target" "$solved_start" "$block_end" "$checkpoint" "solve_failure" "feasibility" "unknown" "not_run" "$job" "$oldjob" "solve failed"
    write_status "solve_failure" "block_${block_index}_solve" "source=$source_cycle target=$jump_target"
    copy_lightweight_evidence
    return 21
  fi

  write_tails "$job"
  if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${job}.sta"; then
    append_summary "$block_index" "$source_cycle" "$jump_target" "$solved_start" "$block_end" "$checkpoint" "sta_not_successful" "feasibility" "unknown" "not_run" "$job" "$oldjob" "sta lacks successful completion line"
    write_status "sta_not_successful" "block_${block_index}_sta_check" "$job"
    copy_lightweight_evidence
    return 22
  fi

  grep "STAGE16N_R3J_OVERWRITE" "${job}.dat" > "$LOG_DIR/${job}_overwrite_trace.txt" || true
  grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${job}.msg" > "$LOG_DIR/${job}_parallelism_check.log" || true

  local extraction_status="not_run"
  if run_logged_phase "block ${block_index} ODB extraction" "$LOG_DIR/${job}_extract.log" \
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$job"; then
    extraction_status="ok"
  else
    extraction_status="failed"
  fi

  if ! extract_state_cycle "$job" "$block_end"; then
    extraction_status="state_extract_failed"
    append_summary "$block_index" "$source_cycle" "$jump_target" "$solved_start" "$block_end" "$checkpoint" "state_extract_failed" "feasibility" "unknown" "not_run" "$job" "$oldjob" "cannot prepare next block source state"
    write_status "state_extract_failed" "block_${block_index}_state_extract" "$job cycle $block_end"
    copy_lightweight_evidence
    return 23
  fi
  local ref_available="no"
  local comparison_status="not_available"
  local scope="feasibility"
  if reference_available_for "$block_end"; then
    ref_available="yes"
    scope="accuracy_validation"
    comparison_status="$(run_comparison_if_available "$job" "$block_end")"
  fi

  append_summary "$block_index" "$source_cycle" "$jump_target" "$solved_start" "$block_end" "$checkpoint" "completed" "$scope" "$ref_available" "$comparison_status" "$job" "$oldjob" "extraction=$extraction_status"
  write_status "completed_block_${block_index}" "block_${block_index}_complete" "block_end=$block_end checkpoint=$checkpoint scope=$scope comparison=$comparison_status"
  copy_lightweight_evidence
  cleanup_previous_source_heavy "$oldjob" "$job"
  rm -f state.bin state.csv
  copy_lightweight_evidence

  if [[ "$comparison_status" != "not_available" && "$comparison_status" != "pass" ]]; then
    write_status "comparison_stop" "block_${block_index}_comparison" "comparison_status=$comparison_status at cycle $block_end"
    return 30
  fi
  return 0
}

on_error() {
  local rc=$?
  write_status "controller_failure" "trap" "exit code $rc"
  copy_lightweight_evidence
  exit 0
}
trap on_error ERR
trap copy_lightweight_evidence EXIT

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4Q] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4Q] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4Q] scratch: ${SCRATCH_CASE_DIR:-$PWD}"
echo "[Stage16N-R4Q] cpus=${ABAQUS_CPUS:-1} mp_mode=${ABAQUS_MP_MODE:-threads}"
init_summary
copy_1000_reference_aliases
enforce_storage_gate
write_status "starting" "preflight" "storage gate passed"

for required in \
  stage16n_r1b_restart_ref_250cycles.inp \
  stage16n_neml_equivalent_chaboche_umat.for \
  stage16n_r3_jump_umat.for \
  stage16n_extract_hysteresis_and_local_states.py \
  stage16n_extract_exact_state_for_reinjection.py \
  stage16n_make_extrapolated_state.py \
  stage16n_make_r4q_restart_deck.py; do
  test -s "$required"
done

run_source_250
copy_lightweight_evidence

block_index=1
previous_cycle=100
source_cycle=250
oldjob="stage16n_r1b_restart_ref_250cycles"

while [[ "$source_cycle" -lt 5000 ]]; do
  if walltime_low; then
    write_status "walltime_safe_stop" "pre_block_${block_index}" "remaining_seconds=$(remaining_seconds)"
    copy_lightweight_evidence
    break
  fi
  if ! run_block "$block_index" "$previous_cycle" "$source_cycle" "$oldjob"; then
    copy_lightweight_evidence
    break
  fi
  previous_cycle="$source_cycle"
  source_cycle=$((source_cycle + BLOCK_SIZE))
  oldjob="stage16n_r4q_block$(printf '%02d' "$block_index")_${previous_cycle}_to_$((previous_cycle + SAFE_JUMP))_solve_$((previous_cycle + SAFE_JUMP + 1))_to_${source_cycle}"
  block_index=$((block_index + 1))
done

df -h /scratch9 /scratch /home 2>/dev/null | tee "$LOG_DIR/R4Q_storage_df_after.txt" || true
du -sh /scratch9/"$USER" 2>/dev/null | tee "$LOG_DIR/R4Q_storage_scratch9_user_after.txt" || true
write_status "finished_or_safe_stopped" "controller_end" "source_cycle=$source_cycle block_index=$block_index"
copy_lightweight_evidence
echo "[Stage16N-R4Q] end: $(date '+%Y-%m-%d %H:%M:%S')"
