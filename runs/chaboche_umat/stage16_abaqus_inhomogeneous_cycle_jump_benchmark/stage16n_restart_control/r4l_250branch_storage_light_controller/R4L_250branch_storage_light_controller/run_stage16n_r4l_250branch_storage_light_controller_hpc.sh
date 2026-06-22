#!/usr/bin/env bash
set -euo pipefail

CONTROLLER="stage16n_r4l_250branch_storage_light_controller"
BASE_OLDJOB="stage16n_r1a_restart_ref_500cycles"
PREVIOUS_CYCLE="100"
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
  return $rc
}

copy_lightweight_evidence() {
  if [[ -n "${HOME_CASE_DIR:-}" && -d "${SCRATCH_CASE_DIR:-}" ]]; then
    mkdir -p "$HOME_CASE_DIR"
    rsync -av \
      --include='*/' \
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
      --exclude='state.bin' \
      --exclude='state.csv' \
      --exclude='*' \
      "$SCRATCH_CASE_DIR/" "$HOME_CASE_DIR/"
  fi
}

cleanup_case_heavy() {
  local source_job="$1"
  local job="$2"
  if [[ "$CLEAN_HEAVY_AFTER_CLASSIFICATION" != "1" ]]; then
    return 0
  fi
  find . -maxdepth 1 -type f \( \
    -name "${source_job}*.odb" -o -name "${source_job}*.stt" -o -name "${source_job}*.res" -o \
    -name "${source_job}*.sim" -o -name "${source_job}*.mdl" -o -name "${source_job}*.prt" -o \
    -name "${source_job}*.dat" -o -name "${source_job}*.msg" -o -name "${source_job}*.023" -o \
    -name "${source_job}*.cax" -o -name "${source_job}*.abq" -o -name "${source_job}*.pac" -o \
    -name "${source_job}*.sel" -o -name "${source_job}*.lck" -o \
    -name "${job}*.odb" -o -name "${job}*.stt" -o -name "${job}*.res" -o \
    -name "${job}*.sim" -o -name "${job}*.mdl" -o -name "${job}*.prt" -o \
    -name "${job}*.dat" -o -name "${job}*.msg" -o -name "${job}*.023" -o \
    -name "${job}*.cax" -o -name "${job}*.abq" -o -name "${job}*.pac" -o \
    -name "${job}*.sel" -o -name "${job}*.lck" \) \
    -printf "%p\n" -delete 2>/dev/null || true
}

write_failure_status() {
  local rc="$1"
  {
    echo "# Stage 16N-R4L Controller Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Controller: \`$CONTROLLER\`"
    echo "- Classification: \`infrastructure_or_solver_execution_failure\`"
    echo "- Exit code: \`$rc\`"
    echo "- Heavy cleanup after classification: \`enabled\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > STAGE16N_R4L_CONTROLLER_STATUS.md
}

trap copy_lightweight_evidence EXIT
on_error() {
  local rc=$?
  write_failure_status "$rc"
  copy_lightweight_evidence
  exit "$rc"
}
trap on_error ERR

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4L] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4L] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4L] controller: $CONTROLLER"
echo "[Stage16N-R4L] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"
echo "[Stage16N-R4L] storage-light cleanup=${CLEAN_HEAVY_AFTER_CLASSIFICATION}"

bash link_r1a_restart_sources.sh

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${BASE_OLDJOB}.${ext}" ]]; then
    echo "Missing linked R1A restart source: ${BASE_OLDJOB}.${ext}" >&2
    exit 2
  fi
done

