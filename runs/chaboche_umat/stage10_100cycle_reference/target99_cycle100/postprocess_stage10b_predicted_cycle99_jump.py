from odbAccess import openOdb
import csv
import sys


ODB_PATH = "chaboche_stage10b_predicted_cycle99_to_cycle100.odb"
REFERENCE_ODB_PATH = "../reference_100cycles/chaboche_vp_v1_cyclic_eps005_100cycles.odb"
REFERENCE_TIME = 100.0
CSV_PATH = "stage10b_predicted_cycle99_jump_result.csv"
REFERENCE_CSV = "cycle100_reference_statev_stress.csv"
REPORT_PATH = "STAGE10B_PREDICTED_CYCLE99_JUMP_RESULT_REPORT.md"
EXPECTED_INITIAL_STATEV1 = 0.70977318519734
EXPECTED_INITIAL_S11 = 364.7584567603074
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


def lerp(a, b, alpha):
    if a is None or b is None:
        return None
    return a + alpha * (b - a)


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


def find_node_set(odb, preferred):
    assembly = odb.rootAssembly
    keys = assembly.nodeSets.keys()
    upper_to_key = dict((key.upper(), key) for key in keys)
    if preferred.upper() in upper_to_key:
        return assembly.nodeSets[upper_to_key[preferred.upper()]], upper_to_key[preferred.upper()]
    for key in keys:
        if preferred.upper() in key.upper():
            return assembly.nodeSets[key], key
    return None, None


def nodal_component(frame, field_name, region, component_index, reducer):
    if region is None or field_name not in frame.fieldOutputs.keys():
        return None, 0
    subset = frame.fieldOutputs[field_name].getSubset(region=region)
    values = [v.data[component_index] for v in subset.values]
    if not values:
        return None, 0
    if reducer == "sum":
        return sum(values), len(values)
    return mean(values), len(values)


def frame_metrics(frame, right_face, right_face_name):
    row = {"frame_value": frame.frameValue, "description": frame.description, "right_face_node_set": right_face_name or ""}
    for i in range(1, 16):
        row["STATEV%d" % i], row["STATEV%d_count" % i] = field_average(frame, "SDV%d" % i)
    stress, stress_count = tensor_average(frame, "S")
    for name, value in zip(STRESS_COMPONENTS, stress):
        row[name] = value
    row["stress_count"] = stress_count
    row["RIGHT_FACE_U1_AVG"], row["right_face_u_count"] = nodal_component(frame, "U", right_face, 0, "mean")
    row["RIGHT_FACE_RF1_SUM"], row["right_face_rf_count"] = nodal_component(frame, "RF", right_face, 0, "sum")
    return row


def collect_stage10b_rows():
    odb = openOdb(ODB_PATH, readOnly=True)
    rows = []
    try:
        step_name = list(odb.steps.keys())[-1]
        step = odb.steps[step_name]
        frames = step.frames
        right_face, right_face_name = find_node_set(odb, "RIGHT_FACE")
        for label, frame in [("first", frames[0]), ("final", frames[-1])]:
            row = frame_metrics(frame, right_face, right_face_name)
            row["frame_label"] = label
            row["step_name"] = step_name
            rows.append(row)
    finally:
        odb.close()
    return rows


def collect_interpolated_reference():
    odb = openOdb(REFERENCE_ODB_PATH, readOnly=True)
    try:
        all_frames = []
        for step_name in odb.steps.keys():
            for frame in odb.steps[step_name].frames:
                all_frames.append((frame.frameValue, step_name, frame))
        all_frames.sort(key=lambda item: item[0])
        lower = None
        upper = None
        for item in all_frames:
            if item[0] <= REFERENCE_TIME:
                lower = item
            if item[0] >= REFERENCE_TIME:
                upper = item
                break
        if lower is None or upper is None:
            raise RuntimeError("Could not bracket reference time %s" % REFERENCE_TIME)
        right_face, right_face_name = find_node_set(odb, "RIGHT_FACE")
        low = frame_metrics(lower[2], right_face, right_face_name)
        high = frame_metrics(upper[2], right_face, right_face_name)
        dt = upper[0] - lower[0]
        alpha = 0.0 if abs(dt) < 1.0e-30 else (REFERENCE_TIME - lower[0]) / dt
        ref = {
            "source": "linear_interpolation_between_bracketing_100cycle_ODB_frames",
            "lower_time": lower[0],
            "upper_time": upper[0],
            "alpha": alpha,
            "right_face_node_set": right_face_name or "",
        }
        for i in range(1, 16):
            ref["STATEV%d" % i] = lerp(low["STATEV%d" % i], high["STATEV%d" % i], alpha)
        for name in STRESS_COMPONENTS:
            ref[name] = lerp(low[name], high[name], alpha)
        ref["RIGHT_FACE_U1_AVG"] = lerp(low["RIGHT_FACE_U1_AVG"], high["RIGHT_FACE_U1_AVG"], alpha)
        ref["RIGHT_FACE_RF1_SUM"] = lerp(low["RIGHT_FACE_RF1_SUM"], high["RIGHT_FACE_RF1_SUM"], alpha)
        return ref
    finally:
        odb.close()


