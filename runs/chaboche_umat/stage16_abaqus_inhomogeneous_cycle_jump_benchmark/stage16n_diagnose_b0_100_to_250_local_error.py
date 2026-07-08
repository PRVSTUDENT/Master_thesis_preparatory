from __future__ import print_function

"""Diagnose Stage 16N-B0-1 local reinjection error at element/IP level.

Run with Abaqus Python from the Stage 16N directory:

    abaqus python stage16n_diagnose_b0_100_to_250_local_error.py
"""

from odbAccess import openOdb
import csv
import math
import os
import re
import sys


CASE = "B0_100_to_250"
REF_ODB = "stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles.odb"
REINJ_ODB = "stage16n_exact_reinjection/cases/B0_100_to_250/stage16n_exact_b0_100_to_250.odb"
OUT_DIR = "stage16n_exact_reinjection/cases/B0_100_to_250/diagnostics"
REFERENCE_CYCLE = 250

VARIABLES = ["S11_ABS", "MISES", "SDV1", "SDV8", "SDV11"]
SDV_NUMBERS = [1, 8, 11]


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % float(value)


def step_cycle(step_name):
    match = re.search(r"CYCLE_(\d+)", step_name.upper())
    if not match:
        return None
    return int(match.group(1))


def find_step(odb, cycle):
    for name in odb.steps.keys():
        if step_cycle(name) == cycle:
            return odb.steps[name], name
    raise RuntimeError("Could not find cycle %d in %s" % (cycle, odb.name))


def find_element_set(odb, preferred):
    assembly = odb.rootAssembly
    lookup = dict((key.upper(), key) for key in assembly.elementSets.keys())
    if preferred.upper() in lookup:
        return assembly.elementSets[lookup[preferred.upper()]]
    for key in assembly.elementSets.keys():
        if preferred.upper() in key.upper():
            return assembly.elementSets[key]
    raise RuntimeError("Could not find element set %s in %s" % (preferred, odb.name))


def mises(data):
    s11, s22, s33, s12, s13, s23 = [float(v) for v in data[:6]]
    mean = (s11 + s22 + s33) / 3.0
    d11 = s11 - mean
    d22 = s22 - mean
    d33 = s33 - mean
    return math.sqrt(1.5 * (d11 * d11 + d22 * d22 + d33 * d33 + 2.0 * (s12 * s12 + s13 * s13 + s23 * s23)))


def latest_field_frame(step):
    frames = [frame for frame in step.frames if "S" in frame.fieldOutputs.keys()]
    if not frames:
        raise RuntimeError("Step %s has no S field frames" % step.name)
    return frames[-1]


def values_by_key(frame, hole_ring):
    out = {}
    stress = frame.fieldOutputs["S"].getSubset(region=hole_ring)
    for value in stress.values:
        key = (int(value.elementLabel), int(value.integrationPoint))
        data = value.data
        out.setdefault(key, {})
        out[key]["S11_ABS"] = abs(float(data[0]))
        out[key]["MISES"] = mises(data)
    for sdv in SDV_NUMBERS:
        field = frame.fieldOutputs["SDV%d" % sdv].getSubset(region=hole_ring)
        for value in field.values:
            key = (int(value.elementLabel), int(value.integrationPoint))
            out.setdefault(key, {})
            out[key]["SDV%d" % sdv] = float(value.data)
    return out


def percentile(values, pct):
    if not values:
        return None
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
    scale = max(abs(ref), 1.0e-12)
    return 100.0 * abs(value - ref) / scale


def max_location(data, variable):
    best_key = None
    best_value = None
    for key, values in data.items():
        value = values.get(variable)
        if value is None:
            continue
        if best_value is None or value > best_value:
            best_value = value
            best_key = key
    return best_key, best_value