make_jump_state() {
  local job="$1"
  local jump_cycles="$2"
  local jump_cycle="$3"
  rm -f state.bin state.csv STAGE16N_R3J_EXTRAPOLATED_STATE.md
  rm -rf _jump_state
  mkdir -p _jump_state
  phase_time "$job extract slope states" \
    abaqus python stage16n_extract_exact_state_for_reinjection.py \
      --odb "${BASE_OLDJOB}.odb" \
      --cycles "${PREVIOUS_CYCLE},${CHECKPOINT_CYCLE}" \
      --outdir _jump_state \
    2>&1 | tee "$LOG_DIR/${job}_extract_slope_states.log"
  phase_time "$job make extrapolated state" \
    python3 stage16n_make_extrapolated_state.py \
      --previous-csv "_jump_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \
      --base-csv "_jump_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" \
      --previous-cycle "$PREVIOUS_CYCLE" \
      --base-cycle "$CHECKPOINT_CYCLE" \
      --jump-cycles "$jump_cycles" \
      --output-cycle "$jump_cycle" \
      --output-csv state.csv \
      --output-bin state.bin \
      --output-summary STAGE16N_R3J_EXTRAPOLATED_STATE.md \
    2>&1 | tee "$LOG_DIR/${job}_make_extrapolated_state.log"
}

