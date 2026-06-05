#!/usr/bin/env bash
set -euo pipefail

BENCHMARK_CYCLES="${BENCHMARK_CYCLES:-50}"
CPU_COUNTS="${CPU_COUNTS:-4 8 12 16 20 30}"
QUEUE="${QUEUE:-entry_teachingq}"
MEM_PER_JOB="${MEM_PER_JOB:-40gb}"
WALLTIME="${WALLTIME:-03:00:00}"
REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE16="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
SUBMIT_DIR="$STAGE16/stage16n_cpu_scaling_benchmark/submits"

mkdir -p "$SUBMIT_DIR"

for cpus in $CPU_COUNTS; do
    pbs="$SUBMIT_DIR/submit_stage16n_scaling_${BENCHMARK_CYCLES}cycles_${cpus}cpu.pbs"
    cat > "$pbs" <<EOF
#!/bin/bash
#PBS -N s16n_scl_${cpus}c
#PBS -q ${QUEUE}
#PBS -l select=1:ncpus=${cpus}:mpiprocs=1:ompthreads=${cpus}:mem=${MEM_PER_JOB}
#PBS -l walltime=${WALLTIME}
#PBS -j oe

set -euo pipefail
cd "\$PBS_O_WORKDIR"
export REPO_ROOT="$REPO_ROOT"
export BENCHMARK_CYCLES="$BENCHMARK_CYCLES"
export ABAQUS_CPUS="$cpus"
export ABAQUS_MP_MODE="threads"

bash runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/run_stage16n_cpu_scaling_case_hpc.sh
EOF
    echo "Submitting $pbs"
    qsub "$pbs"
done
