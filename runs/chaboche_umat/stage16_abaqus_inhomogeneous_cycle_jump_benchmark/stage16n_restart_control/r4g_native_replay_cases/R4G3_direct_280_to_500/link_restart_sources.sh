#!/usr/bin/env bash
set -euo pipefail

DEFAULT_SOURCE_DIR="../../R1A_restart_reference_500cycles"
HPC_SOURCE_DIR="/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"
OLDJOB="stage16n_r1a_restart_ref_500cycles"

SOURCE_DIR="${RESTART_SOURCE_DIR:-$DEFAULT_SOURCE_DIR}"
if [[ ! -e "${SOURCE_DIR}/${OLDJOB}.odb" && -e "${HPC_SOURCE_DIR}/${OLDJOB}.odb" ]]; then
  SOURCE_DIR="$HPC_SOURCE_DIR"
fi

echo "Linking base restart sources from: $SOURCE_DIR"
for ext in odb res stt mdl sim prt; do
  src="${SOURCE_DIR}/${OLDJOB}.${ext}"
  dst="${OLDJOB}.${ext}"
  if [[ ! -e "$src" ]]; then
    echo "Missing base restart source: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done
