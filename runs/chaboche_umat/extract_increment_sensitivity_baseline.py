from odbAccess import openOdb
import csv
import math
import os
import sys


DEFAULT_JOB = "chaboche_eps005_20cycles_dt_original_output"

JOB = DEFAULT_JOB
ODB_PATH = ""

OUT_DIR = "increment_sensitivity_study"
HISTORY_CSV = ""
SUMMARY_CSV = ""
REPORT = ""

NSTATEV = 15
SMALL_VALUE_TOL = 1.0e-10

ORIGINAL_VALIDATED_STATEV1 = 0.142025694251


def configure_paths(job_name):
    global JOB, ODB_PATH, HISTORY_CSV, SUMMARY_CSV, REPORT
    JOB = job_name
    ODB_PATH = JOB + ".odb"
    HISTORY_CSV = os.path.join(OUT_DIR, JOB + "_statev_history.csv")
    SUMMARY_CSV = os.path.join(OUT_DIR, JOB + "_summary.csv")
    REPORT = os.path.join(OUT_DIR, JOB + "_report.md")


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % value


def mean(values):
    return sum(values) / len(values) if values else 0.0


def csv_open_write(path):
    if sys.version_info[0] < 3:
        return open(path, "wb")
    return open(path, "w", newline="")


def avg_field(frame, field_name):
    if field_name not in frame.fieldOutputs.keys():
        raise KeyError("Missing field output: " + field_name)
    values = [v.data for v in frame.fieldOutputs[field_name].values]
    return mean(values), len(values)


def collect_frames():
    odb = openOdb(ODB_PATH)
    frames = []
    try:
        for step_name in odb.steps.keys():
            step = odb.steps[step_name]
            for frame in step.frames:
                frames.append((frame.frameValue, frame))
        frames.sort(key=lambda item: item[0])
        return odb, frames
    except Exception:
        odb.close()
        raise


def nearest_frame(frames, target_time):
    return min(frames, key=lambda item: abs(item[0] - target_time))


def extract_cycle_end_history():
    odb, frames = collect_frames()
    rows = []
    try:
        # cycle-0 baseline
        t0, f0 = nearest_frame(frames, 0.0)
        cycle_zero_values = {}
        for i in range(1, NSTATEV + 1):
            cycle_zero_values[i], _ = avg_field(f0, "SDV%d" % i)

        previous_values = cycle_zero_values
        for cycle in range(1, 21):
            target_time = float(cycle)
            nearest_time, frame = nearest_frame(frames, target_time)
            row = {
                "cycle": cycle,
                "time": nearest_time,
                "target_time": target_time,
                "time_error": nearest_time - target_time,
            }
            current_values = {}
            ip_count = None
            for i in range(1, NSTATEV + 1):
                value, count = avg_field(frame, "SDV%d" % i)
                current_values[i] = value
                row["STATEV%d_end" % i] = value
                row["Delta_STATEV%d" % i] = value - previous_values[i]
                if ip_count is None:
                    ip_count = count
            row["integration_point_values_averaged"] = ip_count
            rows.append(row)
            previous_values = current_values
    finally:
        odb.close()
    return rows


def write_history_csv(rows):
    fields = ["cycle", "time", "target_time", "time_error", "integration_point_values_averaged"]
    fields += ["STATEV%d_end" % i for i in range(1, NSTATEV + 1)]
    fields += ["Delta_STATEV%d" % i for i in range(1, NSTATEV + 1)]
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    with csv_open_write(HISTORY_CSV) as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([fmt(row[field]) if field not in ("cycle", "integration_point_values_averaged")
                             else row[field] for field in fields])


