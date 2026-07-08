#!/usr/bin/env bash
set -euo pipefail

SOURCE_BASE="${R4E2_SOURCE_BASE:-/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source}"
OLDJOB="stage16n_r4k2b_r4e2_candidate_cycle505_source"

echo "[Stage16N-R4K2B] linking preserved R4E2 source:"
echo "[Stage16N-R4K2B]   $SOURCE_BASE"

for ext in stt res mdl prt odb sta inp; do
  src="${SOURCE_BASE}.${ext}"
  dst="${OLDJOB}.${ext}"
  if [[ ! -e "$src" ]]; then
    echo "Missing R4E2 candidate source file: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done

for ext in stt res mdl prt; do
  test -s "${OLDJOB}.${ext}"
done

if ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${OLDJOB}.sta"; then
  echo "R4E2 candidate .sta does not show successful completion" >&2
  exit 3
fi

echo "$OLDJOB"
