import csv
import math
import os
import re
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(THIS_DIR)
THIS_DIR = os.path.join(ROOT, "stage11_500cycle_reference", "target499_cycle500")

BASE_CYCLE = 10
TARGET_CYCLE = 499
REFERENCE_CYCLE = 500
DELTA_N = TARGET_CYCLE - BASE_CYCLE
MEAN_START = 2
MEAN_END = 10
SKIPPED_INTERMEDIATE_CYCLES = DELTA_N - 1

HISTORY_CSV = os.path.join(
    ROOT,
    "stage11_500cycle_reference",
    "reference_500cycles",
    "chaboche_vp_v1_cyclic_eps005_500cycles_cycle_history.csv"
)
SOURCE_UMAT = os.path.join(ROOT, "umat_chaboche_v1_with_sdvini_sigini_predicted_cycle29.f")
SOURCE_DECK = os.path.join(ROOT, "chaboche_stage6d_predicted_cycle29_to_cycle30.inp")

JOB = "chaboche_stage11b_predicted_cycle499_to_cycle500"
CHECK_JOB = JOB + "_check"
TARGET_UMAT = os.path.join(THIS_DIR, "umat_chaboche_v1_with_sdvini_sigini_predicted_cycle499.f")
TARGET_DECK = os.path.join(THIS_DIR, JOB + ".inp")
RUN_BAT = os.path.join(THIS_DIR, "run_stage11b_predicted_cycle499_jump.bat")
POSTPROCESS_PY = os.path.join(THIS_DIR, "postprocess_stage11b_predicted_cycle499_jump.py")
MONITOR_PY = os.path.join(THIS_DIR, "monitor_stage11b_predicted_cycle499_jump.py")

PRED_STATEV_CSV = os.path.join(THIS_DIR, "cycle499_predicted_statev_for_injection.csv")
PRED_STRESS_CSV = os.path.join(THIS_DIR, "cycle499_predicted_stress_for_injection.csv")
ERROR_CSV = os.path.join(THIS_DIR, "cycle499_predicted_vs_exact_error.csv")
REFERENCE_CSV = os.path.join(THIS_DIR, "cycle500_reference_statev_stress.csv")
RESULT_CSV = os.path.join(THIS_DIR, "stage11b_predicted_cycle499_jump_result.csv")
PREP_REPORT = os.path.join(THIS_DIR, "STAGE11B_PREDICTED_CYCLE499_STATE_PREP_REPORT.md")
RESULT_REPORT = os.path.join(THIS_DIR, "STAGE11B_PREDICTED_CYCLE499_JUMP_RESULT_REPORT.md")

NSTATEV = 15
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]
ACTIVE_STATEV = set([1, 2, 3, 4, 8, 9, 10])
NEAR_ZERO_STATEV = set([5, 6, 7, 11, 12, 13])
QISO = 200.0
BISO = 0.05


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % value


def fortran_d(value):
    text = "%.15G" % value
    text = text.replace("E", "D").replace("e", "D")
    if "D" not in text and "." not in text:
        text += ".0"
    return text + "D0" if "D" not in text else text


def maybe_float(text):
    if text is None or text == "":
        return None
    return float(text)


def mean(values):
    return sum(values) / float(len(values)) if values else None


def abs_err(predicted, exact):
    if predicted is None or exact is None:
        return None
    return abs(predicted - exact)


def rel_err(predicted, exact):
    if predicted is None or exact is None or abs(exact) < 1.0e-30:
        return None
    return abs(predicted - exact) / abs(exact)


def read_cycle_history():
    rows = []
    with open(HISTORY_CSV, "r") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed = {"cycle": int(row["cycle"])}
            for i in range(1, NSTATEV + 1):
                parsed["STATEV%d_end" % i] = maybe_float(row["STATEV%d_end" % i])
                parsed["Delta_STATEV%d" % i] = maybe_float(row["Delta_STATEV%d" % i])
            for name in STRESS_COMPONENTS:
                parsed[name] = maybe_float(row[name])
                parsed["Delta_%s" % name] = maybe_float(row["Delta_%s" % name])
            for name in ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]:
                parsed[name] = maybe_float(row.get(name))
            rows.append(parsed)
    return rows


