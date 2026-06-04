#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE16="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
PILOT="$STAGE16/stage16n_1000cycle_pilot"
LOG_DIR="$STAGE16/_logs"
JOB="stage16n_plate_hole_neml_equiv_1000cycles"
ABAQUS_CPUS="${ABAQUS_CPUS:-${PBS_NP:-30}}"
mkdir -p "$LOG_DIR"
echo "[Stage16N] Abaqus CPU request: $ABAQUS_CPUS"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N] generating 1000-cycle pilot deck"
python3 "$STAGE16/prepare_stage16n_neml_plate_with_hole_1000cycles.py" 2>&1 | tee "$LOG_DIR/stage16n_generate_1000cycle_pilot.log"

cd "$PILOT"

if [[ ! -f "${JOB}_datacheck.dat" ]] || ! grep -q "ANALYSIS DATACHECK COMPLETE" "${JOB}_datacheck.dat"; then
    echo "[Stage16N] datacheck"
    abaqus job="${JOB}_datacheck" input="${JOB}.inp" user=stage16n_neml_equivalent_chaboche_umat.for datacheck interactive ask_delete=OFF scratch=. cpus="$ABAQUS_CPUS" mp_mode=mpi \
        2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"
fi

if [[ ! -f "${JOB}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
    echo "[Stage16N] full 1000-cycle pilot"
    abaqus job="$JOB" input="${JOB}.inp" user=stage16n_neml_equivalent_chaboche_umat.for interactive ask_delete=OFF scratch=. cpus="$ABAQUS_CPUS" mp_mode=mpi \
        2>&1 | tee "$LOG_DIR/${JOB}_full.log"
fi

if [[ ! -f "${JOB}_cycle_metrics.csv" ]]; then
    echo "[Stage16N] extraction"
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
        2>&1 | tee "$LOG_DIR/${JOB}_extract.log"
fi

python3 "$STAGE16/stage16n_compare_loop_evolution.py" \
    --cycle-metrics "$PILOT/${JOB}_cycle_metrics.csv" \
    --local-states "$PILOT/${JOB}_selected_cycle_local_states.csv" \
    --out-dir "$PILOT" \
    2>&1 | tee "$LOG_DIR/${JOB}_compare_loop_evolution.log"

echo "[Stage16N] pilot complete"
