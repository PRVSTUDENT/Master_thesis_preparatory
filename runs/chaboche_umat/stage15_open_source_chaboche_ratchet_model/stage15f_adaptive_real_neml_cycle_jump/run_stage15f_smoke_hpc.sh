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

mkdir -p logs
python3 stage15f_correct_stage15e_ranking.py | tee logs/STAGE15F_SMOKE_LOG.txt
python3 stage15f_adaptive_controller.py | tee -a logs/STAGE15F_SMOKE_LOG.txt

python3 - <<'PY'
from pathlib import Path
import numpy as np
import pandas as pd

required = [
    "STAGE15F_ADAPTIVE_JUMP_ROUTES.csv",
    "STAGE15F_ADAPTIVE_JUMP_ERRORS.csv",
    "STAGE15F_ACCEPTED_ROUTE_SUMMARY.csv",
    "STAGE15F_MASTER_SUMMARY.md",
]
for name in required:
    path = Path(name)
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit("missing output: " + name)
routes = pd.read_csv("STAGE15F_ADAPTIVE_JUMP_ROUTES.csv")
summary = pd.read_csv("STAGE15F_ACCEPTED_ROUTE_SUMMARY.csv")
if routes.empty or summary.empty:
    raise SystemExit("empty Stage 15F outputs")
numeric = ["predicted_strain_mean", "predicted_ratcheting_strain", "predicted_strain_max", "max_normalized_error_percent"]
if not np.isfinite(routes[numeric].to_numpy(dtype=float)).all():
    raise SystemExit("NaN/inf in Stage 15F routes")
for name in ["B1_adaptive_route_prediction.svg", "B1_error_vs_jump_size.svg", "B1_accepted_jump_map.svg"]:
    path = Path("plots") / name
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit("missing plot: " + name)
print("Stage 15F smoke rows:", len(routes))
PY

echo "[Stage 15F smoke] PASSED" | tee -a logs/STAGE15F_SMOKE_LOG.txt

