#!/usr/bin/env bash
set -euo pipefail

# Stage 16N-R1 native restart control runner.
# This script is a scaffold: review the restart-enabled deck and checkpoint
# availability before using it in production.

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE16="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
RUN_DIR="$STAGE16/stage16n_restart_control"
JOB="${JOB:-stage16n_restart_enabled_reference}"
ABAQUS_CPUS="${ABAQUS_CPUS:-16}"

module load intel/2024.2.0
module load abaqus/2023

cd "$REPO_ROOT"
python3 "$STAGE16/prepare_stage16n_restart_reference_with_checkpoints.py"

cd "$RUN_DIR"
abaqus job="$JOB" input="stage16n_plate_hole_neml_equiv_1000cycles_restart_enabled.inp" \
  user="$STAGE16/stage16n_neml_equivalent_chaboche_umat.for" \
  interactive ask_delete=OFF scratch=. cpus="$ABAQUS_CPUS" mp_mode=threads
