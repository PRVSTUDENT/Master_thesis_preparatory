from __future__ import print_function

from odbAccess import openOdb
import argparse
import csv
import math
import os
import re
import sys


SELECTED_CYCLES = set([1, 2, 10, 50, 100, 250, 500, 750, 1000])
NSTATEV = 27


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return "%.12g" % value


def step_cycle(step_name):
    match = re.search(r"CYCLE_(\d+)", step_name.upper())
    if not match:
        return None
    return int(match.group(1))


def trapz(xs, ys):
    area = 0.0
    for i in range(1, len(xs)):
        area += 0.5 * (ys[i] + ys[i - 1]) * (xs[i] - xs[i - 1])
    return area


def find_element_set(odb, preferred):
    assembly = odb.rootAssembly
    lookup = dict((key.upper(), key) for key in assembly.elementSets.keys())
    if preferred.upper() in lookup:
        return assembly.elementSets[lookup[preferred.upper()]]
    for key in assembly.elementSets.keys():
        if preferred.upper() in key.upper():
            return assembly.elementSets[key]
    return None


def aggregate_history(step):
    values_by_t = {}
    rf_counts = {}
    u_counts = {}
    for region_name in step.historyRegions.keys():
        region = step.historyRegions[region_name]
        if "RF1" in region.historyOutputs.keys():
            data = region.historyOutputs["RF1"].data or []
            for t, value in data:
                row = values_by_t.setdefault(float(t), {"u_sum": 0.0, "rf_sum": 0.0})
                row["rf_sum"] += float(value)
                rf_counts[float(t)] = rf_counts.get(float(t), 0) + 1
        if "U1" in region.historyOutputs.keys():
            data = region.historyOutputs["U1"].data or []
            for t, value in data:
                row = values_by_t.setdefault(float(t), {"u_sum": 0.0, "rf_sum": 0.0})
                row["u_sum"] += float(value)
                u_counts[float(t)] = u_counts.get(float(t), 0) + 1
    points = []
    for t in sorted(values_by_t.keys()):
        uc = u_counts.get(t, 0)
        rc = rf_counts.get(t, 0)
        if uc <= 0 or rc <= 0:
            continue
        points.append({
            "local_time": t,
            "U1_avg": values_by_t[t]["u_sum"] / float(uc),
            "RF1_sum": values_by_t[t]["rf_sum"],
        })
    return points


def mises_from_tensor(data):
    if len(data) < 6:
        return None
    s11, s22, s33, s12, s13, s23 = data[:6]
    mean = (s11 + s22 + s33) / 3.0
    d11 = s11 - mean
    d22 = s22 - mean
    d33 = s33 - mean
    return math.sqrt(1.5 * (d11 * d11 + d22 * d22 + d33 * d33 + 2.0 * (s12 * s12 + s13 * s13 + s23 * s23)))


def scalar_max(frame, name, region=None):
    if name not in frame.fieldOutputs.keys():
        return None
    field = frame.fieldOutputs[name]
    if region is not None:
        field = field.getSubset(region=region)
    vals = [float(v.data) for v in field.values]
    return max(vals) if vals else None


def stress_metrics(frame, region=None):
    out = {
        "S11_MAX_ABS": None,
        "MISES_MAX": None,
    }
    if "S" not in frame.fieldOutputs.keys():
        return out
    field = frame.fieldOutputs["S"]
    if region is not None:
        field = field.getSubset(region=region)
    s11 = []
    mises = []
    for value in field.values:
        data = value.data
        if len(data) >= 1:
            s11.append(abs(float(data[0])))
        m = mises_from_tensor(data)
        if m is not None:
            mises.append(m)
    if s11:
        out["S11_MAX_ABS"] = max(s11)
    if mises:
        out["MISES_MAX"] = max(mises)
    return out


def local_metrics_for_step(step, hole_ring):
    frames = [frame for frame in step.frames if "S" in frame.fieldOutputs.keys()]
    if not frames:
        return None
    frame = frames[-1]
    row = {}
    all_stress = stress_metrics(frame)
    hole_stress = stress_metrics(frame, hole_ring)
    for key, value in all_stress.items():
        row[key] = value
    for key, value in hole_stress.items():
        row["HOLE_RING_" + key] = value
    for i in range(1, NSTATEV + 1):
        row["SDV%d_MAX" % i] = scalar_max(frame, "SDV%d" % i)
        row["HOLE_RING_SDV%d_MAX" % i] = scalar_max(frame, "SDV%d" % i, hole_ring)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--odb", default=None)
    args = parser.parse_args()

    odb_path = args.odb or (args.job + ".odb")
    if not os.path.exists(odb_path):
        raise RuntimeError("Missing ODB: %s" % odb_path)

    odb = openOdb(odb_path, readOnly=True)
    try:
        hole_ring = find_element_set(odb, "HOLE_RING")
        cycle_rows = []
        selected_loop_rows = []
        local_rows = []
        for step_name in odb.steps.keys():
            cycle = step_cycle(step_name)
            if cycle is None:
                continue
            step = odb.steps[step_name]
            points = aggregate_history(step)
            if points:
                us = [p["U1_avg"] for p in points]
                rfs = [p["RF1_sum"] for p in points]
                cycle_rows.append({
                    "cycle": cycle,
                    "points": len(points),
                    "U1_max": max(us),
                    "U1_min": min(us),
                    "RF1_max": max(rfs),
                    "RF1_min": min(rfs),
                    "RF1_mean": sum(rfs) / float(len(rfs)),
                    "loop_area_abs": abs(trapz(us, rfs)),
                })
                if cycle in SELECTED_CYCLES:
                    for p in points:
                        row = dict(p)
                        row["cycle"] = cycle
                        selected_loop_rows.append(row)
            if cycle in SELECTED_CYCLES:
                metrics = local_metrics_for_step(step, hole_ring)
                if metrics:
                    metrics["cycle"] = cycle
                    local_rows.append(metrics)
    finally:
        odb.close()

    cycle_rows.sort(key=lambda row: row["cycle"])
    local_rows.sort(key=lambda row: row["cycle"])
    selected_loop_rows.sort(key=lambda row: (row["cycle"], row["local_time"]))

    cycle_csv = args.job + "_cycle_metrics.csv"
    loop_csv = args.job + "_selected_cycle_loops.csv"
    local_csv = args.job + "_selected_cycle_local_states.csv"

    with csv_open_write(cycle_csv) as handle:
        fields = ["cycle", "points", "U1_max", "U1_min", "RF1_max", "RF1_min", "RF1_mean", "loop_area_abs"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in cycle_rows:
            writer.writerow(dict((field, fmt(row.get(field))) for field in fields))

    with csv_open_write(loop_csv) as handle:
        fields = ["cycle", "local_time", "U1_avg", "RF1_sum"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in selected_loop_rows:
            writer.writerow(dict((field, fmt(row.get(field))) for field in fields))

    if local_rows:
        fields = ["cycle"] + sorted(k for k in local_rows[0].keys() if k != "cycle")
        with csv_open_write(local_csv) as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in local_rows:
                writer.writerow(dict((field, fmt(row.get(field))) for field in fields))
    else:
        with csv_open_write(local_csv) as handle:
            writer = csv.writer(handle)
            writer.writerow(["cycle", "status"])
            writer.writerow(["", "no selected field-output frames found"])

    print("Wrote:", cycle_csv)
    print("Wrote:", loop_csv)
    print("Wrote:", local_csv)


if __name__ == "__main__":
    main()
