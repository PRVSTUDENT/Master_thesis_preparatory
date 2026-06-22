#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="stage16n_r4l2_250branch_r1b_restart_storage_light_controller"
OLDJOB="stage16n_r1b_restart_ref_250cycles"
CHECKPOINT_CYCLE="250"
FINAL_CYCLE="500"

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
ABAQUS_SCRATCH="${TMPDIR:-$PWD/tmp}"
CLEAN_HEAVY_AFTER_CLASSIFICATION="${CLEAN_HEAVY_AFTER_CLASSIFICATION:-1}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

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

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${SCRATCH_CASE_DIR:-}" ]]; then
    mkdir -p "$HOME_CASE_DIR"
    rsync -av \
      --include='*/' \
      --exclude='state.bin' \
      --exclude='state.csv' \
      --include='*.md' \
      --include='*.csv' \
      --include='*.txt' \
      --include='*.sta' \
      --include='*.log' \
      --include='*.out' \
      --include='*.pbs.out' \
      --exclude='*.odb' \
      --exclude='*.stt' \
      --exclude='*.res' \
      --exclude='*.sim' \
      --exclude='*.mdl' \
      --exclude='*.prt' \
      --exclude='*.dat' \
      --exclude='*.msg' \
      --exclude='*.023' \
      --exclude='*.cax' \
      --exclude='*.abq' \
      --exclude='*.pac' \
      --exclude='*.sel' \
      --exclude='*.lck' \
      --exclude='*' \
      "$SCRATCH_CASE_DIR/" "$HOME_CASE_DIR/"
  fi
}

cleanup_case_heavy() {
  local job="$1"
  if [[ "$CLEAN_HEAVY_AFTER_CLASSIFICATION" != "1" ]]; then
    return 0
  fi
  find . -maxdepth 1 -type f \( \
    -name "${job}*.odb" -o -name "${job}*.stt" -o -name "${job}*.res" -o \
    -name "${job}*.sim" -o -name "${job}*.mdl" -o -name "${job}*.prt" -o \
    -name "${job}*.dat" -o -name "${job}*.msg" -o -name "${job}*.023" -o \
    -name "${job}*.cax" -o -name "${job}*.abq" -o -name "${job}*.pac" -o \
    -name "${job}*.sel" -o -name "${job}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
  rm -f state.bin state.csv
}

write_controller_failure() {
  local rc="$1"
  {
    echo "# Stage 16N-R4L2 Controller Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Controller: \`$CONTROLLER\`"
    echo "- Oldjob: \`$OLDJOB\`"
    echo "- Classification: \`infrastructure_or_preflight_failure\`"
    echo "- Exit code: \`$rc\`"
    echo "- R1A usage: \`disabled\`"
    echo "- Source ODB dependency: \`disabled\`"
    echo "- Continuation restart writing: \`disabled\`"
    echo "- Heavy cleanup after classification: \`enabled\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > STAGE16N_R4L2_CONTROLLER_STATUS.md
}

trap copy_lightweight_evidence EXIT
on_error() {
  local rc=$?
  write_controller_failure "$rc"
  copy_lightweight_evidence
  exit "$rc"
}
trap on_error ERR

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4L2] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4L2] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4L2] controller: $CONTROLLER"
echo "[Stage16N-R4L2] oldjob: $OLDJOB"
echo "[Stage16N-R4L2] R1A usage disabled"
echo "[Stage16N-R4L2] source ODB dependency disabled"
echo "[Stage16N-R4L2] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R4L2] storage-light cleanup=${CLEAN_HEAVY_AFTER_CLASSIFICATION}"

bash link_r1b_restart_sources.sh
for ext in stt res mdl prt sim sta; do
  test -e "${OLDJOB}.${ext}"
done

R1B_RESTART_INC="$(awk -v step="$CHECKPOINT_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${OLDJOB}.sta")"
echo "[Stage16N-R4L2] R1B restart row: STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"

