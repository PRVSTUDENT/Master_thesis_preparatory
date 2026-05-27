#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

set +u
if [ -f /etc/profile ]; then
  source /etc/profile
fi
if command -v module >/dev/null 2>&1; then
  module purge || true
  module load python/gcc/11.4.0/3.11.7 || true
fi
set -u
hash -r

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

mkdir -p logs smoke_test_outputs
rm -rf smoke_test_outputs
mkdir -p smoke_test_outputs logs

{
  echo "[Stage 15J smoke] host=$(hostname)"
  echo "[Stage 15J smoke] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
} | tee logs/STAGE15J_SMOKE_LOG.txt

export STAGE15J_ACTIVE_WORKERS=40
python3 stage15j_preflight_check.py 2>&1 | tee logs/STAGE15J_SMOKE_PREFLIGHT_LOG.txt

python3 stage15j_continuous_multicase_runner.py \
  --extension-target-cycles 100 \
  --primary-target-cycles 100 \
  --stop-after-seconds 1800 \
  --status-every-seconds 1 \
  --checkpoint-every 25 \
  --output-dir smoke_test_outputs \
  --active-workers 4 \
  --case B1_grid_mean50_amp200 \
  --case B1_grid_mean30_amp180 \
  --case B1_aggr_m100_amp260 \
  --case B2_0_to_300 \
  2>&1 | tee -a logs/STAGE15J_SMOKE_LOG.txt

python3 - <<'PY'
import csv
import json
import math
from pathlib import Path

cases = [
    "B1_grid_mean50_amp200",
    "B1_grid_mean30_amp180",
    "B1_aggr_m100_amp260",
    "B2_0_to_300",
]
base = Path("smoke_test_outputs")
required_suffixes = [
    "_target_values.csv",
    "_reduced_cycle_summary.csv",
    "_selected_loops.csv",
    "_status.txt",
    "_checkpoint.json",
]
numeric_columns = [
    "cycle",
    "stress_min",
    "stress_max",
    "strain_min",
    "strain_max",
    "strain_mean",
    "ratcheting_strain",
    "accumulated_inelastic_strain_end",
    "backstress_norm_end",
]
for case in cases:
    for suffix in required_suffixes:
        path = base / f"{case}{suffix}"
        if not path.exists() or path.stat().st_size == 0:
            raise SystemExit(f"missing or empty {path}")
    rows = list(csv.DictReader((base / f"{case}_reduced_cycle_summary.csv").open(newline="")))
    if not rows:
        raise SystemExit(f"no reduced rows for {case}")
    for row in rows:
        if row.get("backend") != "real_neml":
            raise SystemExit(f"backend not real_neml for {case}")
        for column in numeric_columns:
            value = float(row[column])
            if math.isnan(value) or math.isinf(value):
                raise SystemExit(f"{case} {column} has NaN/inf")
    checkpoint = json.loads((base / f"{case}_checkpoint.json").read_text())
    if checkpoint.get("real_neml_metadata", {}).get("backend") != "real_neml":
        raise SystemExit(f"checkpoint backend not real_neml for {case}")
    if checkpoint.get("real_neml_metadata", {}).get("chunk_relaunch") is not False:
        raise SystemExit(f"checkpoint chunk flag wrong for {case}")

if not Path("STAGE15J_GLOBAL_STATUS.txt").exists():
    raise SystemExit("missing STAGE15J_GLOBAL_STATUS.txt")
print("[Stage 15J smoke] output validation passed")
PY

echo "[Stage 15J smoke] passed" | tee -a logs/STAGE15J_SMOKE_LOG.txt

