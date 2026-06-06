from __future__ import print_function

"""Compare Stage 16N-B0 initialization-only audit against reference cycle 100."""

from odbAccess import openOdb
import csv
import math
import os
import re
import struct
import sys


REF_ODB = "stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles.odb"
AUDIT_ODB = "stage16n_exact_reinjection/cases/B0_AUDIT_100_INITIALIZATION_ONLY/stage16n_b0_audit_100_initialization_only.odb"
STATE_CSV = "stage16n_exact_reinjection/cases/B0_AUDIT_100_INITIALIZATION_ONLY/state.csv"
STATE_BIN = "stage16n_exact_reinjection/cases/B0_AUDIT_100_INITIALIZATION_ONLY/state.bin"
OUT_DIR = "stage16n_exact_reinjection/cases/B0_AUDIT_100_INITIALIZATION_ONLY/diagnostics"
CYCLE = 100
TARGET_ELEMENT = 1242
TARGET_IP = 7
VARIABLES = ["S11_ABS", "MISES", "SDV1", "SDV8", "SDV11"]


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    return "%.12g" % float(value)


def step_cycle(name):
    match = re.search(r"CYCLE_(\d+)", name.upper())
    return int(match.group(1)) if match else None


def find_step(odb, cycle):
    for name in odb.steps.keys():
        if step_cycle(name) == cycle:
            return odb.steps[name], name
    raise RuntimeError("Could not find cycle %d in %s" % (cycle, odb.name))


def find_element_set(odb, preferred):
    assembly = odb.rootAssembly
    for key in assembly.elementSets.keys():
        if key.upper() == preferred.upper() or preferred.upper() in key.upper():
            return assembly.elementSets[key]
    raise RuntimeError("Could not find element set %s" % preferred)


def latest_field_frame(step):
    frames = [frame for frame in step.frames if "S" in frame.fieldOutputs.keys()]
    if not frames:
        raise RuntimeError("No S field frame in %s" % step.name)
    return frames[-1]


def mises(data):
    s11, s22, s33, s12, s13, s23 = [float(v) for v in data[:6]]
    mean = (s11 + s22 + s33) / 3.0
    d11 = s11 - mean
    d22 = s22 - mean
    d33 = s33 - mean
    return math.sqrt(1.5 * (d11 * d11 + d22 * d22 + d33 * d33 + 2.0 * (s12 * s12 + s13 * s13 + s23 * s23)))


def values_by_key(frame, hole_ring):
    out = {}
    stress = frame.fieldOutputs["S"].getSubset(region=hole_ring)
    for value in stress.values:
        key = (int(value.elementLabel), int(value.integrationPoint))
        out.setdefault(key, {})
        out[key]["S11_ABS"] = abs(float(value.data[0]))
        out[key]["MISES"] = mises(value.data)
    for sdv in [1, 8, 11]:
        field = frame.fieldOutputs["SDV%d" % sdv].getSubset(region=hole_ring)
        for value in field.values:
            key = (int(value.elementLabel), int(value.integrationPoint))
            out.setdefault(key, {})
            out[key]["SDV%d" % sdv] = float(value.data)
    return out


def percentile(values, pct):
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * pct / 100.0
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi] - vals[lo]) * (pos - lo)


def rel_pct(value, ref):
    return 100.0 * abs(value - ref) / max(abs(ref), 1.0e-12)


def max_location(data, variable):
    best_key = None
    best_value = None
    for key, values in data.items():
        value = values.get(variable)
        if value is not None and (best_value is None or value > best_value):
            best_key = key
            best_value = value
    return best_key, best_value


def read_binary_record(noel, npt):
    recno = (noel - 1) * 8 + npt
    with open(STATE_BIN, "rb") as handle:
        handle.seek((recno - 1) * 33 * 8)
        data = handle.read(33 * 8)
    vals = struct.unpack("<33d", data)
    return vals