csv_to_state_bin() {
  local csv_path="$1"
  local bin_path="$2"
  python3 - <<PY
import csv
import struct
from pathlib import Path
csv_path = Path("$csv_path")
bin_path = Path("$bin_path")
rows = []
with csv_path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        noel = int(row["NOEL"])
        npt = int(row["NPT"])
        values = [float(row.get(f"S{i}") or 0.0) for i in range(1, 7)]
        values.extend(float(row[f"SDV{i}"]) for i in range(1, 28))
        rows.append((noel, npt, values))
max_record = max((noel - 1) * 8 + npt for noel, npt, _ in rows)
with bin_path.open("wb") as handle:
    handle.truncate(max_record * 33 * 8)
    for noel, npt, values in rows:
        recno = (noel - 1) * 8 + npt
        handle.seek((recno - 1) * 33 * 8)
        handle.write(struct.pack("<33d", *values))
PY
}

use_cached_jump_state() {
  local jump_cycle="$1"
  local cache_dir=""

  case "$jump_cycle" in
    270)
      for candidate in \
        "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4J3_250_to_270_solve_271_to_500" \
        "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R3J5_250_to_270_to_500"; do
        if [[ -f "$candidate/state.csv" ]]; then
          cache_dir="$candidate"
          break
        fi
      done
      ;;
    280)
      for candidate in \
        "$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4J7_250_to_280_solve_281_to_500"; do
        if [[ -f "$candidate/state.csv" ]]; then
          cache_dir="$candidate"
          break
        fi
      done
      ;;
    *)
      echo "Unsupported cached jump target: $jump_cycle" >&2
      return 10
      ;;
  esac

  if [[ -z "$cache_dir" ]]; then
    echo "[Stage16N-R4L2] no cached jump state available for target $jump_cycle" >&2
    return 10
  fi

  rm -f state.bin state.csv STAGE16N_R3J_EXTRAPOLATED_STATE.md
  cp "$cache_dir/state.csv" state.csv
  if [[ -f "$cache_dir/state.bin" ]]; then
    cp "$cache_dir/state.bin" state.bin
  else
    csv_to_state_bin state.csv state.bin
  fi
  if [[ -f "$cache_dir/STAGE16N_R3J_EXTRAPOLATED_STATE.md" ]]; then
    cp "$cache_dir/STAGE16N_R3J_EXTRAPOLATED_STATE.md" STAGE16N_R3J_EXTRAPOLATED_STATE.md
  else
    {
      echo "# Stage 16N-R4L2 Cached Jump State"
      echo
      echo "- Cached source: \`$cache_dir\`"
      echo "- Extrapolated material-state cycle: \`$jump_cycle\`"
      echo "- State CSV: \`state.csv\`"
      echo "- State binary: \`state.bin\`"
    } > STAGE16N_R3J_EXTRAPOLATED_STATE.md
  fi
  echo "[Stage16N-R4L2] using cached jump state for target $jump_cycle from $cache_dir"
}

write_diagnostics() {
  local label="$1"
  local job="$2"
  local solved_cycle="$3"
  python3 - <<PY
import csv
from pathlib import Path
label = "$label"
job = "$job"
solved_cycle = "$solved_cycle"
out = Path(f"STAGE16N_R4L2_{label}_DIAGNOSTIC_SUMMARY.md")
lines = [
    f"# Stage 16N-R4L2 {label} Diagnostic Summary",
    "",
    "- Source restart: R1B cycle-250 restart source, linked without requiring `.odb`.",
    f"- First solved continuation cycle check: inspect `{job}_cycle_metrics.csv` and `{job}_selected_cycle_local_states.csv` at cycle `{solved_cycle}`.",
    f"- Comparison details: `{job}_comparison_details.csv`.",
    "- Local hole-ring metric ranking: see top nonzero comparison errors below.",
    "",
]
details = Path(f"{job}_comparison_details.csv")
rows = []
if details.exists():
    with details.open(newline="") as f:
        for row in csv.DictReader(f):
            try:
                row["_err"] = abs(float(row.get("error_pct") or 0.0))
            except ValueError:
                row["_err"] = 0.0
            if "local" in row.get("kind", "").lower() or "HOLE_RING" in row.get("metric", ""):
                rows.append(row)
    rows.sort(key=lambda r: r["_err"], reverse=True)
    lines.append("| kind | cycle | metric | error_pct |")
    lines.append("| --- | ---: | --- | ---: |")
    for row in rows[:20]:
        lines.append(f"| {row.get('kind','')} | {row.get('cycle','')} | {row.get('metric','')} | {row.get('error_pct','')} |")
else:
    lines.append("- Comparison details file was not available.")
out.write_text("\n".join(lines) + "\n")
PY
}