def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    ref_odb = openOdb(REF_ODB, readOnly=True)
    reinj_odb = openOdb(REINJ_ODB, readOnly=True)
    try:
        ref_step, ref_step_name = find_step(ref_odb, REFERENCE_CYCLE)
        reinj_step, reinj_step_name = find_step(reinj_odb, REFERENCE_CYCLE)
        ref_frame = latest_field_frame(ref_step)
        reinj_frame = latest_field_frame(reinj_step)
        ref_hole = find_element_set(ref_odb, "HOLE_RING")
        reinj_hole = find_element_set(reinj_odb, "HOLE_RING")
        ref = values_by_key(ref_frame, ref_hole)
        reinj = values_by_key(reinj_frame, reinj_hole)
    finally:
        ref_odb.close()
        reinj_odb.close()

    common = sorted(set(ref.keys()).intersection(reinj.keys()))
    if not common:
        raise RuntimeError("No common element/IP keys found")

    pointwise_rows = []
    percentile_rows = []
    argmax_rows = []

    for variable in VARIABLES:
        abs_errors = []
        rel_errors = []
        signed_errors = []
        max_err = None
        max_err_key = None

        for key in common:
            if variable not in ref[key] or variable not in reinj[key]:
                continue
            ref_value = ref[key][variable]
            reinj_value = reinj[key][variable]
            abs_error = abs(reinj_value - ref_value)
            signed_error = reinj_value - ref_value
            rel_error = rel_pct(reinj_value, ref_value)
            abs_errors.append(abs_error)
            signed_errors.append(signed_error)
            rel_errors.append(rel_error)
            if max_err is None or rel_error > max_err:
                max_err = rel_error
                max_err_key = key
            pointwise_rows.append({
                "variable": variable,
                "element": key[0],
                "integration_point": key[1],
                "reference": ref_value,
                "reinjection": reinj_value,
                "signed_error": signed_error,
                "absolute_error": abs_error,
                "relative_error_pct": rel_error,
            })

        ref_argmax_key, ref_argmax_value = max_location(ref, variable)
        reinj_argmax_key, reinj_argmax_value = max_location(reinj, variable)
        ref_at_reinj_argmax = ref.get(reinj_argmax_key, {}).get(variable)
        reinj_at_ref_argmax = reinj.get(ref_argmax_key, {}).get(variable)
        argmax_rows.append({
            "variable": variable,
            "reference_argmax_element": ref_argmax_key[0],
            "reference_argmax_ip": ref_argmax_key[1],
            "reference_argmax_value": ref_argmax_value,
            "reinjection_at_reference_argmax": reinj_at_ref_argmax,
            "reinjection_argmax_element": reinj_argmax_key[0],
            "reinjection_argmax_ip": reinj_argmax_key[1],
            "reinjection_argmax_value": reinj_argmax_value,
            "reference_at_reinjection_argmax": ref_at_reinj_argmax,
            "same_argmax_location": str(ref_argmax_key == reinj_argmax_key).lower(),
            "max_pointwise_error_element": max_err_key[0],
            "max_pointwise_error_ip": max_err_key[1],
            "max_pointwise_relative_error_pct": max_err,
        })

        percentile_rows.append({
            "variable": variable,
            "count": len(rel_errors),
            "mean_absolute_error": sum(abs_errors) / float(len(abs_errors)),
            "median_absolute_error": percentile(abs_errors, 50),
            "p95_absolute_error": percentile(abs_errors, 95),
            "max_absolute_error": max(abs_errors),
            "mean_relative_error_pct": sum(rel_errors) / float(len(rel_errors)),
            "median_relative_error_pct": percentile(rel_errors, 50),
            "p95_relative_error_pct": percentile(rel_errors, 95),
            "max_relative_error_pct": max(rel_errors),
            "mean_signed_error": sum(signed_errors) / float(len(signed_errors)),
        })

    pointwise_path = os.path.join(OUT_DIR, "stage16n_b0_100_to_250_pointwise_hole_errors.csv")
    percentiles_path = os.path.join(OUT_DIR, "stage16n_b0_100_to_250_error_percentiles.csv")
    argmax_path = os.path.join(OUT_DIR, "stage16n_b0_100_to_250_argmax_location_check.csv")
    report_path = os.path.join(OUT_DIR, "STAGE16N_B0_100_TO_250_DIAGNOSTIC_REVIEW.md")

    with csv_open_write(pointwise_path) as handle:
        fields = ["variable", "element", "integration_point", "reference", "reinjection", "signed_error", "absolute_error", "relative_error_pct"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in pointwise_rows:
            writer.writerow(dict((field, fmt(row.get(field)) if field not in ("variable", "element", "integration_point") else row.get(field)) for field in fields))

    with csv_open_write(percentiles_path) as handle:
        fields = ["variable", "count", "mean_absolute_error", "median_absolute_error", "p95_absolute_error", "max_absolute_error", "mean_relative_error_pct", "median_relative_error_pct", "p95_relative_error_pct", "max_relative_error_pct", "mean_signed_error"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in percentile_rows:
            writer.writerow(dict((field, fmt(row.get(field)) if field != "variable" else row.get(field)) for field in fields))

    with csv_open_write(argmax_path) as handle:
        fields = [
            "variable",
            "reference_argmax_element",
            "reference_argmax_ip",
            "reference_argmax_value",
            "reinjection_at_reference_argmax",
            "reinjection_argmax_element",
            "reinjection_argmax_ip",
            "reinjection_argmax_value",
            "reference_at_reinjection_argmax",
            "same_argmax_location",
            "max_pointwise_error_element",
            "max_pointwise_error_ip",
            "max_pointwise_relative_error_pct",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in argmax_rows:
            writer.writerow(dict((field, fmt(row.get(field)) if field not in ("variable", "same_argmax_location", "reference_argmax_element", "reference_argmax_ip", "reinjection_argmax_element", "reinjection_argmax_ip", "max_pointwise_error_element", "max_pointwise_error_ip") else row.get(field)) for field in fields))

    sdv8_pct = [row for row in percentile_rows if row["variable"] == "SDV8"][0]
    sdv8_arg = [row for row in argmax_rows if row["variable"] == "SDV8"][0]
    lines = [
        "# Stage 16N-B0-1 Local Diagnostic Review",
        "",
        "## Purpose",
        "",
        "Diagnose whether the `HOLE_RING_SDV8_MAX` mismatch in B0-1 is a field-wide reinjection error or a local extreme / argmax-location artifact.",
        "",
        "## Inputs",
        "",
        "- Reference ODB: `%s`" % REF_ODB,
        "- Reinjection ODB: `%s`" % REINJ_ODB,
        "- Compared cycle: `%d`" % REFERENCE_CYCLE,
        "- Reference step: `%s`" % ref_step_name,
        "- Reinjection step: `%s`" % reinj_step_name,
        "- Common hole-ring element/IP records: `%d`" % len(common),
        "",
        "## SDV8 Summary",
        "",
        "- Mean relative error: `%s%%`" % fmt(sdv8_pct["mean_relative_error_pct"]),
        "- Median relative error: `%s%%`" % fmt(sdv8_pct["median_relative_error_pct"]),
        "- 95th percentile relative error: `%s%%`" % fmt(sdv8_pct["p95_relative_error_pct"]),
        "- Maximum pointwise relative error: `%s%%`" % fmt(sdv8_pct["max_relative_error_pct"]),
        "- Reference argmax element/IP: `%s/%s`" % (sdv8_arg["reference_argmax_element"], sdv8_arg["reference_argmax_ip"]),
        "- Reinjection argmax element/IP: `%s/%s`" % (sdv8_arg["reinjection_argmax_element"], sdv8_arg["reinjection_argmax_ip"]),
        "- Same argmax location: `%s`" % sdv8_arg["same_argmax_location"],
        "",
        "## Output Files",
        "",
        "- `stage16n_b0_100_to_250_pointwise_hole_errors.csv`",
        "- `stage16n_b0_100_to_250_error_percentiles.csv`",
        "- `stage16n_b0_100_to_250_argmax_location_check.csv`",
        "",
        "## Interpretation Rule",
        "",
        "If SDV8 median and 95th-percentile errors are small while only the max/argmax metric is high, B0-1 may be accepted as a practical reinjection pass. If the same element/IP shows large SDV8 error or many hole-ring points are high, B0-1 remains blocked for fixed cycle-jump validation.",
    ]
    with open(report_path, "w") as handle:
        handle.write("\n".join(lines) + "\n")

    print("Wrote:", pointwise_path)
    print("Wrote:", percentiles_path)
    print("Wrote:", argmax_path)
    print("Wrote:", report_path)


if __name__ == "__main__":
    main()
