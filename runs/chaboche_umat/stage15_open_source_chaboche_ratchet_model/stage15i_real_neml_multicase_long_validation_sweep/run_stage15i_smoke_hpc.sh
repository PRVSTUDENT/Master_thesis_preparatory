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
export STAGE15I_ACTIVE_WORKERS=3
export STAGE15I_HARD_MAX_WORKERS=32

rm -rf smoke_test_outputs
mkdir -p smoke_test_outputs logs

{
  echo "[Stage 15I smoke] host=$(hostname)"
  echo "[Stage 15I smoke] python=$(command -v python3 || command -v python)"
  python3 --version 2>/dev/null || python --version
} | tee logs/STAGE15I_SMOKE_LOG.txt

python3 stage15i_preflight_check.py 2>&1 | tee logs/STAGE15I_SMOKE_PREFLIGHT_LOG.txt

python3 stage15i_multicase_long_runner.py \
  --target-cycles 100 \
  --stop-after-seconds 1800 \
  --status-every-seconds 5 \
  --checkpoint-every 50 \
  --output-dir smoke_test_outputs \
  --active-workers 3 \
  --case B1_m150_to_250 \
  --case B1_m150_to_260 \
  --case B2_stress_0_to_300 \
  --resume \
  2>&1 | tee -a logs/STAGE15I_SMOKE_LOG.txt

for case_name in B1_m150_to_250 B1_m150_to_260 B2_stress_0_to_300; do
  test -s "smoke_test_outputs/${case_name}_cycle_summary.csv"
  test -s "smoke_test_outputs/${case_name}_selected_loops.csv"
  test -s "smoke_test_outputs/${case_name}_checkpoint.json"
  test -s "smoke_test_outputs/${case_name}_status.txt"
done
test -s STAGE15I_GLOBAL_STATUS.txt

python3 - <<'PY'
import json
from pathlib import Path
import numpy as np
import pandas as pd

required = [
    "cycle", "strain_mean", "ratcheting_strain", "strain_range",
    "hysteresis_area", "accumulated_inelastic_strain_end", "backstress_norm_end",
]
for path in sorted(Path("smoke_test_outputs").glob("*_cycle_summary.csv")):
    df = pd.read_csv(path)
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise SystemExit(f"{path}: missing columns {missing}")
    numeric = df[required].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric.to_numpy()).all():
        raise SystemExit(f"{path}: contains NaN/inf in required columns")
    if "backend" not in df.columns or set(df["backend"]) != {"real_neml"}:
        raise SystemExit(f"{path}: real NEML backend marker missing")
meta = json.loads(Path("STAGE15I_RUN_METADATA.json").read_text())
if meta.get("backend") != "real_neml":
    raise SystemExit("metadata backend is not real_neml")
print("[Stage 15I smoke] output validation passed")
PY

python3 stage15i_make_reduced_summary.py --input-dir smoke_test_outputs --output STAGE15I_TARGET_CYCLE_VALUES.csv \
  2>&1 | tee -a logs/STAGE15I_SMOKE_LOG.txt

echo "[Stage 15I smoke] passed" | tee -a logs/STAGE15I_SMOKE_LOG.txt
