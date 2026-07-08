#!/usr/bin/env python3
"""Preflight checks for Stage 15I multi-case real NEML sweep."""

from __future__ import print_function

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
    if os.environ.get("STAGE15I_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15I_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise

from stage15i_case_definitions import (
    CASES,
    DEFAULT_ACTIVE_WORKERS,
    EXTENSION_TARGET_CYCLES,
    HARD_MAX_WORKERS,
    PBS_WALLTIME_SECONDS,
    POINTS_PER_CYCLE,
    PRESERVED_TARGET_CYCLES,
    STOP_GUARD_SECONDS,
)

HERE = Path(__file__).resolve().parent


def fail(errors, message):
    print("[FAIL] " + message)
    errors.append(message)


def ok(message):
    print("[OK] " + message)


def main():
    errors = []
    print("[Stage 15I preflight]")
    print("Python: %s" % platform.python_version())

    if sys.version_info < (3, 8):
        fail(errors, "Python >= 3.8 is required")
    else:
        ok("Python version is acceptable")

    ok("numpy import works: %s" % np.__version__)
    ok("pandas import works: %s" % pd.__version__)
    ok("neml import works: %s" % neml.__file__)
    if "site-packages" not in str(neml.__file__):
        fail(errors, "NEML path does not look like installed real NEML")
    else:
        ok("real NEML import path looks valid")

    if os.environ.get("STAGE15I_ALLOW_FALLBACK_BACKEND"):
        fail(errors, "fallback backend flag is set; Stage 15I must use real NEML")
    else:
        ok("fallback backend is not enabled")

    if POINTS_PER_CYCLE != 40:
        fail(errors, "points_per_cycle must be 40")
    else:
        ok("points_per_cycle = 40")

    names = set()
    for case in CASES:
        name = case["case_name"]
        names.add(name)
        if case["stress_min"] >= case["stress_max"]:
            fail(errors, "stress_min must be less than stress_max for %s" % name)
    if len(names) != len(CASES):
        fail(errors, "case names must be unique")
    else:
        ok("case definitions are valid and unique")

    if sorted(PRESERVED_TARGET_CYCLES) != PRESERVED_TARGET_CYCLES:
        fail(errors, "preserved target cycles must be sorted")
    elif PRESERVED_TARGET_CYCLES[-1] > EXTENSION_TARGET_CYCLES:
        fail(errors, "preserved target cycles must be inside extension target")
    else:
        ok("preserved target cycles sorted and inside extension target")

    if STOP_GUARD_SECONDS >= PBS_WALLTIME_SECONDS:
        fail(errors, "stop guard must be less than PBS walltime")
    else:
        ok("stop guard is less than PBS walltime")

    active_workers = int(os.environ.get("STAGE15I_ACTIVE_WORKERS", str(DEFAULT_ACTIVE_WORKERS)))
    hard_max = int(os.environ.get("STAGE15I_HARD_MAX_WORKERS", str(HARD_MAX_WORKERS)))
    if active_workers > DEFAULT_ACTIVE_WORKERS:
        fail(errors, "default active workers must be <= 24; got %d" % active_workers)
    else:
        ok("active workers <= 24 by default: %d" % active_workers)
    if hard_max > HARD_MAX_WORKERS:
        fail(errors, "hard max active workers must be <= 32; got %d" % hard_max)
    else:
        ok("hard max active workers <= 32: %d" % hard_max)
    if active_workers > hard_max:
        fail(errors, "active workers cannot exceed hard max")

    required_env = ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"]
    for key in required_env:
        value = os.environ.get(key)
        if value in (None, ""):
            print("[WARN] %s not set by caller; run scripts/PBS set it to 1" % key)
        elif value != "1":
            fail(errors, "%s should be 1, got %s" % (key, value))
        else:
            ok("%s=1" % key)

    if "stage15g_real_neml_long_b1_validation_baseline" in str(HERE).lower():
        fail(errors, "Stage 15I output path overlaps Stage 15G")
    else:
        ok("output path does not overwrite Stage 15G")

    for folder_name in ["case_outputs", "smoke_test_outputs", "logs"]:
        folder = HERE / folder_name
        folder.mkdir(exist_ok=True)
        for path in [folder / ".write_test", folder / "checkpoint_write_test.json.tmp"]:
            try:
                path.write_text("ok\n")
                path.unlink()
            except OSError as exc:
                fail(errors, "%s is not writable: %s" % (folder_name, exc))
        ok("%s path writable" % folder_name)

    if errors:
        print("[Stage 15I preflight] FAILED with %d error(s)" % len(errors))
        return 1
    print("[Stage 15I preflight] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