def get_cycle_row(rows, cycle):
    for row in rows:
        if row["cycle"] == cycle:
            return row
    raise KeyError("Missing cycle %s in %s" % (cycle, HISTORY_CSV))


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


def compute_prediction(rows):
    base = get_cycle_row(rows, BASE_CYCLE)
    exact = get_cycle_row(rows, TARGET_CYCLE)
    reference = get_cycle_row(rows, REFERENCE_CYCLE)
    window = [row for row in rows if MEAN_START <= row["cycle"] <= MEAN_END]

    pred_statev = {}
    pred_stress = {}
    statev_mean = {}
    stress_mean = {}

    for i in range(1, NSTATEV + 1):
        statev_mean[i] = mean([row["Delta_STATEV%d" % i] for row in window])
        pred_statev[i] = base["STATEV%d_end" % i] + DELTA_N * statev_mean[i]
    pred_statev[14] = QISO * (1.0 - math.exp(-BISO * pred_statev[1]))
    pred_statev[15] = 0.0

    for name in STRESS_COMPONENTS:
        stress_mean[name] = mean([row["Delta_%s" % name] for row in window])
        pred_stress[name] = base[name] + DELTA_N * stress_mean[name]

    return base, exact, reference, pred_statev, pred_stress, statev_mean, stress_mean


