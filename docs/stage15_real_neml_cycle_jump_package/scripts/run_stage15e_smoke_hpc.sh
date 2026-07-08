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
export STAGE15E_MEMORY_SAFE=1
export STAGE15E_MAX_WORKERS="${STAGE15E_MAX_WORKERS:-12}"

mkdir -p smoke_test_outputs logs

{
  echo "[Stage 15E smoke] host=$(hostname)"
  echo "[Stage 15E smoke] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
} | tee logs/STAGE15E_SMOKE_TEST_LOG.txt

python3 stage15e_preflight_check.py 2>&1 | tee -a logs/STAGE15E_SMOKE_TEST_LOG.txt

rm -rf smoke_test_outputs
mkdir -p smoke_test_outputs

python3 stage15e_real_neml_cycle_jump_controller.py \
  --output-dir smoke_test_outputs \
  --cases B1_stress_m150_to_250 \
  --base-cycles 10,50 \
  --target-cycles 100,500,1000 \
  --methods linear_last_2,least_squares_last_20 \
  2>&1 | tee -a logs/STAGE15E_SMOKE_TEST_LOG.txt

python3 - <<'PY'
from pathlib import Path
import numpy as np
import pandas as pd

out = Path("smoke_test_outputs")
matrix = out / "STAGE15E_CYCLE_JUMP_MATRIX.csv"
acceptance = out / "STAGE15E_ACCEPTANCE_TABLE.csv"
if not matrix.exists() or not acceptance.exists():
    raise SystemExit("Smoke CSV outputs were not created")
df = pd.read_csv(matrix)
if df.empty:
    raise SystemExit("Smoke matrix has no rows")
numeric = [
    "predicted_value",
    "reference_value",
    "absolute_error",
    "relative_error_percent",
    "normalized_error_percent",
]
if not np.isfinite(df[numeric].to_numpy(dtype=float)).all():
    raise SystemExit("Smoke matrix contains NaN or inf")
required_plots = [
    out / "plots" / "B1_error_vs_target.svg",
    out / "plots" / "B1_mean_strain_prediction.svg",
    out / "plots" / "B1_ratcheting_prediction.svg",
    out / "plots" / "method_comparison_heatmap.svg",
]
missing = [str(path) for path in required_plots if not path.exists() or path.stat().st_size == 0]
if missing:
    raise SystemExit("Missing smoke SVG plots: " + ", ".join(missing))
print(f"Smoke rows: {len(df)}")
PY

echo "[Stage 15E smoke] PASSED" | tee -a logs/STAGE15E_SMOKE_TEST_LOG.txt
