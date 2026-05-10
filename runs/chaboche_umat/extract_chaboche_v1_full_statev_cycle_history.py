from odbAccess import openOdb
import csv
import math
import os
import sys


JOB = "chaboche_vp_v1_cyclic_eps005_20cycles"
ODB_PATH = JOB + ".odb"

HISTORY_CSV = "chaboche_v1_full_statev_cycle_history.csv"
STABILITY_CSV = "chaboche_v1_full_statev_cycle_stability.csv"
REPORT = "CHABOCHE_V1_FULL_STATEV_CYCLE_HISTORY_REPORT.md"

NSTATEV = 15
REFERENCE_START = 2
REFERENCE_END = 10
SMALL_VALUE_TOL = 1.0e-10
STABLE_REL_RANGE_TOL = 0.05

STATEV_NAMES = {
    1: ("p", "Accumulated viscoplastic strain"),
    2: ("X11", "Backstress tensor component"),
    3: ("X22", "Backstress tensor component"),
    4: ("X33", "Backstress tensor component"),
    5: ("X12", "Backstress tensor component"),
    6: ("X13", "Backstress tensor component"),
    7: ("X23", "Backstress tensor component"),
    8: ("Evp11", "Viscoplastic strain tensor component"),
    9: ("Evp22", "Viscoplastic strain tensor component"),
    10: ("Evp33", "Viscoplastic strain tensor component"),
    11: ("Evp12", "Viscoplastic strain tensor component"),
    12: ("Evp13", "Viscoplastic strain tensor component"),
    13: ("Evp23", "Viscoplastic strain tensor component"),
    14: ("RISO", "Current isotropic hardening stress"),
    15: ("DP", "Last viscoplastic multiplier increment"),
}


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % value


def mean(values):
    return sum(values) / len(values) if values else 0.0


