#!/usr/bin/env bash
set -euo pipefail

OLDJOB="stage16n_r1a_restart_ref_500cycles"
SCRATCH9_SOURCE="/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"
HOME_SOURCE="$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"

if [[ -d "$SCRATCH9_SOURCE" ]]; then
  SOURCE_DIR="$SCRATCH9_SOURCE"
else
  SOURCE_DIR="$HOME_SOURCE"
fi

echo "Linking R1A restart sources from: $SOURCE_DIR"
for ext in odb res stt mdl sim prt; do
  src="$SOURCE_DIR/${OLDJOB}.${ext}"
  dst="${OLDJOB}.${ext}"
  if [[ ! -e "$src" ]]; then
    echo "Missing base restart source: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done
