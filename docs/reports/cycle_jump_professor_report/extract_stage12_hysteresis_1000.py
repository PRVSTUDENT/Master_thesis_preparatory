from __future__ import print_function

import csv
import os

from odbAccess import openOdb


ODB_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "runs",
        "chaboche_umat",
        "stage12_percentage_jump_1000cycles",
        "reference_1000cycles",
        "chaboche_vp_v1_cyclic_eps005_1000cycles.odb",
    )
)
OUT_CSV = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "figures",
        "stage12_1000cycle_hysteresis_selected_cycles.csv",
    )
)

STEP_NAME = "CYCLIC_1000"
RIGHT_FACE_NAME = "RIGHT_FACE"
L0 = 10.0
SELECTED_CYCLES = (1, 10, 373, 1000)


def average_scalar(field):
    values = field.values
    if not values:
        return None
    return sum(v.data for v in values) / float(len(values))


def average_s11(frame):
    values = frame.fieldOutputs["S"].values
    if not values:
        return None
    return sum(v.data[0] for v in values) / float(len(values))


def average_right_u1(frame, right_face):
    subset = frame.fieldOutputs["U"].getSubset(region=right_face)
    values = subset.values
    if not values:
        return None
    return sum(v.data[0] for v in values) / float(len(values))


def cycle_from_time(frame_value):
    # Cycle 1 occupies time 0 <= t <= 1, cycle 1000 occupies 999 < t <= 1000.
    if frame_value <= 0.0:
        return 1
    return int(frame_value - 1.0e-9) + 1


def main():
    odb = openOdb(path=ODB_PATH, readOnly=True)
    try:
        step = odb.steps[STEP_NAME]
        right_face = odb.rootAssembly.nodeSets[RIGHT_FACE_NAME]
        rows = []
        for frame_index, frame in enumerate(step.frames):
            cycle = cycle_from_time(frame.frameValue)
            if cycle not in SELECTED_CYCLES:
                continue
            u1 = average_right_u1(frame, right_face)
            s11 = average_s11(frame)
            sdv1 = average_scalar(frame.fieldOutputs["SDV1"])
            rows.append(
                {
                    "cycle": cycle,
                    "frame_index": frame_index,
                    "frame_time": frame.frameValue,
                    "engineering_strain": u1 / L0 if u1 is not None else "",
                    "S11": s11 if s11 is not None else "",
                    "STATEV1": sdv1 if sdv1 is not None else "",
                }
            )
    finally:
        odb.close()

    out_dir = os.path.dirname(OUT_CSV)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(OUT_CSV, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "cycle",
                "frame_index",
                "frame_time",
                "engineering_strain",
                "S11",
                "STATEV1",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote %d rows to %s" % (len(rows), OUT_CSV))


if __name__ == "__main__":
    main()
