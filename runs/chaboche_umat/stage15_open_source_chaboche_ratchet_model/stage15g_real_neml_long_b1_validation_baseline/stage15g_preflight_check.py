#!/usr/bin/env python3
"""Preflight checks for Stage 15G long B1 real NEML run."""

import os
import platform
import shlex
import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    import neml
except ImportError:
    if os.environ.get("STAGE15G_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15G_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise


HERE = Path(__file__).resolve().parent
PRESERVE_CYCLES = [1000, 5000, 10000, 15000, 50000, 100000, 106250, 200000, 250000, 279725, 300000, 500000, 750000, 1000000, 1250000, 1500000, 1750000, 2000000]
TARGET_CYCLES = 2000000
POINTS_PER_CYCLE = 40
STOP_GUARD_SECONDS = 23 * 3600 + 35 * 60
PBS_WALLTIME_SECONDS = 23 * 3600 + 55 * 60


def fail(errors, message):
    print("[FAIL] " + message)
    errors.append(message)


def ok(message):
    print("[OK] " + message)


def main():
    errors = []
    print("[Stage 15G preflight]")
    print("Python: %s" % platform.python_version())

    if sys.version_info < (3, 6):
        fail(errors, "Python >= 3.6 is required")
    else:
        ok("Python version is acceptable")
    ok("numpy import works: %s" % np.__version__)
    ok("pandas import works: %s" % pd.__version__)
    ok("neml import works: %s" % neml.__file__)
    if "site-packages" not in str(neml.__file__):
        fail(errors, "NEML path does not look like installed real NEML")
    else:
        ok("real NEML import path looks valid")

    if POINTS_PER_CYCLE != 40:
        fail(errors, "points_per_cycle must be 40")
    else:
        ok("points_per_cycle = 40")
    if sorted(PRESERVE_CYCLES) != PRESERVE_CYCLES or PRESERVE_CYCLES[-1] > TARGET_CYCLES:
        fail(errors, "preserved target cycles must be sorted and inside target_cycles")
    else:
        ok("preserved target cycles sorted and inside target")
    if STOP_GUARD_SECONDS >= PBS_WALLTIME_SECONDS:
        fail(errors, "stop guard must be less than PBS walltime")
    else:
        ok("stop guard is less than PBS walltime")
    active_workers = int(os.environ.get("STAGE15G_ACTIVE_WORKERS", "1"))
    if active_workers != 1:
        fail(errors, "STAGE15G_ACTIVE_WORKERS must be 1")
    else:
        ok("active worker count = 1")

    required_env = ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"]
    for key in required_env:
        value = os.environ.get(key)
        if value in (None, ""):
            print("[WARN] %s not set by caller; run scripts/PBS set it to 1" % key)
        elif value != "1":
            fail(errors, "%s should be 1, got %s" % (key, value))
        else:
            ok("%s=1" % key)

    out = HERE / "case_outputs"
    out.mkdir(exist_ok=True)
    for path in [out / ".write_test", out / "B1_long_checkpoint.json.tmp"]:
        try:
            path.write_text("ok\n")
            path.unlink()
        except OSError as exc:
            fail(errors, "output/checkpoint path not writable: %s" % exc)
    ok("output and checkpoint paths writable")

    if errors:
        print("[Stage 15G preflight] FAILED with %d error(s)" % len(errors))
        return 1
    print("[Stage 15G preflight] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

