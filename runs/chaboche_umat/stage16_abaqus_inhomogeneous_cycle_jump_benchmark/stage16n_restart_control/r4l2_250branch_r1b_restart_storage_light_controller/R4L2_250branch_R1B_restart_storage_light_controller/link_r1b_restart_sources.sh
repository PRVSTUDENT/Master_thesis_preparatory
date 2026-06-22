#!/usr/bin/env bash
set -euo pipefail

OLDJOB="stage16n_r1b_restart_ref_250cycles"
CASE_REL="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles"

SEARCH_DIRS=(
  "$HOME/master_thesis/Abaqus_trial/$CASE_REL"
  "/scratch9/$USER/home_offload/home/$USER/master_thesis/Abaqus_trial/$CASE_REL"
)

find_source() {
  local ext="$1"
  local src
  for dir in "${SEARCH_DIRS[@]}"; do
    src="$dir/${OLDJOB}.${ext}"
    if [[ -e "$src" ]]; then
      printf '%s\n' "$src"
      return 0
    fi
  done
  return 1
}

echo "[R4L2] Linking R1B restart source files for oldjob=$OLDJOB"
for ext in stt res mdl prt sim sta; do
  src="$(find_source "$ext")" || {
    echo "Missing required R1B restart source: ${OLDJOB}.${ext}" >&2
    echo "Searched:" >&2
    printf '  %s\n' "${SEARCH_DIRS[@]}" >&2
    exit 2
  }
  ln -sfn "$src" "${OLDJOB}.${ext}"
  ls -lh "${OLDJOB}.${ext}"
done

if src="$(find_source odb)"; then
  ln -sfn "$src" "${OLDJOB}.odb"
  echo "[R4L2] Optional R1B ODB linked: $src"
else
  echo "[R4L2] Optional R1B ODB not available; continuing because R4L2 has no source-ODB dependency."
fi

if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${OLDJOB}.sta"; then
  echo "R1B .sta does not show clean completion." >&2
  exit 2
fi

if ! awk '$1 == 250 && $2 ~ /^[0-9]+$/ {found=1} END {exit found ? 0 : 1}' "${OLDJOB}.sta"; then
  echo "R1B .sta does not contain a readable cycle-250 restart row." >&2
  exit 2
fi

echo "[R4L2] R1B preflight passed: required restart companions are linked and .sta completed cycle 250."
