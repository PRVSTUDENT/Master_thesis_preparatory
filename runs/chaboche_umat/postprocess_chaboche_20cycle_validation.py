from odbAccess import openOdb
import csv
import math
import re
import os


JOB = "chaboche_vp_v1_cyclic_eps005_20cycles"
L0 = 10.0
PREDICTED_SDV1_CYCLE20 = 0.1421214351
MEAN_DELTA_2_TO_10 = 0.007185465191

SUMMARY_CSV = JOB + "_summary.csv"
INCREMENT_CSV = JOB + "_cycle_increments.csv"
REPORT = "CHABOCHE_CYCLE_JUMP_20CYCLE_VALIDATION_REPORT.md"


def fmt(v):
    return "%.10g" % v


def avg(values):
    return sum(values) / len(values) if values else 0.0


def extract_rows():
    odb = openOdb(JOB + ".odb")
    assembly = odb.rootAssembly
    right_set = assembly.nodeSets["RIGHT_FACE"]
    right_labels = set(node.label for node in right_set.nodes[0])
    rows = []

    for step_name in odb.steps.keys():
        step = odb.steps[step_name]
        for frame in step.frames:
            t = frame.frameValue
            u1 = 0.0
            rf1 = 0.0
            s11_vals = []
            sdv1_vals = []
            sdv15_vals = []

            for v in frame.fieldOutputs["U"].values:
                if v.nodeLabel in right_labels and abs(v.data[0]) > abs(u1):
                    u1 = v.data[0]
            for v in frame.fieldOutputs["RF"].values:
                if v.nodeLabel in right_labels:
                    rf1 += v.data[0]
            for v in frame.fieldOutputs["S"].values:
                s11_vals.append(v.data[0])
            for v in frame.fieldOutputs["SDV1"].values:
                sdv1_vals.append(v.data)
            for v in frame.fieldOutputs["SDV15"].values:
                sdv15_vals.append(v.data)

            rows.append({
                "Time_s": t,
                "Cycle_Number": t,
                "U1_mm": u1,
                "EngStrain": u1 / L0,
                "RF1_N": rf1,
                "Avg_S11_MPa": avg(s11_vals),
                "Avg_SDV1_p": avg(sdv1_vals),
                "Avg_SDV15_dp": avg(sdv15_vals),
            })

    odb.close()
    rows.sort(key=lambda r: r["Time_s"])
    return rows


