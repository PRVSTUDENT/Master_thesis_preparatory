from __future__ import print_function

import argparse
import csv
import math
import os
import re
import subprocess
import sys


NSTATEV = 15
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]
ACTIVE_STATEV = set([1, 2, 3, 4, 8, 9, 10])
NEAR_ZERO_STATEV = set([5, 6, 7, 11, 12, 13])
QISO = 200.0
BISO = 0.05
FINAL_CYCLE = 2000

STRATEGIES = {
    "jump25": [
        {"base": 10, "target": 500, "continue": 510},
        {"base": 510, "target": 1000, "continue": 1010},
        {"base": 1010, "target": 1500, "continue": 1510},
        {"base": 1510, "target": 1990, "continue": 2000},
    ],
    "jump37": [
        {"base": 10, "target": 740, "continue": 750},
        {"base": 750, "target": 1480, "continue": 1490},
        {"base": 1490, "target": 1990, "continue": 2000},
    ],
    "jump50": [
        {"base": 10, "target": 1000, "continue": 1010},
        {"base": 1010, "target": 1990, "continue": 2000},
    ],
    "jump65": [
        {"base": 10, "target": 1300, "continue": 1310},
        {"base": 1310, "target": 1990, "continue": 2000},
    ],
}


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


def maybe_float(text):
    if text is None or text == "":
        return None
    return float(text)


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / float(len(values)) if values else None


def abs_err(value, ref):
    if value is None or ref is None:
        return None
    return abs(value - ref)


def rel_err(value, ref):
    if value is None or ref is None or abs(ref) < 1.0e-30:
        return None
    return abs(value - ref) / abs(ref)


def fortran_d(value):
    text = "%.15G" % value
    text = text.replace("E", "D").replace("e", "D")
    if "D" not in text and "." not in text:
        text += ".0"
    return text + "D0" if "D" not in text else text


def statev_policy(index):
    if index in ACTIVE_STATEV:
        return "active_first_order_cycle_space"
    if index in NEAR_ZERO_STATEV:
        return "near_zero_predicted_flagged"
    if index == 14:
        return "recomputed_from_predicted_STATEV1"
    if index == 15:
        return "reset_to_zero_for_injection"
    return "first_order_cycle_space"


def read_cycle_history(path):
    rows = []
    with open(path, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed = {"cycle": int(row["cycle"])}
            for i in range(1, NSTATEV + 1):
                parsed["STATEV%d_end" % i] = maybe_float(row.get("STATEV%d_end" % i))
                parsed["Delta_STATEV%d" % i] = maybe_float(row.get("Delta_STATEV%d" % i))
            for name in STRESS_COMPONENTS:
                parsed[name] = maybe_float(row.get(name))
                parsed["Delta_%s" % name] = maybe_float(row.get("Delta_%s" % name))
            for name in ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]:
                parsed[name] = maybe_float(row.get(name))
            rows.append(parsed)
    return rows


def get_cycle_row(rows, cycle, csv_path):
    for row in rows:
        if row["cycle"] == cycle:
            return row
    raise RuntimeError("Missing cycle %s in %s" % (cycle, csv_path))


def block_dir(stage14, strategy, block_index, base_cycle, target_cycle, continue_to_cycle):
    return os.path.join(
        stage14,
        "strategy_%s" % strategy,
        "block%02d_base%d_target%d_to%d" % (block_index, base_cycle, target_cycle, continue_to_cycle),
    )


def previous_route_path(stage14, strategy, block_index, routes):
    if block_index <= 1:
        return None
    prev = routes[block_index - 2]
    prev_dir = block_dir(stage14, strategy, block_index - 1, prev["base"], prev["target"], prev["continue"])
    return os.path.join(prev_dir, "route_history_until_cycle%d.csv" % prev["continue"])


def choose_prediction_source(args, stage14, routes):
    ref_csv = os.path.join(
        stage14,
        "reference_2000cycles",
        "chaboche_vp_v1_cyclic_eps005_2000cycles_cycle_history.csv",
    )
    if args.base_source == "reference":
        rows = read_cycle_history(ref_csv)
        return ref_csv, rows, 2, 10
    route_csv = previous_route_path(stage14, args.strategy_label, args.block_index, routes)
    if not route_csv or not os.path.exists(route_csv):
        raise RuntimeError("Previous block route history is required but missing: %s" % route_csv)
    rows = read_cycle_history(route_csv)
    return route_csv, rows, args.base_cycle - 9, args.base_cycle


