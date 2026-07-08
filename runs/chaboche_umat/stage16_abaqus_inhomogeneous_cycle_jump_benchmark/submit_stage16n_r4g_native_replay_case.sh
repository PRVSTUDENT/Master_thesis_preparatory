#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R4G case id>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="${SCRIPT_DIR}/stage16n_restart_control/r4g_native_replay_cases/${CASE_ID}"
MANIFEST="${SCRIPT_DIR}/stage16n_restart_control/r4g_native_replay_cases/stage16n_r4g_native_replay_cases.csv"
pbs_script="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $11}' "$MANIFEST")"

if [[ -z "$pbs_script" || ! -d "$CASE_DIR" ]]; then
  echo "Unknown R4G case: $CASE_ID" >&2
  exit 2
fi

cd "$CASE_DIR"
qsub "$pbs_script"