def read_csv_target(noel, npt):
    with open(STATE_CSV, "r") as handle:
        for row in csv.DictReader(handle):
            if int(row["NOEL"]) == noel and int(row["NPT"]) == npt:
                return row
    raise RuntimeError("Target NOEL/NPT not found in CSV")


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    csv_target = read_csv_target(TARGET_ELEMENT, TARGET_IP)
    bin_vals = read_binary_record(TARGET_ELEMENT, TARGET_IP)
    binary_rows = []
    for i in range(1, 7):
        csv_val = abs(float(csv_target["S%d" % i])) if i == 1 else float(csv_target["S%d" % i])
        bin_val = abs(bin_vals[i - 1]) if i == 1 else bin_vals[i - 1]
        binary_rows.append({
            "quantity": "S%d" % i,
            "csv_value": csv_val,
            "binary_value": bin_val,
            "absolute_error": abs(bin_val - csv_val),
        })
    for sdv in [1, 8, 11]:
        csv_val = float(csv_target["SDV%d" % sdv])
        bin_val = bin_vals[6 + sdv - 1]
        binary_rows.append({
            "quantity": "SDV%d" % sdv,
            "csv_value": csv_val,
            "binary_value": bin_val,
            "absolute_error": abs(bin_val - csv_val),
        })

    ref_odb = openOdb(REF_ODB, readOnly=True)
    audit_odb = openOdb(AUDIT_ODB, readOnly=True)
    try:
        ref_step, ref_step_name = find_step(ref_odb, CYCLE)
        audit_step, audit_step_name = find_step(audit_odb, CYCLE)
        ref = values_by_key(latest_field_frame(ref_step), find_element_set(ref_odb, "HOLE_RING"))
        audit = values_by_key(latest_field_frame(audit_step), find_element_set(audit_odb, "HOLE_RING"))
    finally:
        ref_odb.close()
        audit_odb.close()

    common = sorted(set(ref.keys()).intersection(audit.keys()))
    pointwise_rows = []
    percentile_rows = []
    argmax_rows = []
    for variable in VARIABLES:
        abs_errors = []
        rel_errors = []
        for key in common:
            rv = ref[key][variable]
            av = audit[key][variable]
            ae = abs(av - rv)
            re = rel_pct(av, rv)
            abs_errors.append(ae)
            rel_errors.append(re)
            pointwise_rows.append({
                "variable": variable,
                "element": key[0],
                "integration_point": key[1],
                "reference": rv,
                "audit": av,
                "absolute_error": ae,
                "relative_error_pct": re,
            })
        ref_key, ref_val = max_location(ref, variable)
        audit_key, audit_val = max_location(audit, variable)
        argmax_rows.append({
            "variable": variable,
            "reference_argmax_element": ref_key[0],
            "reference_argmax_ip": ref_key[1],
            "reference_argmax_value": ref_val,
            "audit_at_reference_argmax": audit[ref_key][variable],
            "audit_argmax_element": audit_key[0],
            "audit_argmax_ip": audit_key[1],
            "audit_argmax_value": audit_val,
            "reference_at_audit_argmax": ref[audit_key][variable],
            "same_argmax_location": str(ref_key == audit_key).lower(),
        })
        percentile_rows.append({
            "variable": variable,
            "count": len(abs_errors),
            "mean_absolute_error": sum(abs_errors) / float(len(abs_errors)),
            "median_absolute_error": percentile(abs_errors, 50),
            "p95_absolute_error": percentile(abs_errors, 95),
            "max_absolute_error": max(abs_errors),
            "mean_relative_error_pct": sum(rel_errors) / float(len(rel_errors)),
            "median_relative_error_pct": percentile(rel_errors, 50),
            "p95_relative_error_pct": percentile(rel_errors, 95),
            "max_relative_error_pct": max(rel_errors),
        })

    paths = {
        "binary": os.path.join(OUT_DIR, "stage16n_b0_100_binary_reader_audit.csv"),
        "pointwise": os.path.join(OUT_DIR, "stage16n_b0_100_initialization_pointwise_errors.csv"),
        "percentiles": os.path.join(OUT_DIR, "stage16n_b0_100_initialization_summary.csv"),
        "argmax": os.path.join(OUT_DIR, "stage16n_b0_100_initialization_argmax_check.csv"),
        "report": os.path.join(OUT_DIR, "STAGE16N_B0_100_INITIALIZATION_AUDIT_RESULT.md"),
    }
    with csv_open_write(paths["binary"]) as handle:
        fields = ["quantity", "csv_value", "binary_value", "absolute_error"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in binary_rows:
            writer.writerow(dict((f, row[f] if f == "quantity" else fmt(row[f])) for f in fields))
    with csv_open_write(paths["pointwise"]) as handle:
        fields = ["variable", "element", "integration_point", "reference", "audit", "absolute_error", "relative_error_pct"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in pointwise_rows:
            writer.writerow(dict((f, row[f] if f in ("variable", "element", "integration_point") else fmt(row[f])) for f in fields))
    with csv_open_write(paths["percentiles"]) as handle:
        fields = ["variable", "count", "mean_absolute_error", "median_absolute_error", "p95_absolute_error", "max_absolute_error", "mean_relative_error_pct", "median_relative_error_pct", "p95_relative_error_pct", "max_relative_error_pct"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in percentile_rows:
            writer.writerow(dict((f, row[f] if f == "variable" else fmt(row[f])) for f in fields))
    with csv_open_write(paths["argmax"]) as handle:
        fields = ["variable", "reference_argmax_element", "reference_argmax_ip", "reference_argmax_value", "audit_at_reference_argmax", "audit_argmax_element", "audit_argmax_ip", "audit_argmax_value", "reference_at_audit_argmax", "same_argmax_location"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in argmax_rows:
            writer.writerow(dict((f, row[f] if f in ("variable", "same_argmax_location", "reference_argmax_element", "reference_argmax_ip", "audit_argmax_element", "audit_argmax_ip") else fmt(row[f])) for f in fields))

    sdv8 = [row for row in percentile_rows if row["variable"] == "SDV8"][0]
    sdv8_arg = [row for row in argmax_rows if row["variable"] == "SDV8"][0]
    binary_max = max(float(row["absolute_error"]) for row in binary_rows)
    lines = [
        "# Stage 16N-B0 Cycle-100 Initialization Audit Result",
        "",
        "## Purpose",
        "",
        "Determine whether the B0-1 local SDV8 mismatch already exists immediately after exact cycle-100 initialization.",
        "",
        "## Binary Reader Audit",
        "",
        "- Target point: element `%d`, IP `%d`" % (TARGET_ELEMENT, TARGET_IP),
        "- Maximum CSV-vs-binary absolute error over audited S/SDV values: `%s`" % fmt(binary_max),
        "",
        "## Abaqus Initialization Audit",
        "",
        "- Reference step: `%s`" % ref_step_name,
        "- Audit step: `%s`" % audit_step_name,
        "- Common hole-ring element/IP records: `%d`" % len(common),
        "- SDV8 median relative error: `%s%%`" % fmt(sdv8["median_relative_error_pct"]),
        "- SDV8 p95 relative error: `%s%%`" % fmt(sdv8["p95_relative_error_pct"]),
        "- SDV8 max relative error: `%s%%`" % fmt(sdv8["max_relative_error_pct"]),
        "- Reference SDV8 argmax: element `%s`, IP `%s`" % (sdv8_arg["reference_argmax_element"], sdv8_arg["reference_argmax_ip"]),
        "- Audit SDV8 argmax: element `%s`, IP `%s`" % (sdv8_arg["audit_argmax_element"], sdv8_arg["audit_argmax_ip"]),
        "- Same SDV8 argmax location: `%s`" % sdv8_arg["same_argmax_location"],
        "",
        "## Output Files",
        "",
        "- `stage16n_b0_100_binary_reader_audit.csv`",
        "- `stage16n_b0_100_initialization_pointwise_errors.csv`",
        "- `stage16n_b0_100_initialization_argmax_check.csv`",
        "- `stage16n_b0_100_initialization_summary.csv`",
    ]
    with open(paths["report"], "w") as handle:
        handle.write("\n".join(lines) + "\n")

    for path in paths.values():
        print("Wrote:", path)


if __name__ == "__main__":
    main()