def abs_err(value, ref):
    if value is None or ref is None:
        return None
    return abs(value - ref)


def rel_percent(value, ref):
    if value is None or ref is None or abs(ref) < 1.0e-30:
        return None
    return 100.0 * abs(value - ref) / abs(ref)


def write_reference_csv(reference):
    with csv_open_write(REFERENCE_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=["quantity", "cycle100_reference_value", "source", "lower_time", "upper_time", "alpha"])
        writer.writeheader()
        for i in range(1, 16):
            writer.writerow({"quantity": "STATEV%d" % i, "cycle100_reference_value": fmt(reference["STATEV%d" % i]), "source": reference["source"], "lower_time": fmt(reference["lower_time"]), "upper_time": fmt(reference["upper_time"]), "alpha": fmt(reference["alpha"])})
        for name in STRESS_COMPONENTS + ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]:
            writer.writerow({"quantity": name, "cycle100_reference_value": fmt(reference[name]), "source": reference["source"], "lower_time": fmt(reference["lower_time"]), "upper_time": fmt(reference["upper_time"]), "alpha": fmt(reference["alpha"])})


def write_result_csv(rows):
    fields = ["frame_label", "step_name", "frame_value", "description"]
    fields += ["STATEV%d" % i for i in range(1, 16)]
    fields += STRESS_COMPONENTS
    fields += ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM", "right_face_node_set"]
    fields += ["STATEV1_count", "stress_count", "right_face_u_count", "right_face_rf_count"]
    with csv_open_write(CSV_PATH) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {}
            for field in fields:
                out[field] = row[field] if field in ("frame_label", "step_name", "description", "right_face_node_set") else fmt(row.get(field))
            writer.writerow(out)


def decision(statev1_rel, s11_rel):
    if statev1_rel is not None and s11_rel is not None and statev1_rel < 1.0 and s11_rel < 1.0:
        return "accepted_clean_success"
    if statev1_rel is not None and s11_rel is not None and statev1_rel < 1.0 and s11_rel < 3.0:
        return "accepted_exploratory_success"
    return "not_accepted"


