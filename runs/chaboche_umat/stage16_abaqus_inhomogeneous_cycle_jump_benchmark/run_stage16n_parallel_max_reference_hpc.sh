#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}"
STAGE16="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark"
PILOT="$STAGE16/stage16n_1000cycle_pilot"
RUN_DIR="$STAGE16/stage16n_parallel_max_reference"
LOG_DIR="$STAGE16/_logs"

SOURCE_JOB="stage16n_plate_hole_neml_equiv_1000cycles"
JOB="stage16n_parallel_max_reference_1000cycles"
ABAQUS_CPUS="${ABAQUS_CPUS:-${PBS_NP:-30}}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"

mkdir -p "$RUN_DIR" "$LOG_DIR"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N] parallel max reference"
echo "[Stage16N] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N] Abaqus CPU request: $ABAQUS_CPUS"
echo "[Stage16N] Abaqus mp_mode: $ABAQUS_MP_MODE"

if [[ ! -f "$PILOT/${SOURCE_JOB}.inp" ]]; then
    echo "[Stage16N] missing source deck; regenerating pilot deck"
    python3 "$STAGE16/prepare_stage16n_neml_plate_with_hole_1000cycles.py"
fi

cp "$PILOT/${SOURCE_JOB}.inp" "$RUN_DIR/${JOB}.inp"
cp "$PILOT/stage16n_neml_equivalent_chaboche_umat.for" "$RUN_DIR/stage16n_neml_equivalent_chaboche_umat.for"
cp "$STAGE16/stage16n_extract_hysteresis_and_local_states.py" "$RUN_DIR/stage16n_extract_hysteresis_and_local_states.py"

cat > "$RUN_DIR/STAGE16N_PARALLEL_MAX_REFERENCE_MANIFEST.md" <<EOF
# Stage 16N Parallel Max Reference Manifest

- Source deck: \`$PILOT/${SOURCE_JOB}.inp\`
- Run job: \`$JOB\`
- PBS job: \`${PBS_JOBID:-manual}\`
- Abaqus CPUs requested: \`$ABAQUS_CPUS\`
- Abaqus mp_mode: \`$ABAQUS_MP_MODE\`
- Purpose: find the maximum number of full non-jump cycles obtainable in one walltime-limited parallel Abaqus run.
- Validation check: inspect \`${JOB}.msg\` for solver lines reporting more than \`1 MPI RANK x 1 THREAD\`.
EOF

cd "$RUN_DIR"

echo "[Stage16N] datacheck"
abaqus job="${JOB}_datacheck" input="${JOB}.inp" user=stage16n_neml_equivalent_chaboche_umat.for datacheck interactive ask_delete=OFF scratch=. cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${JOB}_datacheck.log"

echo "[Stage16N] full max-cycle reference"
set +e
abaqus job="$JOB" input="${JOB}.inp" user=stage16n_neml_equivalent_chaboche_umat.for interactive ask_delete=OFF scratch=. cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \
    2>&1 | tee "$LOG_DIR/${JOB}_full.log"
ABAQUS_STATUS=${PIPESTATUS[0]}
set -e

echo "[Stage16N] Abaqus exit status: $ABAQUS_STATUS"

echo "[Stage16N] solver parallelism check"
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" | tee "$LOG_DIR/${JOB}_parallelism_check.log" || true

echo "[Stage16N] completed-cycle check"
python3 - "$JOB.sta" "$RUN_DIR/STAGE16N_PARALLEL_MAX_REFERENCE_STATUS.md" <<'PY'
from __future__ import print_function
import re
import sys
from pathlib import Path

sta = Path(sys.argv[1])
out = Path(sys.argv[2])
completed = []
partial = None
if sta.exists():
    for line in sta.read_text(errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 9 and parts[0].isdigit() and parts[1].isdigit():
            step = int(parts[0])
            inc = int(parts[1])
            fraction = None
            try:
                fraction = float(parts[7])
            except Exception:
                pass
            if fraction is not None:
                if fraction >= 0.999:
                    completed.append(step)
                else:
                    partial = step
max_completed = max(completed) if completed else 0
text = [
    "# Stage 16N Parallel Max Reference Status",
    "",
    "- Status generated after Abaqus run.",
    "- Max completed non-jump cycle: `%d`" % max_completed,
    "- Last partial cycle: `%s`" % (partial if partial is not None and partial > max_completed else "none"),
    "",
    "Use this max completed cycle count as the full-reference baseline limit for later cycle-jump comparisons.",
]
out.write_text("\n".join(text) + "\n")
print("max_completed_cycle=%d" % max_completed)
print("wrote=%s" % out)
PY

if [[ -f "${JOB}.odb" ]]; then
    echo "[Stage16N] extraction"
    abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \
        2>&1 | tee "$LOG_DIR/${JOB}_extract.log" || true
fi

echo "[Stage16N] end: $(date '+%Y-%m-%d %H:%M:%S')"
exit "$ABAQUS_STATUS"