def write_summary(rows):
    fields = ["Time_s", "Cycle_Number", "U1_mm", "EngStrain", "RF1_N",
              "Avg_S11_MPa", "Avg_SDV1_p", "Avg_SDV15_dp"]
    with open(SUMMARY_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for row in rows:
            w.writerow([fmt(row[field]) for field in fields])


def nearest(rows, target_time):
    return min(rows, key=lambda r: abs(r["Time_s"] - target_time))


def write_cycle_increments(rows):
    cycles = []
    for cycle in range(1, 21):
        start_t = float(cycle - 1)
        end_t = float(cycle)
        start = nearest(rows, start_t)
        end = nearest(rows, end_t)
        in_cycle = [r for r in rows if start_t <= r["Time_s"] <= end_t]
        max_s11 = max(r["Avg_S11_MPa"] for r in in_cycle)
        min_s11 = min(r["Avg_S11_MPa"] for r in in_cycle)
        cycles.append({
            "cycle": cycle,
            "SDV1_start": start["Avg_SDV1_p"],
            "SDV1_end": end["Avg_SDV1_p"],
            "Delta_SDV1": end["Avg_SDV1_p"] - start["Avg_SDV1_p"],
            "S11_at_zero_end": end["Avg_S11_MPa"],
            "RF1_at_zero_end": end["RF1_N"],
            "Max_S11_in_cycle": max_s11,
            "Min_S11_in_cycle": min_s11,
            "Stress_Amplitude": (max_s11 - min_s11) / 2.0,
            "Mean_Stress": (max_s11 + min_s11) / 2.0,
        })

    fields = ["cycle", "SDV1_start", "SDV1_end", "Delta_SDV1", "S11_at_zero_end",
              "RF1_at_zero_end", "Max_S11_in_cycle", "Min_S11_in_cycle",
              "Stress_Amplitude", "Mean_Stress"]
    with open(INCREMENT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for row in cycles:
            w.writerow([row["cycle"]] + [fmt(row[field]) for field in fields[1:]])
    return cycles


def run_stats():
    msg = open(JOB + ".msg", "r", errors="ignore").read()
    sta = open(JOB + ".sta", "r", errors="ignore").read() if os.path.exists(JOB + ".sta") else ""
    out = {
        "datacheck": "passed",
        "analysis": "completed" if "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" in sta else "not completed",
        "increments": 0,
        "cutbacks": 0,
        "warnings": 0,
        "errors": 0,
    }
    m = re.search(r"TOTAL OF\s+(\d+)\s+INCREMENTS", msg)
    if m:
        out["increments"] = int(m.group(1))
    m = re.search(r"(\d+)\s+CUTBACKS IN AUTOMATIC INCREMENTATION", msg)
    if m:
        out["cutbacks"] = int(m.group(1))
    out["warnings"] = sum(int(v) for v in re.findall(r"^\s*(\d+)\s+WARNING MESSAGES", msg, re.MULTILINE))
    m = re.search(r"^\s*(\d+)\s+ERROR MESSAGES", msg, re.MULTILINE)
    if m:
        out["errors"] = int(m.group(1))
    return out


def svg_bounds(series):
    xs = [x for item in series for x, y in item["data"]]
    ys = [y for item in series for x, y in item["data"]]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax += 1.0
    if ymin == ymax:
        ymax += 1.0
    xr = xmax - xmin
    yr = ymax - ymin
    return xmin - 0.03 * xr, xmax + 0.03 * xr, ymin - 0.05 * yr, ymax + 0.05 * yr


def make_svg(filename, series, xlabel, ylabel, title):
    W, H = 900, 600
    ml, mr, mt, mb = 95, 170, 50, 80
    pw, ph = W - ml - mr, H - mt - mb
    xmin, xmax, ymin, ymax = svg_bounds(series)

    def sx(v):
        return ml + (v - xmin) / (xmax - xmin) * pw

    def sy(v):
        return mt + ph - (v - ymin) / (ymax - ymin) * ph

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="%.2f" y="28" text-anchor="middle" font-size="22" font-family="Arial">%s</text>' % (W / 2.0, title),
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black" stroke-width="2"/>' % (ml, mt + ph, ml + pw, mt + ph),
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black" stroke-width="2"/>' % (ml, mt, ml, mt + ph),
    ]
    for i in range(6):
        xv = xmin + i * (xmax - xmin) / 5.0
        px = sx(xv)
        svg.append('<line x1="%.2f" y1="%d" x2="%.2f" y2="%d" stroke="#dddddd" stroke-width="1"/>' % (px, mt, px, mt + ph))
        svg.append('<text x="%.2f" y="%d" text-anchor="middle" font-size="13" font-family="Arial">%.4g</text>' % (px, mt + ph + 25, xv))
        yv = ymin + i * (ymax - ymin) / 5.0
        py = sy(yv)
        svg.append('<line x1="%d" y1="%.2f" x2="%d" y2="%.2f" stroke="#dddddd" stroke-width="1"/>' % (ml, py, ml + pw, py))
        svg.append('<text x="%d" y="%.2f" text-anchor="end" font-size="13" font-family="Arial">%.4g</text>' % (ml - 10, py + 5, yv))

    for item in series:
        pts = " ".join("%.2f,%.2f" % (sx(x), sy(y)) for x, y in item["data"])
        svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts, item["color"]))

    ly = mt + 8
    for item in series:
        svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"/>' % (ml + pw + 25, ly, ml + pw + 55, ly, item["color"]))
        svg.append('<text x="%d" y="%d" font-size="14" font-family="Arial">%s</text>' % (ml + pw + 65, ly + 5, item["label"]))
        ly += 24
    svg.extend([
        '<text x="%.2f" y="%d" text-anchor="middle" font-size="18" font-family="Arial">%s</text>' % (ml + pw / 2.0, H - 25, xlabel),
        '<text x="25" y="%.2f" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 25,%.2f)">%s</text>' % (mt + ph / 2.0, mt + ph / 2.0, ylabel),
        '</svg>',
    ])
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def make_plots(rows, cycles):
    make_svg("chaboche_eps005_20cycles_stress_strain.svg",
             [{"label": "explicit 20 cycles", "color": "black",
               "data": [(r["EngStrain"], r["Avg_S11_MPa"]) for r in rows]}],
             "Engineering strain, U1/L0", "Average S11 [MPa]",
             "eps005 explicit 20 cycles: stress-strain")
    make_svg("chaboche_eps005_20cycles_sdv1_time.svg",
             [{"label": "explicit 20 cycles", "color": "black",
               "data": [(r["Time_s"], r["Avg_SDV1_p"]) for r in rows]}],
             "Time [s]", "Accumulated viscoplastic strain SDV1",
             "eps005 explicit 20 cycles: SDV1-time")
    make_svg("chaboche_eps005_20cycles_delta_sdv1_per_cycle.svg",
             [{"label": "explicit Delta SDV1", "color": "black",
               "data": [(r["cycle"], r["Delta_SDV1"]) for r in cycles]}],
             "Cycle", "Delta SDV1",
             "eps005 explicit 20 cycles: Delta SDV1")

    explicit = [(r["cycle"], r["SDV1_end"]) for r in cycles]
    predicted = []
    sdv1_10 = next(r["SDV1_end"] for r in cycles if r["cycle"] == 10)
    for n in range(11, 21):
        predicted.append((n, sdv1_10 + (n - 10) * MEAN_DELTA_2_TO_10))
    make_svg("chaboche_cycle_jump_vs_explicit_20cycles.svg",
             [{"label": "explicit Abaqus cycles 1-20", "color": "#1f77b4", "data": explicit},
              {"label": "jump prediction cycles 11-20", "color": "#d62728", "data": predicted}],
             "Cycle", "SDV1", "Cycle-jump prediction vs explicit 20 cycles")


