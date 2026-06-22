#!/usr/bin/env bash
set -euo pipefail

JOB="stage16n_r4k2_deck_clone_exact_505_to_750"
RESTART_CYCLE="505"
FIRST_SOLVED_CYCLE="506"
FINAL_CYCLE="750"
MIN_STT_BYTES="${MIN_STT_BYTES:-1073741824}"
LOG_DIR="${LOG_DIR:-_logs}"
mkdir -p "$LOG_DIR"

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
      --exclude='*' \
      "$SCRATCH_CASE_DIR/" "$HOME_CASE_DIR/"
  fi
}
trap copy_lightweight_evidence EXIT

echo "[Stage16N-R4K2] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4K2] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R4K2] purpose: locate existing clean 505 restart source before any Abaqus solve"

set +e
phase_time "R4K2 505 restart-source preflight" bash -lc '
  set -euo pipefail
  {
    echo "# Stage 16N-R4K2 505 Restart Source Preflight"
    echo
    echo "- PBS job: '"${PBS_JOBID:-manual}"'"
    echo "- Time: $(date "+%Y-%m-%d %H:%M:%S")"
    echo "- Search roots: /scratch9/pr21vyci, /scratch/pr21vyci, /home/pr21vyci/master_thesis/Abaqus_trial"
    echo "- Minimum accepted .stt size: '"$MIN_STT_BYTES"' bytes"
    echo "- Excluded families: generated-buffer/source-split R4I and R4I-R branches"
    echo
    echo "## Storage"
    df -h /home /scratch /scratch9 2>/dev/null || df -h /home /scratch
    echo
    echo "## Candidate files containing 505 in path"
    find /scratch9/pr21vyci /scratch/pr21vyci /home/pr21vyci/master_thesis/Abaqus_trial \
      \( -name "*.stt" -o -name "*.res" -o -name "*.prt" -o -name "*.mdl" \) \
      -path "*505*" -printf "%s %p\n" 2>/dev/null | sort -nr | head -120 || true
    echo
    echo "## Validation"
  } > R4K2_505_RESTART_SOURCE_PREFLIGHT.md

  mapfile -t stt_candidates < <(
    find /scratch9/pr21vyci /scratch/pr21vyci /home/pr21vyci/master_thesis/Abaqus_trial \
      -name "*.stt" -path "*505*" -printf "%p\n" 2>/dev/null | sort
  )

  valid=""
  for stt in "${stt_candidates[@]}"; do
    base="${stt%.stt}"
    case "$base" in
      *stage16n_r4i/*|*stage16n_r4ir/*|*r4i_restart_source_buffer_diagnostics/*|*r4ir_restart_source_buffer_recovery/*|*buffer_*|*source_500_to_525*|*R4H6_source_500_to_506*)
        continue
        ;;
    esac
    stt_size="$(stat -c%s "$stt" 2>/dev/null || echo 0)"
    if (( stt_size >= '"$MIN_STT_BYTES"' )) && [[ -s "${base}.res" && -s "${base}.prt" && -s "${base}.mdl" ]]; then
      sta="${base}.sta"
      if [[ -s "$sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "$sta"; then
        valid="$base"
        break
      fi
    fi
  done

  if [[ -z "$valid" ]]; then
    {
      echo "- Classification: no_valid_existing_505_restart_source_found"
      echo "- Action: stop before Abaqus solve; do not recreate the failing source .stt in this controller."
      echo "- Required next decision: free/relocate scratch or design a source-light 505 restart strategy before rerunning."
    } >> R4K2_505_RESTART_SOURCE_PREFLIGHT.md
    exit 20
  fi

  {
    echo "- Classification: valid_existing_505_restart_source_found"
    echo "- Valid source base: $valid"
    echo "- Note: R4K2 solve execution is intentionally not armed in this preflight-first controller until the validated source is reviewed."
  } >> R4K2_505_RESTART_SOURCE_PREFLIGHT.md
'
PREFLIGHT_RC=$?
set -e

if [[ "$PREFLIGHT_RC" -eq 20 ]]; then
  {
    echo "# Stage 16N-R4K2 Case Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Job: \`$JOB\`"
    echo "- Classification: \`no_valid_existing_505_restart_source_found\`"
    echo "- Action: stopped before Abaqus solve; no source `.stt` recreation attempted."
    echo "- First solved cycle if later redesigned: \`$FIRST_SOLVED_CYCLE\`"
    echo "- Final cycle if later redesigned: \`$FINAL_CYCLE\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > STAGE16N_R4K_CASE_STATUS.md
  copy_lightweight_evidence
  echo "[Stage16N-R4K2] no valid 505 restart source found; stopped before Abaqus solve"
  exit 20
elif [[ "$PREFLIGHT_RC" -ne 0 ]]; then
  {
    echo "# Stage 16N-R4K2 Case Status"
    echo
    echo "- PBS job: \`${PBS_JOBID:-manual}\`"
    echo "- Job: \`$JOB\`"
    echo "- Classification: \`preflight_failed\`"
    echo "- Exit code: \`$PREFLIGHT_RC\`"
    echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  } > STAGE16N_R4K_CASE_STATUS.md
  copy_lightweight_evidence
  exit "$PREFLIGHT_RC"
fi

{
  echo "# Stage 16N-R4K2 Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Job: \`$JOB\`"
  echo "- Classification: \`preflight_only_completed\`"
  echo "- First solved cycle if later armed: \`$FIRST_SOLVED_CYCLE\`"
  echo "- Final cycle if later armed: \`$FINAL_CYCLE\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
} > STAGE16N_R4K_CASE_STATUS.md

copy_lightweight_evidence
echo "[Stage16N-R4K2] end: $(date '+%Y-%m-%d %H:%M:%S')"
