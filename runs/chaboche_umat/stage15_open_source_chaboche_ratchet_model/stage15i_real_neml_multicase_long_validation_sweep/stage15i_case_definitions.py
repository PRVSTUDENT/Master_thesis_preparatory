#!/usr/bin/env python3
"""Case and run definitions for Stage 15I."""

P2_MODEL = {
    "name": "P2_three_backstress_screen",
    "E": 200000.0,
    "nu": 0.3,
    "yield_stress": 100.0,
    "Q": 50.0,
    "b": 5.0,
    "C": [80000.0, 14000.0, 3333.0],
    "gamma": [900.0, 1500.0, 1.0],
    "A": [0.0, 0.0, 0.0],
    "a": [1.0, 1.0, 1.0],
}

POINTS_PER_CYCLE = 40
PRIMARY_TARGET_CYCLES = 1500000
EXTENSION_TARGET_CYCLES = 2000000
MINIMUM_USEFUL_TARGET_CYCLES = 500000
PBS_WALLTIME_SECONDS = 20 * 3600
STOP_GUARD_SECONDS = 19 * 3600 + 40 * 60
DEFAULT_ACTIVE_WORKERS = 24
HARD_MAX_WORKERS = 32

PRESERVED_TARGET_CYCLES = [
    1000,
    5000,
    10000,
    15000,
    50000,
    100000,
    106250,
    200000,
    250000,
    279725,
    300000,
    500000,
    750000,
    1000000,
    1250000,
    1500000,
    1750000,
    2000000,
]

SELECTED_LOOP_CYCLES = [
    1,
    2,
    5,
    10,
    20,
    50,
    100,
    500,
    1000,
    5000,
    10000,
    15000,
    50000,
    100000,
    106250,
    200000,
    250000,
    279725,
    300000,
    500000,
    750000,
    1000000,
    1250000,
    1500000,
    1750000,
    2000000,
]

CASES = [
    {"case_name": "B1_m150_to_240", "stress_min": -150.0, "stress_max": 240.0, "group": "primary_b1"},
    {"case_name": "B1_m150_to_250", "stress_min": -150.0, "stress_max": 250.0, "group": "primary_b1"},
    {"case_name": "B1_m150_to_260", "stress_min": -150.0, "stress_max": 260.0, "group": "primary_b1"},
    {"case_name": "B1_m140_to_250", "stress_min": -140.0, "stress_max": 250.0, "group": "primary_b1"},
    {"case_name": "B1_m160_to_250", "stress_min": -160.0, "stress_max": 250.0, "group": "primary_b1"},
    {"case_name": "B1_mean50_amp180", "stress_min": -130.0, "stress_max": 230.0, "group": "primary_b1"},
    {"case_name": "B1_mean50_amp220", "stress_min": -170.0, "stress_max": 270.0, "group": "primary_b1"},
    {"case_name": "B1_mean70_amp200", "stress_min": -130.0, "stress_max": 270.0, "group": "primary_b1"},
    {"case_name": "B1_m180_to_280", "stress_min": -180.0, "stress_max": 280.0, "group": "aggressive_b1"},
    {"case_name": "B1_m200_to_300", "stress_min": -200.0, "stress_max": 300.0, "group": "aggressive_b1"},
    {"case_name": "B2_stress_0_to_300", "stress_min": 0.0, "stress_max": 300.0, "group": "diagnostic_b2"},
    {"case_name": "B2_0_to_320", "stress_min": 0.0, "stress_max": 320.0, "group": "diagnostic_b2"},
    {"case_name": "B2_m20_to_300", "stress_min": -20.0, "stress_max": 300.0, "group": "diagnostic_b2"},
    {"case_name": "B2_10_to_310", "stress_min": 10.0, "stress_max": 310.0, "group": "diagnostic_b2"},
]


def case_by_name(name):
    for case in CASES:
        if case["case_name"] == name:
            return dict(case)
    raise KeyError(name)