run_case() {
  local label="$1"
  local job="$2"
  local source_job="$3"
  local restart_cycle="$4"
  local first_solved_cycle="$5"
  local jump_cycles="$6"
  local jump_cycle="$7"
  local source_input="${source_job}.inp"
  local cont_input="${job}.inp"

  echo
  echo "[Stage16N-R4L] ${label}: source=$source_job continuation=$job"
  make_jump_state "$job" "$jump_cycles" "$jump_cycle"

  phase_time "$label source solve" \
    abaqus job="$source_job" input="$source_input" oldjob="$BASE_OLDJOB" \
      user=stage16n_neml_equivalent_chaboche_umat.for \
      interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${source_job}.log"

  if [[ ! -f "${source_job}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${source_job}.sta"; then
    echo "$label source solve did not complete successfully; check $source_job.sta" >&2
    exit 2
  fi

  local restart_inc
  restart_inc="$(awk -v step="$restart_cycle" '$1 == step && $2 ~ /^[0-9]+$/ {inc=$2} END {if (inc == "") exit 3; print inc}' "${source_job}.sta")"
  python3 - <<PY
from pathlib import Path
path = Path("$cont_input")
path.write_text(path.read_text().replace("INC=__R4I_RESTART_INC__", "INC=$restart_inc"))
PY

  phase_time "$label source extraction" \
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$source_job" \
    2>&1 | tee "$LOG_DIR/${source_job}_extract.log" || true

  for ext in odb res stt mdl sim prt; do
    if [[ ! -e "${source_job}.${ext}" ]]; then
      echo "Missing generated source restart file: ${source_job}.${ext}" >&2
      exit 2
    fi
  done

  export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
  export STAGE16N_JUMP_TARGET_STEP="$first_solved_cycle"
  export STAGE16N_JUMP_CHECK_TIME="$restart_cycle"

  echo "[Stage16N-R4L] $label restart read: oldjob=$source_job step=$restart_cycle inc=$restart_inc"
  echo "[Stage16N-R4L] $label overwrite trigger: JSTEP(1)=$first_solved_cycle KINC=0 TIME(2)=$restart_cycle"

  phase_time "$label continuation datacheck" \
    abaqus job="${job}_datacheck" input="$cont_input" oldjob="$source_job" \
      user=stage16n_r3_jump_umat.for \
      datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \
      cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${job}_datacheck.log"

  phase_time "$label continuation solve" \
    abaqus job="$job" input="$cont_input" oldjob="$source_job" \
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
    echo "# Stage 16N-R4L ${label} Case Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Case: \`$label\`"
    echo "- Job: \`$job\`"
    echo "- Source job: \`$source_job\`"
    echo "- Source construction: \`validated deck-clone/truncate 250-branch source\`"
    echo "- Restart read: \`STEP=$restart_cycle, INC=$restart_inc\`"
    echo "- True-jump target: \`$jump_cycle\`"
    echo "- First solved cycle: \`$first_solved_cycle\`"
    echo "- Final cycle: \`$FINAL_CYCLE\`"
    echo "- Continuation restart writing: \`disabled\`"
    echo "- Classification: \`$classification\`"
    if [[ -f "${job}_comparison_summary.csv" ]]; then
      tail -n +2 "${job}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
    fi
    echo "- Heavy cleanup after classification: \`enabled\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > "STAGE16N_R4L_${label}_CASE_STATUS.md"

  if [[ "$classification" != "pass" ]]; then
    write_diagnostics "$label" "$job" "$source_job" "$restart_cycle" "$first_solved_cycle"
  fi

  copy_lightweight_evidence
  cleanup_case_heavy "$source_job" "$job"
  rm -f state.bin state.csv
  copy_lightweight_evidence
  echo "$classification"
}

write_diagnostics() {
  local label="$1"
  local job="$2"
  local source_job="$3"
  local restart_cycle="$4"
  local first_solved_cycle="$5"
  python3 - <<PY
import csv
from pathlib import Path
label = "$label"
job = "$job"
source_job = "$source_job"
restart_cycle = "$restart_cycle"
first_solved_cycle = "$first_solved_cycle"
out = Path(f"STAGE16N_R4L_{label}_DIAGNOSTIC_SUMMARY.md")
lines = [
    f"# Stage 16N-R4L {label} Diagnostic Summary",
    "",
    f"- Source cycle state check: inspect `{source_job}_cycle_metrics.csv` and `{source_job}_selected_cycle_local_states.csv` near cycle `{restart_cycle}`.",
    f"- First solved continuation cycle check: inspect `{job}_cycle_metrics.csv` and `{job}_selected_cycle_local_states.csv` at cycle `{first_solved_cycle}`.",
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

R4L1_CLASSIFICATION="$(run_case \
  "R4L1" \
  "stage16n_r4l1_deck_clone_jump_250_to_270_solve_271_to_500" \
  "stage16n_r4l1_deck_clone_jump_250_to_270_solve_271_to_500_source_250_to_271" \
  "270" \
  "271" \
  "20" \
  "270" | tee "$LOG_DIR/stage16n_r4l1_case.log" | tail -n 1)"

if [[ "$R4L1_CLASSIFICATION" == "pass" ]]; then
  R4L2_CLASSIFICATION="$(run_case \
    "R4L2" \
    "stage16n_r4l2_deck_clone_jump_250_to_280_solve_281_to_500" \
    "stage16n_r4l2_deck_clone_jump_250_to_280_solve_281_to_500_source_250_to_281" \
    "280" \
    "281" \
    "30" \
    "280" | tee "$LOG_DIR/stage16n_r4l2_case.log" | tail -n 1)"
else
  R4L2_CLASSIFICATION="not_run_r4l1_${R4L1_CLASSIFICATION}"
fi

{
  echo "# Stage 16N-R4L Controller Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Controller: \`$CONTROLLER\`"
  echo "- Purpose: storage-light true-jump candidates on the validated 250 branch."
  echo "- R4L1 classification: \`$R4L1_CLASSIFICATION\`"
  echo "- R4L2 classification: \`$R4L2_CLASSIFICATION\`"
  echo "- R4J9/R4J10: \`blocked\`"
  echo "- 505 branch: \`parked_after_R4K2B_review\`"
  echo "- Continuation restart writing: \`disabled\`"
  echo "- Heavy copy-back: \`disabled\`"
  echo "- Heavy cleanup after classification: \`enabled\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4L_CONTROLLER_STATUS.md

copy_lightweight_evidence
echo "[Stage16N-R4L] R4L1 classification: $R4L1_CLASSIFICATION"
echo "[Stage16N-R4L] R4L2 classification: $R4L2_CLASSIFICATION"
echo "[Stage16N-R4L] end: $(date '+%Y-%m-%d %H:%M:%S')"
