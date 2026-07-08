#!/usr/bin/env bash
set -euo pipefail

REPO=~/master_thesis/Abaqus_trial
BASE="$REPO/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/native_restart_cases"

R2C1_DIR="$BASE/R2C1_100_to_250"
R2C2_DIR="$BASE/R2C2_250_to_500"

if ! command -v module >/dev/null 2>&1; then
  [ -f /etc/profile.d/modules.sh ] && source /etc/profile.d/modules.sh
fi

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "=== R2C1: extract ==="
cd "$R2C1_DIR"
abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py \
  --job stage16n_r2c1_native_restart_100_to_250 |& tee _r2c1_extract.out || true

echo "=== R2C1: compare ==="
cd "$REPO"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_native_restart_against_1000ref.py \
  --restart-metrics "$R2C1_DIR/stage16n_r2c1_native_restart_100_to_250_cycle_metrics.csv" \
  --restart-local-states "$R2C1_DIR/stage16n_r2c1_native_restart_100_to_250_selected_cycle_local_states.csv" \
  --cycles 250 \
  --out-dir "$R2C1_DIR" |& tee "$R2C1_DIR/_r2c1_compare.out" || true

echo "=== R2C2: extract ==="
cd "$R2C2_DIR"
abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py \
  --job stage16n_r2c2_native_restart_250_to_500 |& tee _r2c2_extract.out || true

echo "=== R2C2: compare ==="
cd "$REPO"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_native_restart_against_1000ref.py \
  --restart-metrics "$R2C2_DIR/stage16n_r2c2_native_restart_250_to_500_cycle_metrics.csv" \
  --restart-local-states "$R2C2_DIR/stage16n_r2c2_native_restart_250_to_500_selected_cycle_local_states.csv" \
  --cycles 500 \
  --out-dir "$R2C2_DIR" |& tee "$R2C2_DIR/_r2c2_compare.out" || true

echo
echo "=== Collected summaries ==="
for DIR in "$R2C1_DIR" "$R2C2_DIR"; do
  echo "---- $DIR ----"
  echo "STAGE16N_R2_CASE_STATUS.md:"
  [ -f "$DIR/STAGE16N_R2_CASE_STATUS.md" ] && sed -n '1,200p' "$DIR/STAGE16N_R2_CASE_STATUS.md" || echo "(missing)"
  echo
  echo "comparison summary:"
  [ -f "$DIR/stage16n_native_restart_comparison_summary.csv" ] && sed -n '1,200p' "$DIR/stage16n_native_restart_comparison_summary.csv" || echo "(missing)"
  echo
done

echo "Done."
