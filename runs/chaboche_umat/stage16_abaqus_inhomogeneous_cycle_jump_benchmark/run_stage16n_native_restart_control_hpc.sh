#!/usr/bin/env bash
set -euo pipefail

# Stage 16N-R1 restart-enabled reference dispatcher.
# Usage:
#   bash run_stage16n_native_restart_control_hpc.sh R1B
#   bash run_stage16n_native_restart_control_hpc.sh R1A

CASE="${1:-}"
if [[ "$CASE" != "R1A" && "$CASE" != "R1B" ]]; then
  echo "Usage: $0 R1A|R1B" >&2
  echo "  R1B: restart-enabled reference to cycle 250" >&2
  echo "  R1A: restart-enabled reference to cycle 500" >&2
  exit 2
fi

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE16="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"

cd "$REPO_ROOT"
python3 "$STAGE16/prepare_stage16n_restart_reference_with_checkpoints.py" --case "$CASE"

if [[ "$CASE" == "R1B" ]]; then
  RUN_DIR="$STAGE16/stage16n_restart_control/R1B_restart_reference_250cycles"
  JOB="stage16n_r1b_restart_ref_250cycles"
else
  RUN_DIR="$STAGE16/stage16n_restart_control/R1A_restart_reference_500cycles"
  JOB="stage16n_r1a_restart_ref_500cycles"
fi

cd "$RUN_DIR"
bash run_stage16n_r1_restart_reference_hpc.sh "$JOB"