def write_summary_and_report(rows):
    final = rows[-1]
    # Prepare summary CSV (single-row with selected fields)
    summary_fields = [
        "JOB",
        "STATEV1_cycle20",
        "STATEV2_cycle20",
        "STATEV3_cycle20",
        "STATEV4_cycle20",
        "STATEV8_cycle20",
        "STATEV9_cycle20",
        "STATEV10_cycle20",
        "STATEV14_cycle20",
        "Avg_S11_cycle20",
        "RF1_RIGHT_FACE_cycle20",
    ]
    # Attempt to get Avg S11 and RF1 from the same final frame if available
    avg_s11 = None
    rf1_val = None
    try:
        # open odb to fetch S11 avg and RF1 history at RIGHT_FACE region
        odb = openOdb(ODB_PATH)
        try:
            # find last frame (nearest to cycle 20)
            step = list(odb.steps.values())[-1]
            frame = step.frames[-1]
            if "S" in frame.fieldOutputs.keys():
                # S is tensor field; average S[0] (S11)
                s_vals = [v.data[0] for v in frame.fieldOutputs["S"].values]
                if s_vals:
                    avg_s11 = mean(s_vals)
        except Exception:
            pass
        finally:
            odb.close()
    except Exception:
        avg_s11 = None

    # RF1 extraction via history output in the MSG or ODB historyOutputs may be present but complex; leave blank if not found

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    with csv_open_write(SUMMARY_CSV) as f:
        writer = csv.writer(f)
        writer.writerow(summary_fields)
        writer.writerow([
            JOB,
            fmt(final["STATEV1_end"]),
            fmt(final["STATEV2_end"]),
            fmt(final["STATEV3_end"]),
            fmt(final["STATEV4_end"]),
            fmt(final["STATEV8_end"]),
            fmt(final["STATEV9_end"]),
            fmt(final["STATEV10_end"]),
            fmt(final["STATEV14_end"]),
            fmt(avg_s11),
            fmt(rf1_val),
        ])

    # Write Markdown report
    abs_diff = None
    rel_pct = None
    try:
        statev1 = float(final["STATEV1_end"])
        abs_diff = abs(statev1 - ORIGINAL_VALIDATED_STATEV1)
        rel_pct = abs_diff / abs(ORIGINAL_VALIDATED_STATEV1) * 100.0
    except Exception:
        pass

    lines = [
        "# Chaboche Increment Sensitivity Baseline Report",
        "",
        "- Input ODB: %s" % ODB_PATH,
        "- Extracted cycles: 1-20 (cycle-end nearest frames)",
        "- Outputs:",
        "  - %s" % HISTORY_CSV,
        "  - %s" % SUMMARY_CSV,
        "",
        "## Final cycle-20 values",
    ]
    lines += [
        "- STATEV1: %s" % fmt(final["STATEV1_end"]),
        "- STATEV2: %s" % fmt(final["STATEV2_end"]),
        "- STATEV3: %s" % fmt(final["STATEV3_end"]),
        "- STATEV4: %s" % fmt(final["STATEV4_end"]),
        "- STATEV8: %s" % fmt(final["STATEV8_end"]),
        "- STATEV9: %s" % fmt(final["STATEV9_end"]),
        "- STATEV10: %s" % fmt(final["STATEV10_end"]),
        "- STATEV14: %s" % fmt(final["STATEV14_end"]),
        "- Avg S11 (frame): %s" % fmt(avg_s11),
        "- RF1 (RIGHT_FACE, if available): %s" % fmt(rf1_val),
    ]
    lines += ["", "## Comparison to original validated STATEV1"]
    if abs_diff is not None and rel_pct is not None:
        lines += [
            "- Original validated STATEV1 = %s" % fmt(ORIGINAL_VALIDATED_STATEV1),
            "- This run STATEV1 = %s" % fmt(final["STATEV1_end"]),
            "- Absolute difference = %s" % fmt(abs_diff),
            "- Relative difference (percent) = %s%%" % fmt(rel_pct),
        ]
    else:
        lines += ["- Comparison could not be computed due to missing values."]

    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")


def update_debug_report(final_row):
    dbg_path = "CHABOCHE_DEBUG_REPORT.md"
    summary_line = "- Increment-sensitivity baseline run `%s`: STATEV1_cycle20=%s" % (JOB, fmt(final_row["STATEV1_end"]))
    try:
        with open(dbg_path, "a") as f:
            f.write("\n" + summary_line + "\n")
    except Exception:
        pass


def main():
    job_name = DEFAULT_JOB
    if len(sys.argv) > 1:
        job_name = sys.argv[1]
    configure_paths(job_name)

    if not os.path.exists(ODB_PATH):
        raise RuntimeError("ODB not found: " + ODB_PATH)
    history = extract_cycle_end_history()
    write_history_csv(history)
    write_summary_and_report(history)
    update_debug_report(history[-1])
    print("Extraction complete")
    print("History:", HISTORY_CSV)
    print("Summary:", SUMMARY_CSV)
    print("Report:", REPORT)


if __name__ == "__main__":
    main()
