#!/usr/bin/env bash
set -euo pipefail

OLDJOB="stage16n_r1a_restart_ref_500cycles"
SCRATCH9_SOURCE="/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"
HOME_SOURCE="$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"

find_source() {
  local ext="$1"
  local candidate
  for candidate in \
    "$SCRATCH9_SOURCE/${OLDJOB}.${ext}" \
    "$HOME_SOURCE/${OLDJOB}.${ext}"; do
    if [[ -e "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

echo "Linking R1A restart sources from scratch/home retained sources"
for ext in stt res sim prt; do
  src="$(find_source "$ext")"
  dst="${OLDJOB}.${ext}"
  ln -sfn "$src" "$dst"
done

for ext in odb mdl; do
  if src="$(find_source "$ext")"; then
    ln -sfn "$src" "${OLDJOB}.${ext}"
  else
    echo "Optional R1A support file not retained after cleanup: ${OLDJOB}.${ext}" >&2
  fi
done
