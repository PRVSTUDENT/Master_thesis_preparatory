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
export STAGE15G_ACTIVE_WORKERS=1

mkdir -p logs
rm -rf smoke_test_outputs
mkdir -p smoke_test_outputs

{
  echo "[Stage 15G smoke] host=$(hostname)"
  echo "[Stage 15G smoke] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
} | tee logs/STAGE15G_SMOKE_LOG.txt

python3 stage15g_preflight_check.py 2>&1 | tee -a logs/STAGE15G_SMOKE_LOG.txt

python3 stage15g_real_neml_long_b1_runner.py \
  --target-cycles 100 \
  --stop-after-seconds 600 \
  --status-every-seconds 1 \
  --checkpoint-every 50 \
  --output-dir smoke_test_outputs \
  2>&1 | tee -a logs/STAGE15G_SMOKE_LOG.txt

python3 - <<'PY'
from pathlib import Path
import json
import numpy as np
import pandas as pd

out = Path("smoke_test_outputs")
required = [
    out / "B1_long_cycle_summary.csv",
    out / "B1_long_selected_loops.csv",
    out / "B1_long_checkpoint.json",
    out / "B1_long_status.txt",
]
missing = [str(path) for path in required if not path.exists() or path.stat().st_size == 0]
if missing:
    raise SystemExit("Missing smoke outputs: " + ", ".join(missing))
summary = pd.read_csv(out / "B1_long_cycle_summary.csv")
if summary.empty:
    raise SystemExit("Smoke cycle summary is empty")
numeric = ["cycle", "strain_mean", "ratcheting_strain", "strain_range", "hysteresis_area"]
if not np.isfinite(summary[numeric].to_numpy(dtype=float)).all():
    raise SystemExit("NaN/inf in smoke cycle summary")
meta = json.loads(Path("STAGE15G_RUN_METADATA.json").read_text())
if meta.get("backend") != "real_neml" or "neml" not in meta.get("neml_path", "").lower():
    raise SystemExit("Smoke run did not record real NEML backend")
print("Stage 15G smoke rows:", len(summary))
PY

echo "[Stage 15G smoke] PASSED" | tee -a logs/STAGE15G_SMOKE_LOG.txt

