#!/usr/bin/env python3
"""Atomic checkpoint helpers for Stage 15G."""

import json
import os
import time


def atomic_write_json(path, payload):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)


def read_json(path):
    with open(path) as handle:
        return json.load(handle)


def vector(values):
    return [float(v) for v in values]


def checkpoint_payload(case_name, cycle, target_cycle, driver, elapsed, first_mean, last_row, status):
    return {
        "case_name": case_name,
        "cycle": int(cycle),
        "target_cycle": int(target_cycle),
        "elapsed_seconds": float(elapsed),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "first_mean": None if first_mean is None else float(first_mean),
        "status": status,
        "last_row": last_row,
        "driver_state": {
            "stress": vector(driver.stress_int[-1]),
            "strain": vector(driver.strain_int[-1]),
            "history": vector(driver.stored_int[-1]),
        },
    }