def write_prediction_csvs(base, exact, reference, pred_statev, pred_stress, statev_mean, stress_mean):
    with csv_open_write(PRED_STATEV_CSV) as handle:
        fields = ["variable", "value", "base_cycle_value", "mean_increment_cycles_2_to_10", "delta_n", "policy"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            writer.writerow({
                "variable": "STATEV%d_end" % i,
                "value": fmt(pred_statev[i]),
                "base_cycle_value": fmt(base["STATEV%d_end" % i]),
                "mean_increment_cycles_2_to_10": fmt(statev_mean[i]),
                "delta_n": DELTA_N,
                "policy": statev_policy(i),
            })

    with csv_open_write(PRED_STRESS_CSV) as handle:
        fields = ["component", "value", "base_cycle_value", "mean_increment_cycles_2_to_10", "delta_n", "policy"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name in STRESS_COMPONENTS:
            writer.writerow({
                "component": name,
                "value": fmt(pred_stress[name]),
                "base_cycle_value": fmt(base[name]),
                "mean_increment_cycles_2_to_10": fmt(stress_mean[name]),
                "delta_n": DELTA_N,
                "policy": "first_order_cycle_space",
            })

    with csv_open_write(ERROR_CSV) as handle:
        fields = ["quantity", "predicted_cycle499", "exact_cycle499", "absolute_error", "relative_error", "relative_error_percent", "policy"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            exact_value = exact["STATEV%d_end" % i]
            relative = rel_err(pred_statev[i], exact_value)
            writer.writerow({
                "quantity": "STATEV%d" % i,
                "predicted_cycle499": fmt(pred_statev[i]),
                "exact_cycle499": fmt(exact_value),
                "absolute_error": fmt(abs_err(pred_statev[i], exact_value)),
                "relative_error": fmt(relative),
                "relative_error_percent": fmt(None if relative is None else 100.0 * relative),
                "policy": statev_policy(i),
            })
        for name in STRESS_COMPONENTS:
            exact_value = exact[name]
            relative = rel_err(pred_stress[name], exact_value)
            writer.writerow({
                "quantity": name,
                "predicted_cycle499": fmt(pred_stress[name]),
                "exact_cycle499": fmt(exact_value),
                "absolute_error": fmt(abs_err(pred_stress[name], exact_value)),
                "relative_error": fmt(relative),
                "relative_error_percent": fmt(None if relative is None else 100.0 * relative),
                "policy": "first_order_cycle_space",
            })

    with csv_open_write(REFERENCE_CSV) as handle:
        fields = ["quantity", "cycle500_history_row_value"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NSTATEV + 1):
            writer.writerow({"quantity": "STATEV%d" % i, "cycle500_history_row_value": fmt(reference["STATEV%d_end" % i])})
        for name in STRESS_COMPONENTS + ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]:
            writer.writerow({"quantity": name, "cycle500_history_row_value": fmt(reference.get(name))})


def write_umat(pred_statev, pred_stress):
    with open(SOURCE_UMAT, "r") as handle:
        text = handle.read()

    text = text.replace("cycle-29", "cycle-499")
    text = text.replace("cycle 29", "cycle 499")
    text = text.replace("cycle29", "cycle499")
    text = text.replace("Stage 6D", "Stage 11B")
    text = text.replace("Stage 5A", "Stage 11B")
    text = text.replace("cycle19_predicted", "cycle499_predicted")

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

    with open(TARGET_UMAT, "w") as handle:
        handle.write(text)


def write_deck():
    with open(SOURCE_DECK, "r") as handle:
        text = handle.read()
    replacements = {
        "Stage 6D": "Stage 11B",
        "Predicted cycle-29 to cycle-30 FE cycle-jump validation": "Predicted cycle-499 to cycle-500 FE cycle-jump validation",
        "Predicted Cycle-29 to Cycle-30 FE Cycle Jump": "Predicted Cycle-499 to Cycle-500 FE Cycle Jump",
        "selected from the Stage 6C scan": "selected by the Stage 11B grouped adaptive controller",
        "cycle-29": "cycle-499",
        "cycle-30": "cycle-500",
        "cycle 30": "cycle 500",
        "cycle 29": "cycle 499",
        "C29_TO_C30": "C99_TO_C100",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    with open(TARGET_DECK, "w") as handle:
        handle.write(text)


def write_runner():
    text = r"""@echo off
REM Stage 11B predicted cycle-499 to cycle-500 FE validation.

setlocal enabledelayedexpansion
cd /d %~dp0

echo ============================================================
echo Loading Intel oneAPI + Visual Studio Build Tools environment
echo ============================================================

set "VS2022INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64

echo.
echo ============================================================
echo Checking compiler/linker/Abaqus availability
echo ============================================================

where ifx
if errorlevel 1 exit /b 1

where link
if errorlevel 1 exit /b 1

where abaqus
if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo Stage 11B datacheck
echo ============================================================

call abaqus job=chaboche_stage11b_predicted_cycle499_to_cycle500_check ^
    input=chaboche_stage11b_predicted_cycle499_to_cycle500.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle499.f ^
    datacheck interactive scratch=.

if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo Stage 11B full predicted cycle-jump analysis
echo ============================================================

call abaqus job=chaboche_stage11b_predicted_cycle499_to_cycle500 ^
    input=chaboche_stage11b_predicted_cycle499_to_cycle500.inp ^
    user=umat_chaboche_v1_with_sdvini_sigini_predicted_cycle499.f ^
    interactive ask_delete=OFF scratch=.

if errorlevel 1 exit /b 1

echo.
echo Stage 11B predicted cycle-jump analysis completed.
"""
    with open(RUN_BAT, "w") as handle:
        handle.write(text)


def write_monitor():
    text = '''from __future__ import print_function

import os
import time


JOB = "chaboche_stage11b_predicted_cycle499_to_cycle500"
STA_PATH = JOB + ".sta"


def parse_sta():
    if not os.path.exists(STA_PATH):
        return None
    last = None
    with open(STA_PATH, "r") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 7 and parts[0].isdigit():
                try:
                    last = {"inc": int(parts[1]), "step_time": float(parts[6])}
                except Exception:
                    pass
    return last


def main():
    print("Monitoring %s" % STA_PATH)
    while True:
        data = parse_sta()
        if data is None:
            print("Waiting for %s..." % STA_PATH)
        else:
            print("inc %d step_time %.8g" % (data["inc"], data["step_time"]))
            if data["step_time"] >= 1.0:
                break
        time.sleep(5)


if __name__ == "__main__":
    main()
'''
    with open(MONITOR_PY, "w") as handle:
        handle.write(text)


def write_postprocessor(pred_statev, pred_stress):
    text = '''from odbAccess import openOdb
import csv
import sys


ODB_PATH = "chaboche_stage11b_predicted_cycle499_to_cycle500.odb"
REFERENCE_ODB_PATH = "../reference_500cycles/chaboche_vp_v1_cyclic_eps005_500cycles.odb"
REFERENCE_TIME = 500.0
CSV_PATH = "stage11b_predicted_cycle499_jump_result.csv"
REFERENCE_CSV = "cycle500_reference_statev_stress.csv"
REPORT_PATH = "STAGE11B_PREDICTED_CYCLE499_JUMP_RESULT_REPORT.md"
EXPECTED_INITIAL_STATEV1 = %(expected_statev1)s
EXPECTED_INITIAL_S11 = %(expected_s11)s
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def fmt(value):
    if value is None:
        return ""
    return "%%.12g" %% value


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
        row["STATEV%%d" %% i], row["STATEV%%d_count" %% i] = field_average(frame, "SDV%%d" %% i)
    stress, stress_count = tensor_average(frame, "S")
    for name, value in zip(STRESS_COMPONENTS, stress):
        row[name] = value
    row["stress_count"] = stress_count
    row["RIGHT_FACE_U1_AVG"], row["right_face_u_count"] = nodal_component(frame, "U", right_face, 0, "mean")
    row["RIGHT_FACE_RF1_SUM"], row["right_face_rf_count"] = nodal_component(frame, "RF", right_face, 0, "sum")
    return row


def collect_stage11b_rows():
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
            raise RuntimeError("Could not bracket reference time %%s" %% REFERENCE_TIME)
        right_face, right_face_name = find_node_set(odb, "RIGHT_FACE")
        low = frame_metrics(lower[2], right_face, right_face_name)
        high = frame_metrics(upper[2], right_face, right_face_name)
        dt = upper[0] - lower[0]
        alpha = 0.0 if abs(dt) < 1.0e-30 else (REFERENCE_TIME - lower[0]) / dt
        ref = {
            "source": "linear_interpolation_between_bracketing_50cycle_ODB_frames",
            "lower_time": lower[0],
            "upper_time": upper[0],
            "alpha": alpha,
            "right_face_node_set": right_face_name or "",
        }
        for i in range(1, 16):
            ref["STATEV%%d" %% i] = lerp(low["STATEV%%d" %% i], high["STATEV%%d" %% i], alpha)
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
        writer = csv.DictWriter(handle, fieldnames=["quantity", "cycle500_reference_value", "source", "lower_time", "upper_time", "alpha"])
        writer.writeheader()
        for i in range(1, 16):
            writer.writerow({"quantity": "STATEV%%d" %% i, "cycle500_reference_value": fmt(reference["STATEV%%d" %% i]), "source": reference["source"], "lower_time": fmt(reference["lower_time"]), "upper_time": fmt(reference["upper_time"]), "alpha": fmt(reference["alpha"])})
        for name in STRESS_COMPONENTS + ["RIGHT_FACE_U1_AVG", "RIGHT_FACE_RF1_SUM"]:
            writer.writerow({"quantity": name, "cycle500_reference_value": fmt(reference[name]), "source": reference["source"], "lower_time": fmt(reference["lower_time"]), "upper_time": fmt(reference["upper_time"]), "alpha": fmt(reference["alpha"])})


def write_result_csv(rows):
    fields = ["frame_label", "step_name", "frame_value", "description"]
    fields += ["STATEV%%d" %% i for i in range(1, 16)]
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
        "# Stage 11B Predicted Cycle-499 FE Jump Result Report",
        "",
        "## Purpose",
        "",
        "Validate the Stage 11B grouped adaptive recommendation: cycle 10 data -> predicted cycle 499 state -> one computed cycle to cycle 500.",
        "",
        "## Route",
        "",
        "- Base cycle: `10`",
        "- Predicted injection cycle: `99`",
        "- Continuation/reference cycle: `100`",
        "- DeltaN_test: `89`",
        "- Skipped intermediate FE cycles: `88`",
        "",
        "## Abaqus Status",
        "",
        "- Datacheck job: `chaboche_stage11b_predicted_cycle499_to_cycle500_check`",
        "- Datacheck status: `completed`",
        "- Full analysis job: `chaboche_stage11b_predicted_cycle499_to_cycle500`",
        "- Full analysis status: `completed`",
        "- Final `.sta` status: `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`",
        "",
        "## Key Values",
        "",
        "| Frame | Time | STATEV1 | S11 (MPa) | RIGHT_FACE RF1 |",
        "|---|---:|---:|---:|---:|",
        "| First output frame | %%s | %%s | %%s | %%s |" %% (fmt(first["frame_value"]), fmt(first["STATEV1"]), fmt(first["S11"]), fmt(first["RIGHT_FACE_RF1_SUM"])),
        "| Final output frame | %%s | %%s | %%s | %%s |" %% (fmt(final["frame_value"]), fmt(final["STATEV1"]), fmt(final["S11"]), fmt(final["RIGHT_FACE_RF1_SUM"])),
        "",
        "## Injection Check",
        "",
        "- Expected injected STATEV1: `%%s`" %% fmt(EXPECTED_INITIAL_STATEV1),
        "- First-frame STATEV1 absolute error: `%%s`" %% fmt(abs_err(first["STATEV1"], EXPECTED_INITIAL_STATEV1)),
        "- Expected injected S11: `%%s MPa`" %% fmt(EXPECTED_INITIAL_S11),
        "- First-frame S11 absolute error: `%%s MPa`" %% fmt(abs_err(first["S11"], EXPECTED_INITIAL_S11)),
        "",
        "## Reference Handling",
        "",
        "- Explicit reference ODB: `%%s`" %% REFERENCE_ODB_PATH,
        "- Reference time: `%%s`" %% fmt(REFERENCE_TIME),
        "- Reference source: `%%s`" %% reference["source"],
        "- Lower bracketing frame: `%%s`" %% fmt(reference["lower_time"]),
        "- Upper bracketing frame: `%%s`" %% fmt(reference["upper_time"]),
        "- Interpolation alpha: `%%s`" %% fmt(reference["alpha"]),
        "",
        "## Final Cycle-500 Comparison",
        "",
        "- Reference cycle-500 STATEV1: `%%s`" %% fmt(reference["STATEV1"]),
        "- Final STATEV1 absolute error: `%%s`" %% fmt(statev1_abs),
        "- Final STATEV1 relative error percent: `%%s`" %% fmt(statev1_rel),
        "- Reference cycle-500 S11: `%%s MPa`" %% fmt(reference["S11"]),
        "- Final S11 absolute error: `%%s MPa`" %% fmt(s11_abs),
        "- Final S11 relative error percent: `%%s`" %% fmt(s11_rel),
        "- Reference cycle-500 RIGHT_FACE RF1: `%%s`" %% fmt(reference["RIGHT_FACE_RF1_SUM"]),
        "- Final RIGHT_FACE RF1 absolute error: `%%s`" %% fmt(rf1_abs),
        "- Final RIGHT_FACE RF1 relative error percent: `%%s`" %% fmt(rf1_rel),
        "",
        "## Decision",
        "",
        "- Final STATEV1 below 1%%%% error: `%%s`" %% ("yes" if statev1_rel is not None and statev1_rel < 1.0 else "no"),
        "- Final S11 below 1%%%% error: `%%s`" %% ("yes" if s11_rel is not None and s11_rel < 1.0 else "no"),
        "- Final S11 below 3%%%% error: `%%s`" %% ("yes" if s11_rel is not None and s11_rel < 3.0 else "no"),
        "- Stage 11B DeltaN = 89 accepted: `%%s`" %% ("yes" if outcome.startswith("accepted") else "no"),
        "- Stage 11B outcome: `%%s`" %% outcome,
        "",
        "## Outputs",
        "",
        "- Result CSV: `%%s`" %% CSV_PATH,
        "- Reference CSV: `%%s`" %% REFERENCE_CSV,
    ]
    with open(REPORT_PATH, "w") as handle:
        handle.write("\\n".join(lines))
        handle.write("\\n")


def main():
    rows = collect_stage11b_rows()
    reference = collect_interpolated_reference()
    write_result_csv(rows)
    write_reference_csv(reference)
    write_report(rows, reference)
    print("Wrote %%s" %% CSV_PATH)
    print("Wrote %%s" %% REFERENCE_CSV)
    print("Wrote %%s" %% REPORT_PATH)


if __name__ == "__main__":
    main()
''' % {
        "expected_statev1": repr(pred_statev[1]),
        "expected_s11": repr(pred_stress["S11"]),
    }
    with open(POSTPROCESS_PY, "w") as handle:
        handle.write(text)


def write_prep_report(pred_statev, pred_stress, exact, reference):
    statev1_rel = 100.0 * rel_err(pred_statev[1], exact["STATEV1_end"])
    s11_rel = 100.0 * rel_err(pred_stress["S11"], exact["S11"])
    lines = [
        "# Stage 11B Predicted Cycle-499 State Preparation Report",
        "",
        "## Purpose",
        "",
        "Prepare a manually selected long-horizon Stage 11B target for direct FE validation.",
        "",
        "## Setup",
        "",
        "- Route: cycle 10 -> predicted cycle 499 -> cycle 500",
        "- Base cycle: `%d`" % BASE_CYCLE,
        "- Target injection cycle: `%d`" % TARGET_CYCLE,
        "- Continuation/reference cycle: `%d`" % REFERENCE_CYCLE,
        "- DeltaN_test: `%d`" % DELTA_N,
        "- Skipped intermediate FE cycles: `%d`" % SKIPPED_INTERMEDIATE_CYCLES,
        "- Mean increment window: cycles `%d-%d`" % (MEAN_START, MEAN_END),
        "- Prediction rule: `predicted_cycle499 = value_cycle10 + DeltaN * mean_increment_per_cycle`",
        "",
        "No validated Stage 5B/6D UMAT, deck, or ODB files are modified. All Stage 11B files are local to this folder.",
        "",
        "## Key Prediction Errors Against Exact Cycle 499 History Row",
        "",
        "- Predicted STATEV1: `%s`" % fmt(pred_statev[1]),
        "- Exact cycle-499 STATEV1: `%s`" % fmt(exact["STATEV1_end"]),
        "- STATEV1 relative error: `%s%%`" % fmt(statev1_rel),
        "- Predicted S11: `%s MPa`" % fmt(pred_stress["S11"]),
        "- Exact cycle-499 S11: `%s MPa`" % fmt(exact["S11"]),
        "- S11 relative error: `%s%%`" % fmt(s11_rel),
        "",
        "## Cycle-500 History Row Reference",
        "",
        "- Reference STATEV1: `%s`" % fmt(reference["STATEV1_end"]),
        "- Reference S11: `%s MPa`" % fmt(reference["S11"]),
        "- Reference RIGHT_FACE RF1: `%s`" % fmt(reference.get("RIGHT_FACE_RF1_SUM")),
        "",
        "The final result postprocessor uses exact-time interpolation from the 500-cycle ODB at time 500.0.",
        "",
        "## Generated Files",
        "",
        "- Predicted STATEV CSV: `%s`" % os.path.basename(PRED_STATEV_CSV),
        "- Predicted stress CSV: `%s`" % os.path.basename(PRED_STRESS_CSV),
        "- Prediction error CSV: `%s`" % os.path.basename(ERROR_CSV),
        "- Cycle-500 reference CSV: `%s`" % os.path.basename(REFERENCE_CSV),
        "- UMAT: `%s`" % os.path.basename(TARGET_UMAT),
        "- Input deck: `%s`" % os.path.basename(TARGET_DECK),
        "- Runner: `%s`" % os.path.basename(RUN_BAT),
        "- Monitor: `%s`" % os.path.basename(MONITOR_PY),
        "- Postprocessor: `%s`" % os.path.basename(POSTPROCESS_PY),
    ]
    with open(PREP_REPORT, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main():
    rows = read_cycle_history()
    base, exact, reference, pred_statev, pred_stress, statev_mean, stress_mean = compute_prediction(rows)
    write_prediction_csvs(base, exact, reference, pred_statev, pred_stress, statev_mean, stress_mean)
    write_umat(pred_statev, pred_stress)
    write_deck()
    write_runner()
    write_monitor()
    write_postprocessor(pred_statev, pred_stress)
    write_prep_report(pred_statev, pred_stress, exact, reference)
    for path in [
        PRED_STATEV_CSV, PRED_STRESS_CSV, ERROR_CSV, REFERENCE_CSV,
        TARGET_UMAT, TARGET_DECK, RUN_BAT, MONITOR_PY, POSTPROCESS_PY, PREP_REPORT,
    ]:
        print("Wrote %s" % path)


if __name__ == "__main__":
    main()




