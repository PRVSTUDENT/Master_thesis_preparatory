#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R2C1_100_to_250|R2C2_250_to_500>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/stage16n_restart_control/native_restart_cases"
CASE_DIR="${ROOT_DIR}/${CASE_ID}"
MANIFEST="${ROOT_DIR}/stage16n_r2_native_restart_cases.csv"

if [[ ! -d "$CASE_DIR" ]]; then
  echo "Unknown case directory: $CASE_DIR" >&2
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing manifest: $MANIFEST" >&2
  exit 2
fi

row="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $0}' "$MANIFEST")"
if [[ -z "$row" ]]; then
  echo "Case not found in manifest: $CASE_ID" >&2
  exit 2
fi

IFS=, read -r case_id job oldjob checkpoint_cycle checkpoint_inc target_cycle <<< "$row"
cd "$CASE_DIR"
bash link_restart_sources.sh
bash run_stage16n_native_restart_continuation_hpc.sh "$job" "$oldjob" "$target_cycle"