def sample_std(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


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
        cycle_zero_values = {}
        t0, f0 = nearest_frame(frames, 0.0)
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
    with csv_open_write(HISTORY_CSV) as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([fmt(row[field]) if field not in ("cycle", "integration_point_values_averaged")
                             else row[field] for field in fields])


def classify_statev(index, mean_delta, rel_range, max_abs_end, max_abs_delta):
    if index == 14:
        return "diagnostic/recomputable"
    if index == 15:
        return "diagnostic/recomputable"
    if max_abs_end < SMALL_VALUE_TOL and max_abs_delta < SMALL_VALUE_TOL:
        return "small/nearly zero component"
    if rel_range is not None and rel_range <= STABLE_REL_RANGE_TOL:
        return "stable extrapolation candidate"
    if abs(mean_delta) < SMALL_VALUE_TOL:
        return "small/nearly zero component"
    return "needs caution"


def stability_rows(history_rows):
    rows = []
    ref = [r for r in history_rows if REFERENCE_START <= r["cycle"] <= REFERENCE_END]
    for i in range(1, NSTATEV + 1):
        deltas = [r["Delta_STATEV%d" % i] for r in ref]
        ends = [r["STATEV%d_end" % i] for r in history_rows]
        m = mean(deltas)
        sd = sample_std(deltas)
        delta_range = max(deltas) - min(deltas)
        rel_range = None
        if abs(m) > SMALL_VALUE_TOL:
            rel_range = delta_range / abs(m)
        max_abs_end = max(abs(v) for v in ends)
        max_abs_delta = max(abs(r["Delta_STATEV%d" % i]) for r in history_rows)
        symbol, meaning = STATEV_NAMES[i]
        rows.append({
            "statev_index": i,
            "symbol_or_name": symbol,
            "inferred_meaning": meaning,
            "mean_delta_cycles_2_10": m,
            "std_delta_cycles_2_10": sd,
            "relative_range_delta_cycles_2_10": rel_range,
            "max_abs_end_cycles_1_20": max_abs_end,
            "max_abs_delta_cycles_1_20": max_abs_delta,
            "classification": classify_statev(i, m, rel_range, max_abs_end, max_abs_delta),
        })
    return rows


def write_stability_csv(rows):
    fields = [
        "statev_index",
        "symbol_or_name",
        "inferred_meaning",
        "mean_delta_cycles_2_10",
        "std_delta_cycles_2_10",
        "relative_range_delta_cycles_2_10",
        "max_abs_end_cycles_1_20",
        "max_abs_delta_cycles_1_20",
        "classification",
    ]
    with csv_open_write(STABILITY_CSV) as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([fmt(row[field]) if field not in ("statev_index", "symbol_or_name", "inferred_meaning", "classification")
                             else row[field] for field in fields])


def write_report(history_rows, stability):
    stable = [r for r in stability if r["classification"] == "stable extrapolation candidate"]
    small = [r for r in stability if r["classification"] == "small/nearly zero component"]
    diagnostic = [r for r in stability if r["classification"] == "diagnostic/recomputable"]
    caution = [r for r in stability if r["classification"] == "needs caution"]

    final = history_rows[-1]
    lines = [
        "# Chaboche-v1 Full STATEV Cycle-History Report",
        "",
        "This report extracts cycle-end averages of all 15 solution-dependent state variables from the validated 20-cycle Abaqus ODB. It prepares the transition from scalar SDV1 cycle jumping to vector-valued STATEV cycle-jump analysis.",
        "",
        "## Input",
        "",
        "- ODB: `%s`" % ODB_PATH,
        "- Cycles extracted: `1-20`",
        "- Cycle-end target times: `1, 2, ..., 20`",
        "- Field outputs extracted: `SDV1` through `SDV15`",
        "- No UMAT files were modified.",
        "- No Abaqus input files were modified.",
        "- Abaqus was not rerun; only the existing ODB was postprocessed.",
        "",
        "## Output Files",
        "",
        "- `%s`" % HISTORY_CSV,
        "- `%s`" % STABILITY_CSV,
        "",
        "## Final Cycle-End State",
        "",
    ]
    for i in range(1, NSTATEV + 1):
        symbol, meaning = STATEV_NAMES[i]
        lines.append("- `STATEV(%d)` `%s`: `%s`" % (i, symbol, fmt(final["STATEV%d_end" % i])))

    lines += [
        "",
        "## Stability Classification",
        "",
        "| STATEV | Symbol | Mean Delta cycles 2-10 | Relative range | Classification |",
        "| ---: | --- | ---: | ---: | --- |",
    ]
    for row in stability:
        rel = row["relative_range_delta_cycles_2_10"]
        rel_txt = "" if rel is None else fmt(rel)
        lines.append("| %d | `%s` | `%s` | `%s` | %s |" % (
            row["statev_index"],
            row["symbol_or_name"],
            fmt(row["mean_delta_cycles_2_10"]),
            rel_txt,
            row["classification"],
        ))

    lines += [
        "",
        "## Stable Extrapolation Candidates",
        "",
    ]
    if stable:
        for row in stable:
            lines.append("- `STATEV(%d)` `%s`: %s" % (row["statev_index"], row["symbol_or_name"], row["inferred_meaning"]))
    else:
        lines.append("- None under the current thresholds.")

    lines += [
        "",
        "## Small / Nearly Zero Components",
        "",
    ]
    if small:
        for row in small:
            lines.append("- `STATEV(%d)` `%s`: %s" % (row["statev_index"], row["symbol_or_name"], row["inferred_meaning"]))
    else:
        lines.append("- None.")

    lines += [
        "",
        "## Diagnostic / Recomputable",
        "",
    ]
    for row in diagnostic:
        lines.append("- `STATEV(%d)` `%s`: %s" % (row["statev_index"], row["symbol_or_name"], row["inferred_meaning"]))

    lines += [
        "",
        "## Needs Caution",
        "",
    ]
    if caution:
        for row in caution:
            lines.append("- `STATEV(%d)` `%s`: %s" % (row["statev_index"], row["symbol_or_name"], row["inferred_meaning"]))
    else:
        lines.append("- None identified by the current cycle-increment stability thresholds.")

    lines += [
        "",
        "## Implication for Level-2 Nesnas-Saanouni Cycle Jump",
        "",
        "The scalar SDV1 jump has already been validated at postprocessing level. This full STATEV history shows which components can be considered for a vector-valued cycle-jump predictor before any Abaqus restart or injected-state continuation is attempted.",
        "",
        "For Level-2 preparation, the independent material state should focus on `STATEV(1-13)`: accumulated viscoplastic strain, backstress tensor components, and viscoplastic strain tensor components. `STATEV(14)` is recomputable from `STATEV(1)` and material constants in this UMAT, while `STATEV(15)` is a last-increment diagnostic.",
        "",
        "The next safe step is a vector-valued postprocessing analyzer that extrapolates the stable/nonzero components of `STATEV(1-13)` and computes a conservative jump size from the most restrictive state component.",
    ]
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    if not os.path.exists(ODB_PATH):
        raise RuntimeError("ODB not found: " + ODB_PATH)
    history = extract_cycle_end_history()
    stability = stability_rows(history)
    write_history_csv(history)
    write_stability_csv(stability)
    write_report(history, stability)
    print("Full STATEV cycle-history extraction complete")
    print("History CSV:", HISTORY_CSV)
    print("Stability CSV:", STABILITY_CSV)
    print("Report:", REPORT)
    print("Final STATEV1:", fmt(history[-1]["STATEV1_end"]))


if __name__ == "__main__":
    main()