def compute_prediction(source_rows, source_csv, ref_rows, ref_csv, base_cycle, target_cycle, continue_to_cycle, mean_start, mean_end):
    base = get_cycle_row(source_rows, base_cycle, source_csv)
    exact_target = get_cycle_row(ref_rows, target_cycle, ref_csv)
    ref_continue = get_cycle_row(ref_rows, continue_to_cycle, ref_csv)
    window = [row for row in source_rows if mean_start <= row["cycle"] <= mean_end]
    if len(window) != 9:
        raise RuntimeError("Expected 9 rows in mean-increment window %d-%d, got %d" % (mean_start, mean_end, len(window)))
    delta_n = target_cycle - base_cycle

    pred_statev = {}
    pred_stress = {}
    statev_mean = {}
    stress_mean = {}
    for i in range(1, NSTATEV + 1):
        statev_mean[i] = mean([row["Delta_STATEV%d" % i] for row in window])
        pred_statev[i] = base["STATEV%d_end" % i] + delta_n * statev_mean[i]
    pred_statev[14] = QISO * (1.0 - math.exp(-BISO * pred_statev[1]))
    pred_statev[15] = 0.0

    for name in STRESS_COMPONENTS:
        stress_mean[name] = mean([row["Delta_%s" % name] for row in window])
        pred_stress[name] = base[name] + delta_n * stress_mean[name]

    return base, exact_target, ref_continue, pred_statev, pred_stress, statev_mean, stress_mean


