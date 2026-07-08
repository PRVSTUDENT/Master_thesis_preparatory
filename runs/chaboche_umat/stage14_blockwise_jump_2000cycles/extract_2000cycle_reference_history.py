from odbAccess import openOdb
import csv
import os
import sys


ODB_PATH = "chaboche_vp_v1_cyclic_eps005_2000cycles.odb"
OUT_CSV = "chaboche_vp_v1_cyclic_eps005_2000cycles_cycle_history.csv"
SUMMARY_MD = "STAGE14A_2000CYCLE_REFERENCE_SUMMARY.md"

NSTATEV = 15
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]
TARGET_CYCLES = list(range(1, 2001))


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / float(len(values)) if values else None


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return "%.12g" % value


def field_average(frame, field_name):
    if field_name not in frame.fieldOutputs.keys():
        return None
    return mean([v.data for v in frame.fieldOutputs[field_name].values])


def tensor_average(frame, field_name):
    if field_name not in frame.fieldOutputs.keys():
        return [None] * 6
    values = frame.fieldOutputs[field_name].values
    accum = [0.0] * 6
    count = 0
    for value in values:
        for i in range(6):
            accum[i] += value.data[i]
        count += 1
    if count == 0:
        return [None] * 6
    return [item / float(count) for item in accum]


def find_node_set(odb, preferred):
    assembly = odb.rootAssembly
    upper_to_key = dict((key.upper(), key) for key in assembly.nodeSets.keys())
    if preferred.upper() in upper_to_key:
        return assembly.nodeSets[upper_to_key[preferred.upper()]]
    for key in assembly.nodeSets.keys():
        if preferred.upper() in key.upper():
            return assembly.nodeSets[key]
    return None


def nodal_component(frame, field_name, region, component_index, reducer):
    if region is None or field_name not in frame.fieldOutputs.keys():
        return None
    values = [v.data[component_index] for v in frame.fieldOutputs[field_name].getSubset(region=region).values]
    if not values:
        return None
    if reducer == "sum":
        return sum(values)
    return mean(values)


def frame_metrics(frame, right_face):
    row = {}
    for i in range(1, NSTATEV + 1):
        row["STATEV%d_end" % i] = field_average(frame, "SDV%d" % i)
    stress = tensor_average(frame, "S")
    for name, value in zip(STRESS_COMPONENTS, stress):
        row[name] = value
    row["RIGHT_FACE_U1_AVG"] = nodal_component(frame, "U", right_face, 0, "mean")
    row["RIGHT_FACE_RF1_SUM"] = nodal_component(frame, "RF", right_face, 0, "sum")
    return row


def main():
    if not os.path.exists(ODB_PATH):
        raise RuntimeError("Missing ODB: %s" % ODB_PATH)

    odb = openOdb(ODB_PATH, readOnly=True)
    try:
        all_frames = []
        for step_name in odb.steps.keys():
            for frame in odb.steps[step_name].frames:
                all_frames.append((frame.frameValue, step_name, frame))
        all_frames.sort(key=lambda item: item[0])
        right_face = find_node_set(odb, "RIGHT_FACE")
        rows = []
        previous = None

        for cycle in TARGET_CYCLES:
            frame_time, step_name, frame = min(all_frames, key=lambda item: abs(item[0] - float(cycle)))
            row = {"cycle": cycle, "frame_time": frame_time, "frame_time_error": frame_time - float(cycle), "step_name": step_name}
            row.update(frame_metrics(frame, right_face))
            if previous is None:
                for i in range(1, NSTATEV + 1):
                    row["Delta_STATEV%d" % i] = ""
                for name in STRESS_COMPONENTS:
                    row["Delta_%s" % name] = ""
            else:
                for i in range(1, NSTATEV + 1):
                    key = "STATEV%d_end" % i
                    row["Delta_STATEV%d" % i] = row[key] - previous[key]
                for name in STRESS_COMPONENTS:
                    row["Delta_%s" % name] = row[name] - previous[name]
            rows.append(row)
            previous = row
    finally:
        odb.close()

    fields = ["cycle", "frame_time", "frame_time_error", "step_name"]
    fields += ["STATEV%d_end" % i for i in range(1, NSTATEV + 1)]
    fields += ["Delta_STATEV%d" % i for i in range(1, NSTATEV + 1)]
    fields += STRESS_COMPONENTS
    fields += ["Delta_%s" % name for name in STRESS_COMPONENTS]
    fields += ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]

    with csv_open_write(OUT_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict((field, fmt(row.get(field))) for field in fields))

    final = rows[-1]
    lines = [
        "# Stage 14A 2000-Cycle Reference Summary",
        "",
        "- Extracted rows: `%d`" % len(rows),
        "- Min cycle: `1`",
        "- Max cycle: `2000`",
        "- Cycle 2000 frame time: `%s`" % fmt(final["frame_time"]),
        "- Cycle 2000 STATEV1: `%s`" % fmt(final["STATEV1_end"]),
        "- Cycle 2000 S11: `%s MPa`" % fmt(final["S11"]),
        "- Cycle 2000 RIGHT_FACE_RF1_SUM: `%s`" % fmt(final["RIGHT_FACE_RF1_SUM"]),
    ]
    with open(SUMMARY_MD, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")

    print("Wrote:", OUT_CSV)
    print("Extracted cycles:", len(rows))
    print("Cycle 2000 STATEV1:", final["STATEV1_end"])
    print("Cycle 2000 S11:", final["S11"])
    print("Cycle 2000 RIGHT_FACE_RF1_SUM:", final["RIGHT_FACE_RF1_SUM"])


if __name__ == "__main__":
    main()
