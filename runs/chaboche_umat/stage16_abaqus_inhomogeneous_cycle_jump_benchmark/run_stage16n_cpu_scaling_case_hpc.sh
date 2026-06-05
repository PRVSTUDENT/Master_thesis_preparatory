#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE16="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
LOG_DIR="$STAGE16/_logs"
BENCHMARK_CYCLES="${BENCHMARK_CYCLES:-50}"
ABAQUS_CPUS="${ABAQUS_CPUS:-${PBS_NP:-8}}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"

RUN_ROOT="$STAGE16/stage16n_cpu_scaling_benchmark/cycles_$(printf '%04d' "$BENCHMARK_CYCLES")"
BASE_JOB="stage16n_scaling_$(printf '%04d' "$BENCHMARK_CYCLES")cycles"
JOB="${BASE_JOB}_${ABAQUS_CPUS}cpu"

mkdir -p "$LOG_DIR"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N scaling] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N scaling] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N scaling] cycles: $BENCHMARK_CYCLES"
echo "[Stage16N scaling] Abaqus CPU request: $ABAQUS_CPUS"
echo "[Stage16N scaling] Abaqus mp_mode: $ABAQUS_MP_MODE"

python3 "$STAGE16/stage16n_make_scaling_benchmark_deck.py" --cycles "$BENCHMARK_CYCLES"
cd "$RUN_ROOT"

cp "${BASE_JOB}.inp" "${JOB}.inp"

START_EPOCH="$(date +%s)"
abaqus job="$JOB" input="${JOB}.inp" user=stage16n_neml_equivalent_chaboche_umat.for interactive ask_delete=OFF scratch=. cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${JOB}.log"
END_EPOCH="$(date +%s)"
WALL_SECONDS="$((END_EPOCH - START_EPOCH))"

PARALLEL_LINE="$(grep -m 1 -A1 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" | tail -n 1 | sed 's/^[[:space:]]*//')"
COMPLETED="$(grep -c "THE ANALYSIS HAS COMPLETED" "${JOB}.dat" || true)"

cat > "${JOB}_scaling_summary.csv" <<EOF
job,cycles,abaqus_cpus,mp_mode,wall_seconds,analysis_completed,parallelism
${JOB},${BENCHMARK_CYCLES},${ABAQUS_CPUS},${ABAQUS_MP_MODE},${WALL_SECONDS},${COMPLETED},"${PARALLEL_LINE}"
EOF

cat "${JOB}_scaling_summary.csv"
echo "[Stage16N scaling] end: $(date '+%Y-%m-%d %H:%M:%S')"
