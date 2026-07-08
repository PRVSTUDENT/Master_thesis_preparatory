#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R4I case id>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="${SCRIPT_DIR}/stage16n_restart_control/r4i_restart_source_buffer_diagnostics/${CASE_ID}"
MANIFEST="${SCRIPT_DIR}/stage16n_restart_control/r4i_restart_source_buffer_diagnostics/stage16n_r4i_restart_source_buffer_diagnostics.csv"
pbs_script="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $12}' "$MANIFEST")"

if [[ -z "$pbs_script" || ! -d "$CASE_DIR" ]]; then
  echo "Unknown R4I case: $CASE_ID" >&2
  exit 2
fi

mkdir -p /scratch/$USER/stage16n_r4i_pbs
cd "$CASE_DIR"
if command -v qsub_abq >/dev/null 2>&1; then
  qsub_abq "$pbs_script"
elif [[ -x "$HOME/bin/qsub_abq_guarded" ]]; then
  "$HOME/bin/qsub_abq_guarded" "$pbs_script"
else
  echo "qsub_abq guarded wrapper not found; refusing raw qsub for Abaqus job" >&2
  exit 2
fi
