#!/usr/bin/env python3
"""Preflight checks for Stage 15J final continuous multicase validation."""

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
    if os.environ.get("STAGE15J_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15J_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise

from stage15j_case_definitions import (
    CASES,
    DEFAULT_ACTIVE_WORKERS,
    EXTENSION_TARGET_CYCLES,
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


def check_writable(errors, folder_name):
    folder = HERE / folder_name
    folder.mkdir(exist_ok=True)
    for name in [".write_test", "checkpoint_write_test.json.tmp"]:
        path = folder / name
        try:
            path.write_text("ok\n")
            path.unlink()
        except OSError as exc:
            fail(errors, "%s is not writable: %s" % (folder_name, exc))
            return
    ok("%s path writable" % folder_name)


def main():
    errors = []
    print("[Stage 15J preflight]")
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

    if os.environ.get("STAGE15J_ALLOW_FALLBACK_BACKEND"):
        fail(errors, "fallback backend flag is set; Stage 15J must use real NEML")
    else:
        ok("fallback backend is not enabled")

    check_writable(errors, ".")
    check_writable(errors, "case_outputs")
    check_writable(errors, "smoke_test_outputs")
    check_writable(errors, "logs")

    if len(CASES) != 40:
        fail(errors, "exactly 40 cases are required; got %d" % len(CASES))
    else:
        ok("exactly 40 cases defined")

    names = set()
    for case in CASES:
        if case["case_name"] in names:
            fail(errors, "duplicate case name: %s" % case["case_name"])
        names.add(case["case_name"])
        if case["stress_min"] >= case["stress_max"]:
            fail(errors, "stress_min must be less than stress_max for %s" % case["case_name"])
    ok("case stress ranges checked")

    if POINTS_PER_CYCLE != 40:
        fail(errors, "points_per_cycle must be 40")
    else:
        ok("points_per_cycle = 40")

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

    active_workers = int(os.environ.get("STAGE15J_ACTIVE_WORKERS", str(DEFAULT_ACTIVE_WORKERS)))
    if active_workers != 40:
        fail(errors, "STAGE15J_ACTIVE_WORKERS must be 40; got %d" % active_workers)
    else:
        ok("STAGE15J_ACTIVE_WORKERS=40")

    for key in ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
        value = os.environ.get(key)
        if value != "1":
            fail(errors, "%s must be 1; got %s" % (key, value))
        else:
            ok("%s=1" % key)

    here_lower = str(HERE).lower()
    if "stage15g_real_neml_long_b1_validation_baseline" in here_lower or "stage15i_real_neml_multicase_long_validation_sweep" in here_lower:
        fail(errors, "Stage 15J output path overlaps Stage 15G or Stage 15I")
    else:
        ok("output path does not overwrite Stage 15G or Stage 15I")

    if errors:
        print("[Stage 15J preflight] FAILED with %d error(s)" % len(errors))
        return 1
    print("[Stage 15J preflight] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
