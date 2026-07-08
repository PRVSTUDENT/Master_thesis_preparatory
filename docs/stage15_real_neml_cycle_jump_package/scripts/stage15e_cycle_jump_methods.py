#!/usr/bin/env python3
"""Cycle-jump prediction helpers for Stage 15E."""

import math
from collections import namedtuple

import numpy as np
import pandas as pd


TINY = 1.0e-12

PRIMARY_VARIABLES = ["strain_mean", "ratcheting_strain"]
SECONDARY_VARIABLES = ["strain_max", "strain_min", "strain_range", "hysteresis_area"]
VARIABLES = PRIMARY_VARIABLES + SECONDARY_VARIABLES

METHODS = [
    "linear_last_2",
    "linear_last_5",
    "linear_last_10",
    "linear_last_20",
    "least_squares_last_20",
    "least_squares_last_50",
    "least_squares_last_100",
]

BASE_CYCLES = [10, 20, 50, 100, 500, 1000, 5000, 10000]

TARGET_CYCLES = {
    "B1_stress_m150_to_250": [100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 250000],
    "B2_stress_0_to_300": [100, 500, 1000, 5000, 10000, 50000, 100000, 150000, 180000],
}

BASELINE_FILES = {
    "B1_stress_m150_to_250": "B1_stress_m150_to_250_cycle_summary.csv",
    "B2_stress_0_to_300": "B2_stress_0_to_300_cycle_summary.csv",
}


Prediction = namedtuple("Prediction", ["slope", "intercept", "base_value", "predicted_value", "effective_window"])


def method_window(method):
    try:
        return int(method.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Unsupported method name: {method}") from exc


def load_cycle_summary(path):
    df = pd.read_csv(path)
    df["cycle"] = pd.to_numeric(df["cycle"], errors="raise").astype(int)
    for column in VARIABLES + ["stress_min", "stress_max"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="raise")
    return df.sort_values("cycle").reset_index(drop=True)


def finite_required(df, columns):
    values = df[list(columns)].to_numpy(dtype=float)
    return bool(np.isfinite(values).all())


def row_at_cycle(df, cycle):
    rows = df.loc[df["cycle"] == int(cycle)]
    if rows.empty:
        raise KeyError(f"Cycle {cycle} not found")
    return rows.iloc[0]


def _window(df, base_cycle, requested_window):
    subset = df.loc[df["cycle"] <= int(base_cycle)].tail(int(requested_window))
    if len(subset) < 2:
        raise ValueError(f"Need at least two cycles at base {base_cycle}")
    return subset


def estimate_prediction(df, variable, method, base_cycle, target_cycle):
    if variable not in df.columns:
        raise KeyError(f"Missing variable {variable}")
    if method not in METHODS:
        raise ValueError(f"Unsupported method {method}")

    requested_window = method_window(method)
    sample = _window(df, base_cycle, requested_window)
    x = sample["cycle"].to_numpy(dtype=float)
    y = sample[variable].to_numpy(dtype=float)

    if method.startswith("linear_last_"):
        slope = (y[-1] - y[0]) / max(x[-1] - x[0], TINY)
        intercept = y[-1] - slope * x[-1]
    elif method.startswith("least_squares_last_"):
        slope, intercept = np.polyfit(x, y, 1)
    else:
        raise ValueError(f"Unsupported method {method}")

    base_row = row_at_cycle(df, base_cycle)
    base_value = float(base_row[variable])
    predicted_value = base_value + float(slope) * (int(target_cycle) - int(base_cycle))
    return Prediction(float(slope), float(intercept), base_value, float(predicted_value), int(len(sample)))


def error_metrics(predicted, reference, strain_range_reference):
    absolute = abs(float(predicted) - float(reference))
    relative = 100.0 * absolute / max(abs(float(reference)), TINY)
    normalized = 100.0 * absolute / max(abs(float(strain_range_reference)), TINY)
    return {
        "absolute_error": absolute,
        "relative_error_percent": relative,
        "normalized_error_percent": normalized,
    }


def drift_direction_ok(base_value, predicted, reference):
    predicted_drift = float(predicted) - float(base_value)
    reference_drift = float(reference) - float(base_value)
    if abs(reference_drift) <= TINY and abs(predicted_drift) <= TINY:
        return True
    if abs(reference_drift) <= TINY:
        return abs(predicted_drift) <= TINY
    return math.copysign(1.0, predicted_drift) == math.copysign(1.0, reference_drift)