def write_prediction_csvs(paths, base, exact, ref_continue, pred_statev, pred_stress, statev_mean, stress_mean, base_cycle, target_cycle, continue_to_cycle, mean_start, mean_end):
    delta_n = target_cycle - base_cycle
    mean_label = "mean_increment_cycles_%d_to_%d" % (mean_start, mean_end)

    with csv_open_write(paths["pred_statev"]) as handle:
        fields = ["variable", "value", "base_cycle_value", mean_label, "delta_n", "policy"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            writer.writerow({
                "variable": "STATEV%d_end" % i,
                "value": fmt(pred_statev[i]),
                "base_cycle_value": fmt(base["STATEV%d_end" % i]),
                mean_label: fmt(statev_mean[i]),
                "delta_n": delta_n,
                "policy": statev_policy(i),
            })

    with csv_open_write(paths["pred_stress"]) as handle:
        fields = ["component", "value", "base_cycle_value", mean_label, "delta_n", "policy"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name in STRESS_COMPONENTS:
            writer.writerow({
                "component": name,
                "value": fmt(pred_stress[name]),
                "base_cycle_value": fmt(base[name]),
                mean_label: fmt(stress_mean[name]),
                "delta_n": delta_n,
                "policy": "first_order_cycle_space",
            })

    with csv_open_write(paths["error"]) as handle:
        fields = ["quantity", "predicted_target", "reference_target", "absolute_error", "relative_error", "relative_error_percent", "policy"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            ref_value = exact["STATEV%d_end" % i]
            relative = rel_err(pred_statev[i], ref_value)
            writer.writerow({
                "quantity": "STATEV%d" % i,
                "predicted_target": fmt(pred_statev[i]),
                "reference_target": fmt(ref_value),
                "absolute_error": fmt(abs_err(pred_statev[i], ref_value)),
                "relative_error": fmt(relative),
                "relative_error_percent": fmt(None if relative is None else 100.0 * relative),
                "policy": statev_policy(i),
            })
        for name in STRESS_COMPONENTS:
            ref_value = exact[name]
            relative = rel_err(pred_stress[name], ref_value)
            writer.writerow({
                "quantity": name,
                "predicted_target": fmt(pred_stress[name]),
                "reference_target": fmt(ref_value),
                "absolute_error": fmt(abs_err(pred_stress[name], ref_value)),
                "relative_error": fmt(relative),
                "relative_error_percent": fmt(None if relative is None else 100.0 * relative),
                "policy": "first_order_cycle_space",
            })

    with csv_open_write(paths["reference"]) as handle:
        fields = ["quantity", "cycle%d_reference_value" % continue_to_cycle]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            writer.writerow({"quantity": "STATEV%d" % i, fields[1]: fmt(ref_continue["STATEV%d_end" % i])})
        for name in STRESS_COMPONENTS + ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]:
            writer.writerow({"quantity": name, fields[1]: fmt(ref_continue.get(name))})


def write_umat(source_umat, target_umat, pred_statev, pred_stress, target_cycle):
    with open(source_umat, "r") as handle:
        text = handle.read()
    text = re.sub(r"cycle-\d+", "cycle-%d" % target_cycle, text)
    text = re.sub(r"cycle \d+", "cycle %d" % target_cycle, text)
    text = re.sub(r"cycle\d+", "cycle%d" % target_cycle, text)
    text = text.replace("Stage 11B", "Stage 14")
    text = text.replace("Stage 13", "Stage 14")
    text = text.replace("Stage 12", "Stage 14")

    for index, name in enumerate(STRESS_COMPONENTS, start=1):
        pattern = r"(      IF \(NTENS\.GE\.%d\) SIGMA\(%d\) = )[-+0-9.DEde]+"
        text = re.sub(pattern % (index, index), r"\g<1>" + fortran_d(pred_stress[name]), text)

    comments = {
        1: "accumulated viscoplastic strain",
        2: "backstress X1",
        3: "backstress X2",
        4: "backstress X3",
        5: "near-zero shear component",
        6: "near-zero shear component",
        7: "near-zero shear component",
        8: "viscoplastic strain Ep1",
        9: "viscoplastic strain Ep2",
        10: "viscoplastic strain Ep3",
        11: "near-zero shear component",
        12: "near-zero shear component",
        13: "near-zero shear component",
        14: "recomputed isotropic hardening",
        15: "reset for injection",
    }
    for i in range(1, NSTATEV + 1):
        lhs = "      STATEV(%-2d) =" % i
        pattern = r"      STATEV\(\s*%d\s*\)\s*=\s*[-+0-9.DEde]+.*" % i
        text = re.sub(pattern, "%s %s       ! STATEV%d: %s" % (lhs, fortran_d(pred_statev[i]), i, comments[i]), text)
    with open(target_umat, "w") as handle:
        handle.write(text)


def amplitude_lines(continuation_cycles):
    lines = ["*AMPLITUDE, NAME=AMP_CYCLIC_10, DEFINITION=TABULAR"]
    for cycle in range(continuation_cycles):
        base = float(cycle)
        for t, a in [(base, 0.0), (base + 0.25, 1.0), (base + 0.50, 0.0), (base + 0.75, -1.0)]:
            lines.append("%.2f, %.1f" % (t, a))
    lines.append("%.2f, 0.0" % float(continuation_cycles))
    return lines


def write_deck(path, job, strategy, block_index, target_cycle, continue_to_cycle):
    continuation_cycles = continue_to_cycle - target_cycle
    if continuation_cycles != 10:
        raise RuntimeError("Stage 14 blocks must continue exactly 10 cycles; got %d" % continuation_cycles)
    lines = [
        "** Stage 14 blockwise controller: %s block %02d" % (strategy, block_index),
        "** Physical mapping: local time 0 -> cycle %d, local time 10 -> cycle %d" % (target_cycle, continue_to_cycle),
        "",
        "*HEADING",
        "Stage 14 %s block %02d: predicted cycle %d to %d" % (strategy, block_index, target_cycle, continue_to_cycle),
        "",
        "*PART, NAME=BLOCK",
        "*NODE",
        "1,0.0,0.0,0.0",
        "2,10.0,0.0,0.0",
        "3,10.0,2.0,0.0",
        "4,0.0,2.0,0.0",
        "5,0.0,0.0,2.0",
        "6,10.0,0.0,2.0",
        "7,10.0,2.0,2.0",
        "8,0.0,2.0,2.0",
        "*ELEMENT, TYPE=C3D8, ELSET=BLOCK",
        "1,1,2,3,4,5,6,7,8",
        "*SOLID SECTION, ELSET=BLOCK, MATERIAL=CHABOCHE_VP",
        "*END PART",
        "",
        "*ASSEMBLY, NAME=ASSEMBLY",
        "*INSTANCE, NAME=BLOCK_INST, PART=BLOCK",
        "*END INSTANCE",
        "*NSET, NSET=LEFT_FACE, INSTANCE=BLOCK_INST",
        "1,4,5,8",
        "*NSET, NSET=RIGHT_FACE, INSTANCE=BLOCK_INST",
        "2,3,6,7",
        "*END ASSEMBLY",
        "",
        "*MATERIAL, NAME=CHABOCHE_VP",
        "*DEPVAR",
        "15",
        "*USER MATERIAL, CONSTANTS=9",
        "** E, nu, sigma_y, Q, b, C, gamma, K, m",
        "210000.0, 0.3, 520.0, 200.0, 0.05, 120000.0, 800.0, 1000.0, 5.0",
        "",
    ]
    lines += amplitude_lines(continuation_cycles)
    lines += [
        "",
        "*INITIAL CONDITIONS, TYPE=SOLUTION, USER",
        "*INITIAL CONDITIONS, TYPE=STRESS, USER",
        "",
        "*STEP, NAME=CYCLIC_CONT_STAGE14_%s_BLOCK%02d, NLGEOM=NO, INC=1200" % (strategy.upper(), block_index),
        "*STATIC",
        "0.001, 10.0, 1.0E-08, 0.02",
        "",
        "*BOUNDARY",
        "LEFT_FACE, 1, 1, 0.0",
        "BLOCK_INST.1, 2, 3, 0.0",
        "BLOCK_INST.4, 3, 3, 0.0",
        "*BOUNDARY, AMPLITUDE=AMP_CYCLIC_10",
        "RIGHT_FACE, 1, 1, 0.05",
        "",
        "*OUTPUT, FIELD, FREQUENCY=1",
        "*NODE OUTPUT",
        "U, RF",
        "*ELEMENT OUTPUT",
        "S, SDV",
        "",
        "*OUTPUT, HISTORY, FREQUENCY=1",
        "*NODE OUTPUT, NSET=RIGHT_FACE",
        "U1, RF1",
        "",
        "*END STEP",
        "",
    ]
    with open(path, "w") as handle:
        handle.write("\n".join(lines))


def write_runner(path, job, inp, user):
    text = """@echo off
setlocal
cd /d %%~dp0

set "VSDEV=C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\Common7\\Tools\\VsDevCmd.bat"
set "SETVARS=C:\\Program Files (x86)\\Intel\\oneAPI\\setvars.bat"

call "%%VSDEV%%" -arch=amd64
if errorlevel 1 exit /b 1
call "%%SETVARS%%" intel64
if errorlevel 1 exit /b 1

abaqus job=%s_datacheck input=%s user=%s datacheck interactive ask_delete=OFF scratch=.
if errorlevel 1 exit /b 1

abaqus job=%s input=%s user=%s interactive ask_delete=OFF scratch=.
if errorlevel 1 exit /b 1

abaqus python postprocess_%s.py
if errorlevel 1 exit /b 1

endlocal
""" % (job, inp, user, job, inp, user, job)
    with open(path, "w") as handle:
        handle.write(text)


def write_postprocessor(path, job, strategy, block_index, target_cycle, continue_to_cycle, reference_csv, previous_route_csv, route_csv, result_csv, report_path):
    text = r'''from odbAccess import openOdb
import csv
import os
import sys

ODB_PATH = "__JOB__.odb"
REFERENCE_CSV_PATH = "__REFERENCE_CSV__"
PREVIOUS_ROUTE_CSV = "__PREVIOUS_ROUTE_CSV__"
ROUTE_CSV = "__ROUTE_CSV__"
RESULT_CSV = "__RESULT_CSV__"
REPORT_PATH = "__REPORT_PATH__"
STRATEGY = "__STRATEGY__"
BLOCK_INDEX = __BLOCK_INDEX__
TARGET_CYCLE = __TARGET_CYCLE__
CONTINUE_TO_CYCLE = __CONTINUE_TO_CYCLE__
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]
NSTATEV = 15


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


def maybe_float(text):
    if text is None or text == "":
        return None
    return float(text)


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / float(len(values)) if values else None


def rel_percent(value, ref):
    if value is None or ref is None or abs(ref) < 1.0e-30:
        return None
    return 100.0 * abs(value - ref) / abs(ref)


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


def frame_metrics(frame, physical_cycle, right_face):
    row = {"cycle": physical_cycle, "frame_time": frame.frameValue, "frame_time_error": frame.frameValue - float(physical_cycle - TARGET_CYCLE)}
    for i in range(1, NSTATEV + 1):
        row["STATEV%d_end" % i] = field_average(frame, "SDV%d" % i)
    stress = tensor_average(frame, "S")
    for name, value in zip(STRESS_COMPONENTS, stress):
        row[name] = value
    row["RIGHT_FACE_U1_AVG"] = nodal_component(frame, "U", right_face, 0, "mean")
    row["RIGHT_FACE_RF1_SUM"] = nodal_component(frame, "RF", right_face, 0, "sum")
    return row


def read_rows(path):
    rows = []
    if not path or path == "__NONE__" or not os.path.exists(path):
        return rows
    with open(path, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed = dict(row)
            parsed["cycle"] = int(row["cycle"])
            for i in range(1, NSTATEV + 1):
                parsed["STATEV%d_end" % i] = maybe_float(row.get("STATEV%d_end" % i))
                parsed["Delta_STATEV%d" % i] = maybe_float(row.get("Delta_STATEV%d" % i))
            for name in STRESS_COMPONENTS:
                parsed[name] = maybe_float(row.get(name))
                parsed["Delta_%s" % name] = maybe_float(row.get("Delta_%s" % name))
            parsed["RIGHT_FACE_U1_AVG"] = maybe_float(row.get("RIGHT_FACE_U1_AVG"))
            parsed["RIGHT_FACE_RF1_SUM"] = maybe_float(row.get("RIGHT_FACE_RF1_SUM"))
            rows.append(parsed)
    return rows


def reference_row(cycle):
    with open(REFERENCE_CSV_PATH, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if int(row["cycle"]) == cycle:
                return row
    raise RuntimeError("Missing reference cycle %d" % cycle)


def collect_current_rows():
    odb = openOdb(ODB_PATH, readOnly=True)
    try:
        step = odb.steps[list(odb.steps.keys())[-1]]
        frames = [(frame.frameValue, frame) for frame in step.frames]
        right_face = find_node_set(odb, "RIGHT_FACE")
        rows = []
        for physical_cycle in range(TARGET_CYCLE, CONTINUE_TO_CYCLE + 1):
            local_time = float(physical_cycle - TARGET_CYCLE)
            frame_time, frame = min(frames, key=lambda item: abs(item[0] - local_time))
            rows.append(frame_metrics(frame, physical_cycle, right_face))
        return rows
    finally:
        odb.close()


def recompute_deltas(rows):
    rows.sort(key=lambda item: item["cycle"])
    previous = None
    for row in rows:
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
        previous = row
    return rows


def outcome(statev, s11, rf1):
    if statev is not None and statev <= 1.0 and s11 is not None and s11 <= 1.0 and rf1 is not None and rf1 <= 1.0:
        return "accepted_clean_success"
    if statev is not None and statev <= 1.0:
        return "accepted_exploratory_success"
    return "not_accepted"


def main():
    previous_rows = read_rows(PREVIOUS_ROUTE_CSV)
    current_rows = collect_current_rows()
    by_cycle = {}
    for row in previous_rows + current_rows:
        by_cycle[int(row["cycle"])] = row
    route_rows = recompute_deltas(list(by_cycle.values()))

    fields = ["cycle", "frame_time", "frame_time_error"]
    fields += ["STATEV%d_end" % i for i in range(1, NSTATEV + 1)]
    fields += ["Delta_STATEV%d" % i for i in range(1, NSTATEV + 1)]
    fields += STRESS_COMPONENTS
    fields += ["Delta_%s" % name for name in STRESS_COMPONENTS]
    fields += ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]

    with csv_open_write(ROUTE_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in route_rows:
            writer.writerow(dict((field, fmt(row.get(field))) for field in fields))

    final = [row for row in route_rows if int(row["cycle"]) == CONTINUE_TO_CYCLE][0]
    ref = reference_row(CONTINUE_TO_CYCLE)
    statev_err = rel_percent(final["STATEV1_end"], float(ref["STATEV1_end"]))
    s11_err = rel_percent(final["S11"], float(ref["S11"]))
    rf1_err = rel_percent(final["RIGHT_FACE_RF1_SUM"], float(ref["RIGHT_FACE_RF1_SUM"]))
    final_outcome = outcome(statev_err, s11_err, rf1_err)

    result_fields = [
        "strategy", "block_index", "continue_to_cycle",
        "block_final_STATEV1", "reference_STATEV1", "block_final_statev1_error_pct",
        "block_final_S11", "reference_S11", "block_final_s11_error_pct",
        "block_final_RIGHT_FACE_RF1_SUM", "reference_RIGHT_FACE_RF1_SUM", "block_final_rf1_error_pct",
        "outcome",
    ]
    with csv_open_write(RESULT_CSV) as handle:
        writer = csv.DictWriter(handle, fieldnames=result_fields)
        writer.writeheader()
        writer.writerow({
            "strategy": STRATEGY,
            "block_index": BLOCK_INDEX,
            "continue_to_cycle": CONTINUE_TO_CYCLE,
            "block_final_STATEV1": fmt(final["STATEV1_end"]),
            "reference_STATEV1": fmt(float(ref["STATEV1_end"])),
            "block_final_statev1_error_pct": fmt(statev_err),
            "block_final_S11": fmt(final["S11"]),
            "reference_S11": fmt(float(ref["S11"])),
            "block_final_s11_error_pct": fmt(s11_err),
            "block_final_RIGHT_FACE_RF1_SUM": fmt(final["RIGHT_FACE_RF1_SUM"]),
            "reference_RIGHT_FACE_RF1_SUM": fmt(float(ref["RIGHT_FACE_RF1_SUM"])),
            "block_final_rf1_error_pct": fmt(rf1_err),
            "outcome": final_outcome,
        })

    lines = [
        "# Stage 14 %s Block %02d Result Report" % (STRATEGY, BLOCK_INDEX),
        "",
        "- Continue-to cycle: `%d`" % CONTINUE_TO_CYCLE,
        "- Block final STATEV1 error percent: `%s`" % fmt(statev_err),
        "- Block final S11 error percent: `%s`" % fmt(s11_err),
        "- Block final RF1 error percent: `%s`" % fmt(rf1_err),
        "- Outcome at this block: `%s`" % final_outcome,
        "- Route history: `%s`" % ROUTE_CSV,
    ]
    with open(REPORT_PATH, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")
    print("Wrote %s" % ROUTE_CSV)
    print("Wrote %s" % RESULT_CSV)
    print("Wrote %s" % REPORT_PATH)


if __name__ == "__main__":
    main()
'''
    replacements = {
        "__JOB__": job,
        "__REFERENCE_CSV__": reference_csv.replace("\\", "/"),
        "__PREVIOUS_ROUTE_CSV__": (previous_route_csv or "__NONE__").replace("\\", "/"),
        "__ROUTE_CSV__": route_csv,
        "__RESULT_CSV__": result_csv,
        "__REPORT_PATH__": report_path,
        "__STRATEGY__": strategy,
        "__BLOCK_INDEX__": str(block_index),
        "__TARGET_CYCLE__": str(target_cycle),
        "__CONTINUE_TO_CYCLE__": str(continue_to_cycle),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    with open(path, "w") as handle:
        handle.write(text)


def read_pre_errors(path):
    statev = None
    s11 = None
    with open(path, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["quantity"] == "STATEV1":
                statev = maybe_float(row.get("relative_error_percent"))
            if row["quantity"] == "S11":
                s11 = maybe_float(row.get("relative_error_percent"))
    return statev, s11


def write_prep_report(path, strategy, block_index, base_cycle, target_cycle, continue_to_cycle, base_source, source_csv, mean_start, mean_end, pred_statev, pred_stress, exact, ref_continue):
    statev_rel = 100.0 * rel_err(pred_statev[1], exact["STATEV1_end"])
    s11_rel = 100.0 * rel_err(pred_stress["S11"], exact["S11"])
    lines = [
        "# Stage 14 %s Block %02d Prep Report" % (strategy, block_index),
        "",
        "## Route",
        "",
        "- Base cycle: `%d`" % base_cycle,
        "- Predicted target cycle: `%d`" % target_cycle,
        "- Continue-to cycle: `%d`" % continue_to_cycle,
        "- DeltaN: `%d`" % (target_cycle - base_cycle),
        "- Skipped intermediate cycles: `%d`" % (target_cycle - base_cycle - 1),
        "- Recovery cycles: `%d`" % (continue_to_cycle - target_cycle),
        "",
        "## Prediction Source",
        "",
        "- Base source: `%s`" % base_source,
        "- Source CSV: `%s`" % source_csv,
        "- Mean increment window: `%d-%d`" % (mean_start, mean_end),
        "",
        "## Pre-Target Errors Against No-Skip Reference",
        "",
        "- Predicted STATEV1: `%s`" % fmt(pred_statev[1]),
        "- Reference target STATEV1: `%s`" % fmt(exact["STATEV1_end"]),
        "- STATEV1 relative error: `%s%%`" % fmt(statev_rel),
        "- Predicted S11: `%s MPa`" % fmt(pred_stress["S11"]),
        "- Reference target S11: `%s MPa`" % fmt(exact["S11"]),
        "- S11 relative error: `%s%%`" % fmt(s11_rel),
        "",
        "## Continue-To Reference",
        "",
        "- Reference STATEV1: `%s`" % fmt(ref_continue["STATEV1_end"]),
        "- Reference S11: `%s MPa`" % fmt(ref_continue["S11"]),
        "- Reference RIGHT_FACE_RF1_SUM: `%s`" % fmt(ref_continue.get("RIGHT_FACE_RF1_SUM")),
    ]
    with open(path, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def validate_deck(path):
    text = open(path, "r").read()
    if "0.001, 10.0, 1.0E-08, 0.02" not in text:
        raise RuntimeError("Generated block deck missing Stage 14 static line.")
    if "INC=1200" not in text.upper():
        raise RuntimeError("Generated block deck missing INC=1200.")
    if "*AMPLITUDE, NAME=AMP_CYCLIC_10, DEFINITION=TABULAR" not in text:
        raise RuntimeError("Generated block deck missing AMP_CYCLIC_10.")
    if "10.00, 0.0" not in text:
        raise RuntimeError("Generated block deck amplitude does not end at 10.00, 0.0.")
    if "TIME MARKS=YES" in text.upper():
        raise RuntimeError("Generated block deck unexpectedly contains TIME MARKS=YES.")


def create_block(args):
    repo = os.path.abspath(args.repo_root)
    stage14 = os.path.join(repo, "runs", "chaboche_umat", "stage14_blockwise_jump_2000cycles")
    if args.strategy_label not in STRATEGIES:
        raise RuntimeError("Unknown strategy: %s" % args.strategy_label)
    routes = STRATEGIES[args.strategy_label]
    if args.block_index < 1 or args.block_index > len(routes):
        raise RuntimeError("Invalid block index %d for strategy %s" % (args.block_index, args.strategy_label))
    expected = routes[args.block_index - 1]
    if expected["base"] != args.base_cycle or expected["target"] != args.target_cycle or expected["continue"] != args.continue_to_cycle:
        raise RuntimeError("Provided block route does not match STRATEGIES definition.")

    reference_csv = os.path.join(stage14, "reference_2000cycles", "chaboche_vp_v1_cyclic_eps005_2000cycles_cycle_history.csv")
    source_umat = os.path.join(stage14, "reference_2000cycles", "umat_chaboche_v1_with_sdvini_sigini.f")
    if not os.path.exists(reference_csv):
        raise RuntimeError("Missing Stage 14A reference CSV: %s" % reference_csv)
    if not os.path.exists(source_umat):
        raise RuntimeError("Missing source UMAT: %s" % source_umat)

    case_dir = block_dir(stage14, args.strategy_label, args.block_index, args.base_cycle, args.target_cycle, args.continue_to_cycle)
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)

    job = "chaboche_stage14_%s_block%02d_target%d_to%d" % (args.strategy_label, args.block_index, args.target_cycle, args.continue_to_cycle)
    previous_csv = previous_route_path(stage14, args.strategy_label, args.block_index, routes)
    route_csv_name = "route_history_until_cycle%d.csv" % args.continue_to_cycle
    result_csv_name = "stage14_%s_block%02d_result.csv" % (args.strategy_label, args.block_index)
    prep_report_name = "STAGE14_%s_BLOCK%02d_PREP_REPORT.md" % (args.strategy_label.upper(), args.block_index)
    result_report_name = "STAGE14_%s_BLOCK%02d_RESULT_REPORT.md" % (args.strategy_label.upper(), args.block_index)
    post_name = "postprocess_%s.py" % job

    paths = {
        "pred_statev": os.path.join(case_dir, "cycle%d_predicted_statev_for_injection.csv" % args.target_cycle),
        "pred_stress": os.path.join(case_dir, "cycle%d_predicted_stress_for_injection.csv" % args.target_cycle),
        "error": os.path.join(case_dir, "cycle%d_predicted_vs_reference_error.csv" % args.target_cycle),
        "reference": os.path.join(case_dir, "cycle%d_reference_statev_stress.csv" % args.continue_to_cycle),
        "umat": os.path.join(case_dir, "umat_chaboche_v1_with_sdvini_sigini_predicted_cycle%d.f" % args.target_cycle),
        "deck": os.path.join(case_dir, job + ".inp"),
        "runner": os.path.join(case_dir, "run_stage14_%s_block%02d_target%d_to%d.bat" % (args.strategy_label, args.block_index, args.target_cycle, args.continue_to_cycle)),
        "post": os.path.join(case_dir, post_name),
        "prep_report": os.path.join(case_dir, prep_report_name),
        "result_report": os.path.join(case_dir, result_report_name),
        "route_csv": os.path.join(case_dir, route_csv_name),
        "result_csv": os.path.join(case_dir, result_csv_name),
    }

    ref_rows = read_cycle_history(reference_csv)
    source_csv, source_rows, mean_start, mean_end = choose_prediction_source(args, stage14, routes)
    base, exact, ref_continue, pred_statev, pred_stress, statev_mean, stress_mean = compute_prediction(
        source_rows, source_csv, ref_rows, reference_csv, args.base_cycle, args.target_cycle, args.continue_to_cycle, mean_start, mean_end
    )

    write_prediction_csvs(paths, base, exact, ref_continue, pred_statev, pred_stress, statev_mean, stress_mean, args.base_cycle, args.target_cycle, args.continue_to_cycle, mean_start, mean_end)
    write_umat(source_umat, paths["umat"], pred_statev, pred_stress, args.target_cycle)
    write_deck(paths["deck"], job, args.strategy_label, args.block_index, args.target_cycle, args.continue_to_cycle)
    write_runner(paths["runner"], job, os.path.basename(paths["deck"]), os.path.basename(paths["umat"]))
    write_postprocessor(paths["post"], job, args.strategy_label, args.block_index, args.target_cycle, args.continue_to_cycle, reference_csv, previous_csv if args.block_index > 1 else None, paths["route_csv"], paths["result_csv"], result_report_name)
    write_prep_report(paths["prep_report"], args.strategy_label, args.block_index, args.base_cycle, args.target_cycle, args.continue_to_cycle, args.base_source, source_csv, mean_start, mean_end, pred_statev, pred_stress, exact, ref_continue)
    validate_deck(paths["deck"])

    subprocess.check_call([sys.executable, "-m", "py_compile", paths["post"]])
    for key in ["pred_statev", "pred_stress", "error", "reference", "umat", "deck", "runner", "post", "prep_report"]:
        print("Wrote %s" % paths[key])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy-label", required=True)
    parser.add_argument("--block-index", type=int, required=True)
    parser.add_argument("--base-cycle", type=int, required=True)
    parser.add_argument("--target-cycle", type=int, required=True)
    parser.add_argument("--continue-to-cycle", type=int, required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--base-source", choices=["reference", "previous_block"], required=True)
    args = parser.parse_args()
    create_block(args)


if __name__ == "__main__":
    main()
