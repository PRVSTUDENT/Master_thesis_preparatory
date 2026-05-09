from odbAccess import openOdb
import csv
import os
import sys


JOB = "chaboche_vp_v1_cyclic_eps005_50cycles"
ODB_PATH = JOB + ".odb"
SUMMARY_CSV = JOB + "_summary.csv"
CYCLE_HISTORY_CSV = JOB + "_cycle_history.csv"
REPORT_MD = "CHABOCHE_50CYCLE_REFERENCE_REPORT.md"

NSTATEV = 15
NCYCLES = 50
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % value


def mean(values):
    return sum(values) / float(len(values)) if values else None


def avg_scalar(frame, field_name):
    if field_name not in frame.fieldOutputs.keys():
        return None, 0
    values = [value.data for value in frame.fieldOutputs[field_name].values]
    return mean(values), len(values)


def avg_tensor(frame, field_name, ncomp):
    if field_name not in frame.fieldOutputs.keys():
        return [None] * ncomp, 0
    values = frame.fieldOutputs[field_name].values
    accum = [0.0] * ncomp
    count = 0
    for value in values:
        for i in range(ncomp):
            accum[i] += value.data[i]
        count += 1
    if count == 0:
        return [None] * ncomp, 0
    return [item / float(count) for item in accum], count


def find_node_set(odb, preferred):
    keys = odb.rootAssembly.nodeSets.keys()
    upper_to_key = dict((key.upper(), key) for key in keys)
    if preferred.upper() in upper_to_key:
        key = upper_to_key[preferred.upper()]
        return odb.rootAssembly.nodeSets[key], key
    for key in keys:
        if preferred.upper() in key.upper():
            return odb.rootAssembly.nodeSets[key], key
    return None, ""


def nodal_component(frame, field_name, region, component_index, reducer):
    if region is None or field_name not in frame.fieldOutputs.keys():
        return None, 0
    subset = frame.fieldOutputs[field_name].getSubset(region=region)
    values = [value.data[component_index] for value in subset.values]
    if not values:
        return None, 0
    if reducer == "sum":
        return sum(values), len(values)
    return mean(values), len(values)


def collect_rows():
    odb = openOdb(ODB_PATH, readOnly=True)
    rows = []
    try:
        frames = []
        for step_name in odb.steps.keys():
            step = odb.steps[step_name]
            for frame in step.frames:
                frames.append((frame.frameValue, step_name, frame))
        frames.sort(key=lambda item: item[0])
        right_face, right_face_name = find_node_set(odb, "RIGHT_FACE")

        previous = {}
        for cycle in range(1, NCYCLES + 1):
            target = float(cycle)
            frame_time, step_name, frame = min(frames, key=lambda item: abs(item[0] - target))
            row = {
                "cycle": cycle,
                "step_name": step_name,
                "time": frame_time,
                "target_time": target,
                "time_error": frame_time - target,
                "right_face_node_set": right_face_name,
            }
            for i in range(1, NSTATEV + 1):
                value, count = avg_scalar(frame, "SDV%d" % i)
                row["STATEV%d_end" % i] = value
                row["Delta_STATEV%d" % i] = None if cycle == 1 else value - previous["STATEV%d_end" % i]
                row["statev_count"] = count
            stress, stress_count = avg_tensor(frame, "S", len(STRESS_COMPONENTS))
            for name, value in zip(STRESS_COMPONENTS, stress):
                row[name] = value
                row["Delta_%s" % name] = None if cycle == 1 else value - previous[name]
            row["stress_count"] = stress_count
            row["RIGHT_FACE_U1_AVG"], row["right_face_u_count"] = nodal_component(frame, "U", right_face, 0, "mean")
            row["RIGHT_FACE_RF1_SUM"], row["right_face_rf_count"] = nodal_component(frame, "RF", right_face, 0, "sum")
            rows.append(row)
            previous = row
    finally:
        odb.close()
    return rows


def write_cycle_history(rows):
    fields = ["cycle", "step_name", "time", "target_time", "time_error", "statev_count", "stress_count"]
    fields += ["STATEV%d_end" % i for i in range(1, NSTATEV + 1)]
    fields += ["Delta_STATEV%d" % i for i in range(1, NSTATEV + 1)]
    fields += STRESS_COMPONENTS
    fields += ["Delta_%s" % name for name in STRESS_COMPONENTS]
    fields += ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM", "right_face_node_set", "right_face_u_count", "right_face_rf_count"]
    with csv_open_write(CYCLE_HISTORY_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {}
            for field in fields:
                out[field] = row[field] if field in ("cycle", "step_name", "right_face_node_set", "statev_count", "stress_count", "right_face_u_count", "right_face_rf_count") else fmt(row.get(field))
            writer.writerow(out)


def write_summary(rows):
    final = rows[-1]
    fields = ["quantity", "value"]
    items = [
        ("cycles", NCYCLES),
        ("final_time", final["time"]),
        ("final_time_error", final["time_error"]),
        ("final_STATEV1", final["STATEV1_end"]),
        ("final_S11", final["S11"]),
        ("final_RIGHT_FACE_U1_AVG", final["RIGHT_FACE_U1_AVG"]),
        ("final_RIGHT_FACE_RF1_SUM", final["RIGHT_FACE_RF1_SUM"]),
        ("final_Delta_STATEV1", final["Delta_STATEV1"]),
        ("final_Delta_S11", final["Delta_S11"]),
    ]
    with csv_open_write(SUMMARY_CSV) as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        for key, value in items:
            writer.writerow([key, fmt(value)])


def write_report(rows):
    final = rows[-1]
    lines = [
        "# Chaboche-v1 50-Cycle Explicit Reference Report",
        "",
        "## Input",
        "",
        "- ODB: `%s`" % ODB_PATH,
        "- Input deck: `chaboche_vp_v1_cyclic_eps005_50cycles.inp`",
        "- UMAT: `umat/chaboche_vp_v1_working.f`",
        "- Cycles: `50`",
        "- DMAX: `0.02`",
        "- INC limit: `6000`",
        "",
        "## Final Cycle-50 Values",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        "| STATEV1 | %s |" % fmt(final["STATEV1_end"]),
        "| S11 (MPa) | %s |" % fmt(final["S11"]),
        "| RIGHT_FACE average U1 | %s |" % fmt(final["RIGHT_FACE_U1_AVG"]),
        "| RIGHT_FACE summed RF1 | %s |" % fmt(final["RIGHT_FACE_RF1_SUM"]),
        "| Final Delta STATEV1 | %s |" % fmt(final["Delta_STATEV1"]),
        "| Final Delta S11 | %s |" % fmt(final["Delta_S11"]),
        "",
        "## Output Files",
        "",
        "- Summary CSV: `%s`" % SUMMARY_CSV,
        "- Cycle history CSV: `%s`" % CYCLE_HISTORY_CSV,
        "",
        "This no-skip 50-cycle reference is intended for Stage 6B validation of a predicted jump from cycle 10 to cycle 49 followed by one computed continuation cycle.",
    ]
    with open(REPORT_MD, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    rows = collect_rows()
    write_cycle_history(rows)
    write_summary(rows)
    write_report(rows)
    print("Wrote %s" % CYCLE_HISTORY_CSV)
    print("Wrote %s" % SUMMARY_CSV)
    print("Wrote %s" % REPORT_MD)


if __name__ == "__main__":
    main()
