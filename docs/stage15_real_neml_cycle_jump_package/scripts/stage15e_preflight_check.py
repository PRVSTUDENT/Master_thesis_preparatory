#!/usr/bin/env python3
"""Preflight checks for Stage 15E cycle-jump benchmark."""

import os
import platform
import shlex
import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ImportError:
    if os.environ.get("STAGE15E_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15E_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise

from stage15e_cycle_jump_methods import BASELINE_FILES, TARGET_CYCLES, VARIABLES, finite_required


HERE = Path(__file__).resolve().parent
BASELINE_DIR = HERE.parent / "stage15d_real_neml_full_baseline"
CASE_OUTPUTS = BASELINE_DIR / "case_outputs"
REQUIRED_COLUMNS = ["case_name", "cycle", "strain_min", "strain_max", "strain_mean", "strain_range", "ratcheting_strain", "hysteresis_area"]


def fail(message, errors):
    print(f"[FAIL] {message}")
    errors.append(message)


def ok(message):
    print(f"[OK] {message}")


def main():
    errors = []
    print("[Stage 15E preflight]")
    print(f"Python: {platform.python_version()}")

    if sys.version_info < (3, 9):
        fail("Python >= 3.9 is required", errors)
    else:
        ok("Python version is acceptable")

    ok(f"numpy import works: {np.__version__}")
    ok(f"pandas import works: {pd.__version__}")
    try:
        import scipy  # noqa: F401
        ok("scipy import works (not required by current implementation)")
    except Exception as exc:  # pragma: no cover - depends on HPC environment
        print(f"[WARN] scipy import failed but Stage 15E does not require scipy: {exc}")

    max_workers = int(os.environ.get("STAGE15E_MAX_WORKERS", "12"))
    memory_safe = os.environ.get("STAGE15E_MEMORY_SAFE", "1")
    if memory_safe != "1":
        fail("STAGE15E_MEMORY_SAFE must be 1", errors)
    else:
        ok("memory-safe mode enabled")
    if max_workers > 12:
        fail(f"STAGE15E_MAX_WORKERS={max_workers} is greater than 12", errors)
    else:
        ok(f"STAGE15E_MAX_WORKERS={max_workers}")

    for summary in ("STAGE15D_BASELINE_RUN_SUMMARY.csv", "STAGE15D_BASELINE_MASTER_SUMMARY.md"):
        path = BASELINE_DIR / summary
        if path.exists():
            ok(f"baseline file exists: {path}")
        else:
            fail(f"missing baseline file: {path}", errors)

    for case_name, file_name in BASELINE_FILES.items():
        path = CASE_OUTPUTS / file_name
        if not path.exists():
            fail(f"missing cycle summary for {case_name}: {path}", errors)
            continue
        ok(f"cycle summary exists for {case_name}")
        df = pd.read_csv(path)
        missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
        if missing:
            fail(f"{case_name} missing required columns: {missing}", errors)
            continue
        ok(f"{case_name} required columns exist")
        for column in VARIABLES + ["cycle"]:
            df[column] = pd.to_numeric(df[column], errors="coerce")
        if not finite_required(df, VARIABLES + ["cycle"]):
            fail(f"{case_name} has NaN/inf in required numeric columns", errors)
        else:
            ok(f"{case_name} numeric columns are finite")
        max_cycle = int(df["cycle"].max())
        required_max = 250000 if case_name.startswith("B1_") else 180000
        if max_cycle < required_max:
            fail(f"{case_name} max cycle {max_cycle} < required {required_max}", errors)
        else:
            ok(f"{case_name} max cycle {max_cycle} covers required target")
        missing_targets = [cycle for cycle in TARGET_CYCLES[case_name] if cycle > max_cycle or df.loc[df["cycle"] == cycle].empty]
        if missing_targets:
            fail(f"{case_name} missing target cycles: {missing_targets}", errors)
        else:
            ok(f"{case_name} selected target cycles are available")

    try:
        test_path = HERE / ".stage15e_write_test"
        test_path.write_text("ok\n")
        test_path.unlink()
        ok("output folder is writable")
    except OSError as exc:
        fail(f"output folder is not writable: {exc}", errors)

    if errors:
        print(f"[Stage 15E preflight] FAILED with {len(errors)} error(s)")
        return 1
    print("[Stage 15E preflight] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
