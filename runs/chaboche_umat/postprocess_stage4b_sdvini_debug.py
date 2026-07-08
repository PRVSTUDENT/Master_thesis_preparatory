from odbAccess import openOdb
import csv
import sys


ODB_PATH = "chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_debug.odb"
CSV_PATH = "stage4_injected_cycle_jump/stage4b_sdvini_debug_first_final.csv"
REPORT_PATH = "stage4_injected_cycle_jump/STAGE4B_SDVINI_DEBUG_REPORT.md"
EXPECTED_INITIAL_STATEV1 = 0.13485494256019592
REFERENCE_FINAL_STATEV1 = 0.14202569425106049


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


def field_average(frame, field_name):
    if field_name not in frame.fieldOutputs.keys():
        return None, 0
    values = [v.data for v in frame.fieldOutputs[field_name].values]
    return mean(values), len(values)


def tensor_average(frame, field_name):
    if field_name not in frame.fieldOutputs.keys():
        return [None] * 6, 0
    values = frame.fieldOutputs[field_name].values
    accum = [0.0] * 6
    count = 0
    for value in values:
        for i in range(6):
            accum[i] += value.data[i]
        count += 1
    if count == 0:
        return [None] * 6, 0
    return [item / float(count) for item in accum], count


def collect():
    odb = openOdb(ODB_PATH, readOnly=True)
    rows = []
    try:
        step_name = list(odb.steps.keys())[-1]
        step = odb.steps[step_name]
        frames = step.frames
        picks = [("first", frames[0]), ("final", frames[-1])]
        for label, frame in picks:
            row = {
                "frame_label": label,
                "step_name": step_name,
                "frame_value": frame.frameValue,
                "description": frame.description,
            }
            for i in range(1, 16):
                row["STATEV%d" % i], row["STATEV%d_count" % i] = field_average(frame, "SDV%d" % i)
            stress, stress_count = tensor_average(frame, "S")
            for name, value in zip(["S11", "S22", "S33", "S12", "S13", "S23"], stress):
                row[name] = value
            row["stress_count"] = stress_count
            rows.append(row)
    finally:
        odb.close()
    return rows


def write_csv(rows):
    fields = ["frame_label", "step_name", "frame_value", "description"]
    fields += ["STATEV%d" % i for i in range(1, 16)]
    fields += ["S11", "S22", "S33", "S12", "S13", "S23"]
    fields += ["STATEV1_count", "stress_count"]
    with csv_open_write(CSV_PATH) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {}
            for field in fields:
                out[field] = row[field] if field in ("frame_label", "step_name", "description") else fmt(row.get(field))
            writer.writerow(out)


def abs_err(value, ref):
    if value is None:
        return None
    return abs(value - ref)


def write_report(rows):
    first = rows[0]
    final = rows[-1]
    first_sdv1 = first["STATEV1"]
    final_sdv1 = final["STATEV1"]
    first_matches = first_sdv1 is not None and abs(first_sdv1 - EXPECTED_INITIAL_STATEV1) < 1.0e-6
    final_near_ref = final_sdv1 is not None and abs(final_sdv1 - REFERENCE_FINAL_STATEV1) < 1.0e-3

    lines = [
        "# Stage 4B SDVINI Debug Report",
        "",
        "## Inputs",
        "",
        "- ODB: `%s`" % ODB_PATH,
        "- Debug UMAT: `umat_chaboche_v1_with_sdvini_debug.f`",
        "- Debug input deck: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only_debug.inp`",
        "",
        "## Key STATEV1 Values",
        "",
        "| Frame | Time | STATEV1 | S11 (MPa) |",
        "|---|---:|---:|---:|",
        "| First output frame | %s | %s | %s |" % (fmt(first["frame_value"]), fmt(first_sdv1), fmt(first["S11"])),
        "| Final output frame | %s | %s | %s |" % (fmt(final["frame_value"]), fmt(final_sdv1), fmt(final["S11"])),
        "",
        "Expected injected STATEV1: `%s`" % fmt(EXPECTED_INITIAL_STATEV1),
        "Reference cycle-20 STATEV1: `%s`" % fmt(REFERENCE_FINAL_STATEV1),
        "",
        "## Interpretation",
        "",
        "- First output STATEV1 matches injected cycle-19 value within `1e-6`: `%s`" % ("yes" if first_matches else "no"),
        "- Final output STATEV1 is near explicit cycle-20 reference within `1e-3`: `%s`" % ("yes" if final_near_ref else "no"),
        "- First-frame absolute error from injected STATEV1: `%s`" % fmt(abs_err(first_sdv1, EXPECTED_INITIAL_STATEV1)),
        "- Final-frame absolute error from cycle-20 reference: `%s`" % fmt(abs_err(final_sdv1, REFERENCE_FINAL_STATEV1)),
        "",
        "Note: Fortran debug file writes did not appear in the working directory or standard Abaqus text outputs, so this report uses ODB evidence for the numerical SDVINI check.",
        "",
        "## Output",
        "",
        "- CSV: `%s`" % CSV_PATH,
    ]
    with open(REPORT_PATH, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    rows = collect()
    write_csv(rows)
    write_report(rows)
    print("Wrote %s" % CSV_PATH)
    print("Wrote %s" % REPORT_PATH)


if __name__ == "__main__":
    main()