run_case() {
  local label="$1"
  local job="$2"
  local input="$3"
  local jump_cycle="$4"
  local trigger_step="$5"
  local solved_cycle="$6"

  echo
  echo "[Stage16N-R4L2] ${label}: oldjob=$OLDJOB continuation=$job target=$jump_cycle"
  if ! use_cached_jump_state "$jump_cycle"; then
    {
      echo "# Stage 16N-R4L2 ${label} Case Status"
      echo
      echo "- PBS job: \`${PBS_JOBID:-manual}\`"
      echo "- Case: \`$label\`"
      echo "- Job: \`$job\`"
      echo "- Oldjob: \`$OLDJOB\`"
      echo "- Classification: \`blocked_missing_cached_jump_state\`"
      echo "- Missing true-jump state target: \`$jump_cycle\`"
      echo "- R1A usage: \`disabled\`"
      echo "- Source ODB dependency: \`disabled\`"
      echo "- Solver status: \`not_submitted_for_case\`"
      echo "- Heavy cleanup after classification: \`enabled\`"
      echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
    } > "STAGE16N_R4L2_${label}_CASE_STATUS.md"
    copy_lightweight_evidence
    echo "blocked_missing_cached_jump_state"
    return 0
  fi

  export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
  export STAGE16N_JUMP_TARGET_STEP="$trigger_step"
  export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

  echo "[Stage16N-R4L2] $label restart read: oldjob=$OLDJOB STEP=$CHECKPOINT_CYCLE INC=$R1B_RESTART_INC"
  echo "[Stage16N-R4L2] $label overwrite trigger: JSTEP(1)=$trigger_step KINC=0 TIME(2)=$CHECKPOINT_CYCLE"

  phase_time "$label continuation datacheck" \
    abaqus job="${job}_datacheck" input="$input" oldjob="$OLDJOB" \
      user=stage16n_r3_jump_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${job}_datacheck.log"

  phase_time "$label continuation solve" \
    abaqus job="$job" input="$input" oldjob="$OLDJOB" \
      user=stage16n_r3_jump_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${job}.log"

  grep "STAGE16N_R3J_OVERWRITE" "${job}.dat" > "$LOG_DIR/${job}_overwrite_trace.txt" || true
  grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${job}.msg" | tee "$LOG_DIR/${job}_parallelism_check.log" || true

  phase_time "$label ODB extraction" \
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$job" \
    2>&1 | tee "$LOG_DIR/${job}_extract.log"

  copy_lightweight_evidence

  set +e
  phase_time "$label comparison" \
    python3 stage16n_compare_r3j_jump_against_reference.py \
      --jump-metrics "${job}_cycle_metrics.csv" \
      --jump-local-states "${job}_selected_cycle_local_states.csv" \
      --ref-metrics "reference_1000_cycle_metrics.csv" \
      --ref-local-states "reference_1000_selected_cycle_local_states.csv" \
      --cycles "$FINAL_CYCLE" \
      --out-dir "." \
      --prefix "$job" \
    2>&1 | tee "$LOG_DIR/${job}_compare.log"
  local compare_rc=${PIPESTATUS[0]}
  set -e

  local classification="review_or_fail"
  if [[ "$compare_rc" -eq 0 && -f "${job}_comparison_summary.csv" ]] && awk -F, 'NR == 2 && $2 == "pass" {ok=1} END {exit ok ? 0 : 1}' "${job}_comparison_summary.csv"; then
    classification="pass"
  fi

  {
    echo "# Stage 16N-R4L2 ${label} Case Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Case: \`$label\`"
    echo "- Job: \`$job\`"
    echo "- Oldjob: \`$OLDJOB\`"
    echo "- Source construction: \`R1B direct cycle-250 Abaqus restart source\`"
    echo "- Restart read: \`STEP=$CHECKPOINT_CYCLE, INC=$R1B_RESTART_INC\`"
    echo "- True-jump target: \`$jump_cycle\`"
    echo "- Overwrite trigger step: \`$trigger_step\`"
    echo "- First solved cycle: \`$solved_cycle\`"
    echo "- Final cycle: \`$FINAL_CYCLE\`"
    echo "- R1A usage: \`disabled\`"
    echo "- Source ODB dependency: \`disabled\`"
    echo "- Continuation restart writing: \`disabled\`"
    echo "- Classification: \`$classification\`"
    if [[ -f "${job}_comparison_summary.csv" ]]; then
      tail -n +2 "${job}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
    fi
    echo "- Heavy cleanup after classification: \`enabled\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > "STAGE16N_R4L2_${label}_CASE_STATUS.md"

  if [[ "$classification" != "pass" ]]; then
    write_diagnostics "$label" "$job" "$solved_cycle"
  fi

  copy_lightweight_evidence
  cleanup_case_heavy "$job"
  copy_lightweight_evidence
  echo "$classification"
}

R4L2_1_CLASSIFICATION="$(run_case \
  "R4L2_1" \
  "stage16n_r4l2_1_r1b_jump_250_to_270_solve_271_to_500" \
  "stage16n_r4l2_1_r1b_jump_250_to_270_solve_271_to_500.inp" \
  "270" \
  "251" \
  "271" | tee "$LOG_DIR/stage16n_r4l2_1_case.log" | tail -n 1)"

if [[ "$R4L2_1_CLASSIFICATION" == "pass" ]]; then
  R4L2_2_CLASSIFICATION="$(run_case \
    "R4L2_2" \
    "stage16n_r4l2_2_r1b_jump_250_to_280_solve_281_to_500" \
    "stage16n_r4l2_2_r1b_jump_250_to_280_solve_281_to_500.inp" \
    "280" \
    "251" \
    "281" | tee "$LOG_DIR/stage16n_r4l2_2_case.log" | tail -n 1)"
else
  R4L2_2_CLASSIFICATION="not_run_r4l2_1_${R4L2_1_CLASSIFICATION}"
fi

{
  echo "# Stage 16N-R4L2 Controller Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Controller: \`$CONTROLLER\`"
  echo "- Purpose: R1B-based storage-light true-jump candidates on the validated 250 branch."
  echo "- Oldjob: \`$OLDJOB\`"
  echo "- R1B restart row: \`STEP=$CHECKPOINT_CYCLE, INC=$R1B_RESTART_INC\`"
  echo "- R4L2-1 classification: \`$R4L2_1_CLASSIFICATION\`"
  echo "- R4L2-2 classification: \`$R4L2_2_CLASSIFICATION\`"
  echo "- R1A usage: \`disabled\`"
  echo "- Source ODB dependency: \`disabled\`"
  echo "- R4J9/R4J10: \`blocked\`"
  echo "- 505 branch: \`parked_after_R4K2B_review\`"
  echo "- Continuation restart writing: \`disabled\`"
  echo "- Heavy copy-back: \`disabled\`"
  echo "- Heavy cleanup after classification: \`enabled\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4L2_CONTROLLER_STATUS.md

copy_lightweight_evidence
echo "[Stage16N-R4L2] R4L2-1 classification: $R4L2_1_CLASSIFICATION"
echo "[Stage16N-R4L2] R4L2-2 classification: $R4L2_2_CLASSIFICATION"
echo "[Stage16N-R4L2] end: $(date '+%Y-%m-%d %H:%M:%S')"
