from __future__ import print_function

"""Extract exact Stage 16N stress and SDV fields for reinjection.

Run with Abaqus Python on the completed 1000-cycle reference ODB, for example:

    abaqus python stage16n_extract_exact_state_for_reinjection.py \
      --odb stage16n_parallel_max_reference_1000cycles.odb \
      --cycles 100,250,500 \
      --outdir stage16n_exact_reinjection/state
"""

from odbAccess import openOdb
import argparse
import csv
import os
import re
import struct
import sys


NSTATEV = 27
STRESS_COMPONENTS = 6


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    return "%.16g" % float(value)


def step_cycle(step_name):
    match = re.search(r"CYCLE_(\d+)", step_name.upper())
    if not match:
        return None
    return int(match.group(1))


def parse_cycles(text):
    cycles = []
    for part in text.split(","):
        part = part.strip()
        if part:
            cycles.append(int(part))
    return cycles


def field_by_label_and_ip(field):
    out = {}
    for value in field.values:
        key = (int(value.elementLabel), int(value.integrationPoint))
        data = value.data
        try:
            out[key] = tuple(float(v) for v in data)
        except TypeError:
            out[key] = (float(data),)
    return out


def extract_cycle(odb, cycle, outdir):
    step_name = None
    for name in odb.steps.keys():
        if step_cycle(name) == cycle:
            step_name = name
            break
    if step_name is None:
        raise RuntimeError("No step found for cycle %d" % cycle)

    step = odb.steps[step_name]
    frames = [frame for frame in step.frames if "S" in frame.fieldOutputs.keys()]
    if not frames:
        raise RuntimeError("No stress field-output frame found for cycle %d" % cycle)
    frame = frames[-1]

    if "S" not in frame.fieldOutputs.keys():
        raise RuntimeError("Missing S field in cycle %d" % cycle)
    stress = field_by_label_and_ip(frame.fieldOutputs["S"])

    sdv_fields = []
    for i in range(1, NSTATEV + 1):
        key = "SDV%d" % i
        if key not in frame.fieldOutputs.keys():
            raise RuntimeError("Missing %s field in cycle %d" % (key, cycle))
        sdv_fields.append(field_by_label_and_ip(frame.fieldOutputs[key]))

    keys = sorted(stress.keys())
    state_path = os.path.join(outdir, "stage16n_exact_state_cycle%04d.csv" % cycle)
    binary_path = os.path.join(outdir, "stage16n_exact_state_cycle%04d.bin" % cycle)
    summary_path = os.path.join(outdir, "stage16n_exact_state_cycle%04d_summary.md" % cycle)

    fields = ["NOEL", "NPT"]
    fields += ["S%d" % i for i in range(1, STRESS_COMPONENTS + 1)]
    fields += ["SDV%d" % i for i in range(1, NSTATEV + 1)]

    with csv_open_write(state_path) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for key in keys:
            if any(key not in field for field in sdv_fields):
                raise RuntimeError("Missing SDV field at element/IP %s" % (key,))
            row = {"NOEL": key[0], "NPT": key[1]}
            svals = stress[key]
            for i in range(STRESS_COMPONENTS):
                row["S%d" % (i + 1)] = fmt(svals[i] if i < len(svals) else 0.0)
            for i, field in enumerate(sdv_fields, start=1):
                row["SDV%d" % i] = fmt(field[key][0])
            writer.writerow(row)

    max_record = max((noel - 1) * 8 + npt for noel, npt in keys)
    zero_record = struct.pack("<33d", *([0.0] * 33))
    with open(binary_path, "wb") as handle:
        handle.truncate(max_record * 33 * 8)
        for key in keys:
            noel, npt = key
            recno = (noel - 1) * 8 + npt
            svals = list(stress[key][:STRESS_COMPONENTS])
            while len(svals) < STRESS_COMPONENTS:
                svals.append(0.0)
            vals = svals + [sdv_fields[i][key][0] for i in range(NSTATEV)]
            handle.seek((recno - 1) * 33 * 8)
            handle.write(struct.pack("<33d", *vals))

    lines = [
        "# Stage 16N Exact Reinjection State",
        "",
        "- Source ODB: `%s`" % os.path.basename(odb.name),
        "- Source step: `%s`" % step_name,
        "- Source cycle: `%d`" % cycle,
        "- Frame value: `%s`" % frame.frameValue,
        "- Element/IP records: `%d`" % len(keys),
        "- State CSV: `%s`" % os.path.basename(state_path),
        "- State binary: `%s`" % os.path.basename(binary_path),
        "- Stress components: `S1-S6`",
        "- State variables: `SDV1-SDV27`",
    ]
    with open(summary_path, "w") as handle:
        handle.write("\n".join(lines) + "\n")

    print("Wrote %s" % state_path)
    print("Wrote %s" % summary_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--odb", required=True)
    parser.add_argument("--cycles", default="100,250,500")
    parser.add_argument("--outdir", default="stage16n_exact_reinjection/state")
    args = parser.parse_args()

    if not os.path.exists(args.odb):
        raise RuntimeError("Missing ODB: %s" % args.odb)
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    odb = openOdb(args.odb, readOnly=True)
    try:
        for cycle in parse_cycles(args.cycles):
            extract_cycle(odb, cycle, args.outdir)
    finally:
        odb.close()


if __name__ == "__main__":
    main()
