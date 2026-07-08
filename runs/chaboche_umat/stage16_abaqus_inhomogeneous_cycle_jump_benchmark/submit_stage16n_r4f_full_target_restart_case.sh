#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R4F1_250_to_280_fullrestart_solve_281_to_500|R4F2_500_to_505_fullrestart_solve_506_to_750>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="${SCRIPT_DIR}/stage16n_restart_control/full_target_restart_cases/${CASE_ID}"
MANIFEST="${SCRIPT_DIR}/stage16n_restart_control/full_target_restart_cases/stage16n_r4f_full_target_restart_cases.csv"

if [[ ! -d "$CASE_DIR" ]]; then
  echo "Unknown case directory: $CASE_DIR" >&2
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing manifest: $MANIFEST" >&2
  exit 2
fi

pbs_script="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $11}' "$MANIFEST")"
if [[ -z "$pbs_script" ]]; then
  echo "Case not found in manifest: $CASE_ID" >&2
  exit 2
fi

cd "$CASE_DIR"
qsub "$pbs_script"