def write_report(rows, reference):
    first = rows[0]
    final = rows[-1]
    statev1_abs = abs_err(final["STATEV1"], reference["STATEV1"])
    statev1_rel = rel_percent(final["STATEV1"], reference["STATEV1"])
    s11_abs = abs_err(final["S11"], reference["S11"])
    s11_rel = rel_percent(final["S11"], reference["S11"])
    rf1_abs = abs_err(final["RIGHT_FACE_RF1_SUM"], reference["RIGHT_FACE_RF1_SUM"])
    rf1_rel = rel_percent(final["RIGHT_FACE_RF1_SUM"], reference["RIGHT_FACE_RF1_SUM"])
    outcome = decision(statev1_rel, s11_rel)
    lines = [
        "# Stage 10B Predicted Cycle-99 FE Jump Result Report",
        "",
        "## Purpose",
        "",
        "Validate the Stage 10B grouped adaptive recommendation: cycle 10 data -> predicted cycle 99 state -> one computed cycle to cycle 100.",
        "",
        "## Route",
        "",
        "- Base cycle: `10`",
        "- Predicted injection cycle: `99`",
        "- Continuation/reference cycle: `100`",
        "- DeltaN_restart: `89`",
        "- Skipped intermediate FE cycles: `88`",
        "",
        "## Abaqus Status",
        "",
        "- Datacheck job: `chaboche_stage10b_predicted_cycle99_to_cycle100_check`",
        "- Datacheck status: `completed`",
        "- Full analysis job: `chaboche_stage10b_predicted_cycle99_to_cycle100`",
        "- Full analysis status: `completed`",
        "- Final `.sta` status: `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`",
        "",
        "## Key Values",
        "",
        "| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |",
        "|---|---:|---:|---:|---:|",
        "| First output frame | %s | %s | %s | %s |" % (fmt(first["frame_value"]), fmt(first["STATEV1"]), fmt(first["S11"]), fmt(first["RIGHT_FACE_RF1_SUM"])),
        "| Final output frame | %s | %s | %s | %s |" % (fmt(final["frame_value"]), fmt(final["STATEV1"]), fmt(final["S11"]), fmt(final["RIGHT_FACE_RF1_SUM"])),
        "",
        "## Injection Check",
        "",
        "- Expected injected STATEV1: `%s`" % fmt(EXPECTED_INITIAL_STATEV1),
        "- First-frame STATEV1 absolute error: `%s`" % fmt(abs_err(first["STATEV1"], EXPECTED_INITIAL_STATEV1)),
        "- Expected injected S11: `%s MPa`" % fmt(EXPECTED_INITIAL_S11),
        "- First-frame S11 absolute error: `%s MPa`" % fmt(abs_err(first["S11"], EXPECTED_INITIAL_S11)),
        "",
        "## Reference Handling",
        "",
        "- Explicit reference ODB: `%s`" % REFERENCE_ODB_PATH,
        "- Reference time: `%s`" % fmt(REFERENCE_TIME),
        "- Reference source: `%s`" % reference["source"],
        "- Lower bracketing frame: `%s`" % fmt(reference["lower_time"]),
        "- Upper bracketing frame: `%s`" % fmt(reference["upper_time"]),
        "- Interpolation alpha: `%s`" % fmt(reference["alpha"]),
        "",
        "## Final Cycle-100 Comparison",
        "",
        "- Reference cycle-100 STATEV1: `%s`" % fmt(reference["STATEV1"]),
        "- Final STATEV1 absolute error: `%s`" % fmt(statev1_abs),
        "- Final STATEV1 relative error percent: `%s`" % fmt(statev1_rel),
        "- Reference cycle-100 S11: `%s MPa`" % fmt(reference["S11"]),
        "- Final S11 absolute error: `%s MPa`" % fmt(s11_abs),
        "- Final S11 relative error percent: `%s`" % fmt(s11_rel),
        "- Reference cycle-100 RIGHT_FACE RF1: `%s`" % fmt(reference["RIGHT_FACE_RF1_SUM"]),
        "- Final RIGHT_FACE RF1 absolute error: `%s`" % fmt(rf1_abs),
        "- Final RIGHT_FACE RF1 relative error percent: `%s`" % fmt(rf1_rel),
        "",
        "## Decision",
        "",
        "- Final STATEV1 below 1%% error: `%s`" % ("yes" if statev1_rel is not None and statev1_rel < 1.0 else "no"),
        "- Final S11 below 1%% error: `%s`" % ("yes" if s11_rel is not None and s11_rel < 1.0 else "no"),
        "- Final S11 below 3%% error: `%s`" % ("yes" if s11_rel is not None and s11_rel < 3.0 else "no"),
        "- Stage 10B DeltaN = 89 accepted: `%s`" % ("yes" if outcome.startswith("accepted") else "no"),
        "- Stage 10B outcome: `%s`" % outcome,
        "",
        "## Outputs",
        "",
        "- Result CSV: `%s`" % CSV_PATH,
        "- Reference CSV: `%s`" % REFERENCE_CSV,
    ]
    with open(REPORT_PATH, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    rows = collect_stage10b_rows()
    reference = collect_interpolated_reference()
    write_result_csv(rows)
    write_reference_csv(reference)
    write_report(rows, reference)
    print("Wrote %s" % CSV_PATH)
    print("Wrote %s" % REFERENCE_CSV)
    print("Wrote %s" % REPORT_PATH)


if __name__ == "__main__":
    main()
