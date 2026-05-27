#!/usr/bin/env python3
"""Case and run definitions for Stage 15J."""

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
DEFAULT_ACTIVE_WORKERS = 40
HARD_MAX_WORKERS = 40

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


def _case(case_name, group, stress_min, stress_max, mean_stress=None, stress_amplitude=None):
    return {
        "case_name": case_name,
        "group": group,
        "stress_min": float(stress_min),
        "stress_max": float(stress_max),
        "mean_stress": mean_stress,
        "stress_amplitude": stress_amplitude,
    }


CASES = []

for mean in [30, 40, 50, 60, 70]:
    for amplitude in [180, 190, 200, 210, 220]:
        CASES.append(
            _case(
                "B1_grid_mean%d_amp%d" % (mean, amplitude),
                "b1_transferability_grid",
                mean - amplitude,
                mean + amplitude,
                mean,
                amplitude,
            )
        )

CASES.extend([
    _case("B1_aggr_m80_amp220", "aggressive_b1", -140, 300, 80, 220),
    _case("B1_aggr_m80_amp240", "aggressive_b1", -160, 320, 80, 240),
    _case("B1_aggr_m80_amp260", "aggressive_b1", -180, 340, 80, 260),
    _case("B1_aggr_m100_amp220", "aggressive_b1", -120, 320, 100, 220),
    _case("B1_aggr_m100_amp240", "aggressive_b1", -140, 340, 100, 240),
    _case("B1_aggr_m100_amp260", "aggressive_b1", -160, 360, 100, 260),
    _case("B1_aggr_m50_amp240", "aggressive_b1", -190, 290, 50, 240),
    _case("B1_aggr_m50_amp260", "aggressive_b1", -210, 310, 50, 260),
    _case("B1_aggr_m70_amp240", "aggressive_b1", -170, 310, 70, 240),
    _case("B1_aggr_m70_amp260", "aggressive_b1", -190, 330, 70, 260),
])

CASES.extend([
    _case("B2_0_to_280", "diagnostic_b2", 0, 280),
    _case("B2_0_to_300", "diagnostic_b2", 0, 300),
    _case("B2_0_to_320", "diagnostic_b2", 0, 320),
    _case("B2_10_to_310", "diagnostic_b2", 10, 310),
    _case("B2_m20_to_300", "diagnostic_b2", -20, 300),
])


def case_by_name(name):
    for case in CASES:
        if case["case_name"] == name:
            return dict(case)
    raise KeyError(name)

