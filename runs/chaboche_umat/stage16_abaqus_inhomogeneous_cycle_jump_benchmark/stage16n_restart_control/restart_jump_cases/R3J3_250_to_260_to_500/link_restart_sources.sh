#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="../../R1A_restart_reference_500cycles"
OLDJOB="stage16n_r1a_restart_ref_500cycles"
for ext in odb res stt mdl sim prt; do
  src="${SOURCE_DIR}/${OLDJOB}.${ext}"
  dst="${OLDJOB}.${ext}"
  if [[ ! -e "$src" ]]; then
    echo "Missing restart source: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done
