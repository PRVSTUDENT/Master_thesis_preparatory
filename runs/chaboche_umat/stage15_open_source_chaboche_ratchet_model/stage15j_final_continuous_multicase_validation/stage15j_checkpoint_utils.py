#!/usr/bin/env python3
"""Atomic checkpoint helpers for Stage 15J."""

import json
import os
import time
from pathlib import Path


def _array_to_list(value):
    try:
        return [float(x) for x in value]
    except TypeError:
        return value


def checkpoint_payload(case_name, cycle, target_cycle, driver, elapsed, first_mean, last_row, status, metadata):
    return {
        "case_name": case_name,
        "cycle": int(cycle),
        "target_cycle": int(target_cycle),
        "status": status,
        "elapsed_seconds": float(elapsed),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "first_mean": first_mean,
        "last_row": last_row,
        "real_neml_metadata": metadata,
        "driver_state": {
            "stress": _array_to_list(driver.stress_int[-1]),
            "strain": _array_to_list(driver.strain_int[-1]),
            "history": _array_to_list(driver.stored_int[-1]),
        },
    }


def atomic_write_json(path, payload):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(str(tmp), str(path))


def read_json(path):
    with Path(path).open() as handle:
        return json.load(handle)