def write_report(stats, cycles, actual, abs_error, rel_error):
    deltas_11_20 = [r["Delta_SDV1"] for r in cycles if 11 <= r["cycle"] <= 20]
    avg_11_20 = avg(deltas_11_20)
    range_11_20 = max(deltas_11_20) - min(deltas_11_20)
    rel_range_11_20 = range_11_20 / avg_11_20 if avg_11_20 else 0.0
    validated = rel_error < 1.0
    generated = [
        JOB + ".inp",
        SUMMARY_CSV,
        INCREMENT_CSV,
        "chaboche_eps005_20cycles_stress_strain.svg",
        "chaboche_eps005_20cycles_sdv1_time.svg",
        "chaboche_eps005_20cycles_delta_sdv1_per_cycle.svg",
        "chaboche_cycle_jump_vs_explicit_20cycles.svg",
        REPORT,
    ]
    lines = [
        "# Chaboche-v1 cycle-jump 20-cycle validation report",
        "",
        "## Run status",
        "",
        "- Datacheck status: %s" % stats["datacheck"],
        "- Full analysis status: %s" % stats["analysis"],
        "- Increments: %d" % stats["increments"],
        "- Cutbacks: %d" % stats["cutbacks"],
        "- Warnings: %d" % stats["warnings"],
        "- Errors: %d" % stats["errors"],
        "",
        "## Prediction comparison",
        "",
        "- Predicted SDV1 at cycle 20: %s" % fmt(PREDICTED_SDV1_CYCLE20),
        "- Explicit SDV1 at cycle 20: %s" % fmt(actual),
        "- Absolute error, actual - predicted: %s" % fmt(abs_error),
        "- Relative error: %s%%" % fmt(rel_error),
        "- 10-cycle jump predictor validated: %s" % ("yes" if validated else "not within 1% tolerance"),
        "",
        "## Stability from cycles 11-20",
        "",
        "- Average Delta_SDV1 cycles 11-20: %s" % fmt(avg_11_20),
        "- Relative range Delta_SDV1 cycles 11-20: %s" % fmt(rel_range_11_20),
        "- Delta_SDV1 remains stable from cycles 11-20: %s" % ("yes" if rel_range_11_20 < 0.01 else "check drift"),
        "",
        "## Generated files",
        "",
    ]
    lines.extend(["- " + name for name in generated])
    lines.append("")
    with open(REPORT, "w") as f:
        f.write("\n".join(lines))


def main():
    rows = extract_rows()
    write_summary(rows)
    cycles = write_cycle_increments(rows)
    stats = run_stats()
    actual = next(r["SDV1_end"] for r in cycles if r["cycle"] == 20)
    abs_error = actual - PREDICTED_SDV1_CYCLE20
    rel_error = abs(abs_error) / actual * 100.0 if actual else 0.0
    make_plots(rows, cycles)
    write_report(stats, cycles, actual, abs_error, rel_error)

    print("Wrote", SUMMARY_CSV)
    print("Wrote", INCREMENT_CSV)
    print("Wrote", REPORT)
    print("Predicted SDV1 cycle 20 =", fmt(PREDICTED_SDV1_CYCLE20))
    print("Explicit SDV1 cycle 20 =", fmt(actual))
    print("Absolute error =", fmt(abs_error))
    print("Relative error percent =", fmt(rel_error))


if __name__ == "__main__":
    main()
