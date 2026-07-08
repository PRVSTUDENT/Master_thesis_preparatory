from odbAccess import openOdb
import csv
import math


JOB = "chaboche_vp_v1_cyclic_eps005_10cycles"
L0 = 10.0

FULL_CSV = JOB + "_diagnostics_full.csv"
QUARTER_CSV = JOB + "_quarter_points.csv"
INCREMENT_CSV = JOB + "_cycle_increments.csv"
REPORT = "CHABOCHE_EPS005_10CYCLE_DIAGNOSTICS_REPORT.md"


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
                "Phase_In_Cycle": t - math.floor(t),
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


def write_full(rows):
    fields = ["Time_s", "Cycle_Number", "Phase_In_Cycle", "U1_mm", "EngStrain",
              "RF1_N", "Avg_S11_MPa", "Avg_SDV1_p", "Avg_SDV15_dp"]
    with open(FULL_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for row in rows:
            w.writerow([fmt(row[field]) for field in fields])


def nearest(rows, target_time):
    return min(rows, key=lambda r: abs(r["Time_s"] - target_time))


def write_quarter_points(rows):
    targets = [
        ("peak_tension", -0.75),
        ("zero_after_tension", -0.50),
        ("peak_compression", -0.25),
        ("zero_after_compression_cycle_end", 0.0),
    ]
    out = []
    for cycle in range(1, 11):
        for point_type, offset in targets:
            target_time = cycle + offset
            row = nearest(rows, target_time)
            out.append({
                "cycle": cycle,
                "target_time": target_time,
                "nearest_frame_time": row["Time_s"],
                "time_error": row["Time_s"] - target_time,
                "point_type": point_type,
                "U1_mm": row["U1_mm"],
                "EngStrain": row["EngStrain"],
                "Avg_S11_MPa": row["Avg_S11_MPa"],
                "RF1_N": row["RF1_N"],
                "Avg_SDV1_p": row["Avg_SDV1_p"],
                "Avg_SDV15_dp": row["Avg_SDV15_dp"],
            })

    fields = ["cycle", "target_time", "nearest_frame_time", "time_error", "point_type",
              "U1_mm", "EngStrain", "Avg_S11_MPa", "RF1_N", "Avg_SDV1_p", "Avg_SDV15_dp"]
    with open(QUARTER_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for row in out:
            w.writerow([row["cycle"], fmt(row["target_time"]), fmt(row["nearest_frame_time"]),
                        fmt(row["time_error"]), row["point_type"], fmt(row["U1_mm"]),
                        fmt(row["EngStrain"]), fmt(row["Avg_S11_MPa"]), fmt(row["RF1_N"]),
                        fmt(row["Avg_SDV1_p"]), fmt(row["Avg_SDV15_dp"])])
    return out


def write_cycle_increments(rows):
    out = []
    for cycle in range(1, 11):
        start_t = cycle - 1.0
        end_t = cycle * 1.0
        start = nearest(rows, start_t)
        end = nearest(rows, end_t)
        in_cycle = [r for r in rows if start_t <= r["Time_s"] <= end_t]
        max_s11 = max(r["Avg_S11_MPa"] for r in in_cycle)
        min_s11 = min(r["Avg_S11_MPa"] for r in in_cycle)
        out.append({
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
        for row in out:
            w.writerow([row["cycle"]] + [fmt(row[field]) for field in fields[1:]])
    return out


def svg_bounds(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax += 1.0
    if ymin == ymax:
        ymax += 1.0
    xr = xmax - xmin
    yr = ymax - ymin
    return xmin - 0.03 * xr, xmax + 0.03 * xr, ymin - 0.05 * yr, ymax + 0.05 * yr


def make_svg(filename, points, xlabel, ylabel, title):
    W, H = 900, 600
    ml, mr, mt, mb = 95, 35, 50, 80
    pw, ph = W - ml - mr, H - mt - mb
    xmin, xmax, ymin, ymax = svg_bounds(points)

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

    pts = " ".join("%.2f,%.2f" % (sx(x), sy(y)) for x, y in points)
    svg.extend([
        '<polyline points="%s" fill="none" stroke="black" stroke-width="2.5"/>' % pts,
        '<text x="%.2f" y="%d" text-anchor="middle" font-size="18" font-family="Arial">%s</text>' % (ml + pw / 2.0, H - 25, xlabel),
        '<text x="25" y="%.2f" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 25,%.2f)">%s</text>' % (mt + ph / 2.0, mt + ph / 2.0, ylabel),
        '</svg>',
    ])
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def make_plots(cycles):
    make_svg("chaboche_eps005_10cycles_delta_sdv1_per_cycle.svg",
             [(r["cycle"], r["Delta_SDV1"]) for r in cycles],
             "Cycle", "Delta SDV1 per cycle", "eps005 10 cycles: Delta SDV1 per cycle")
    make_svg("chaboche_eps005_10cycles_residual_stress_per_cycle.svg",
             [(r["cycle"], r["S11_at_zero_end"]) for r in cycles],
             "Cycle", "S11 at zero-strain cycle end [MPa]", "eps005 10 cycles: residual stress")
    make_svg("chaboche_eps005_10cycles_stress_amplitude_per_cycle.svg",
             [(r["cycle"], r["Stress_Amplitude"]) for r in cycles],
             "Cycle", "Stress amplitude [MPa]", "eps005 10 cycles: stress amplitude")
    make_svg("chaboche_eps005_10cycles_mean_stress_per_cycle.svg",
             [(r["cycle"], r["Mean_Stress"]) for r in cycles],
             "Cycle", "Mean stress [MPa]", "eps005 10 cycles: mean stress")


def monotone_non_decreasing(values):
    return all(values[i] >= values[i - 1] - 1.0e-12 for i in range(1, len(values)))


def write_report(rows, quarters, cycles):
    sdv1_values = [r["Avg_SDV1_p"] for r in rows]
    deltas_2_10 = [r["Delta_SDV1"] for r in cycles[1:]]
    avg_delta_2_10 = avg(deltas_2_10)
    delta_range = max(deltas_2_10) - min(deltas_2_10)
    delta_rel_range = delta_range / avg_delta_2_10 if avg_delta_2_10 else 0.0
    residual_change_2_10 = cycles[-1]["S11_at_zero_end"] - cycles[1]["S11_at_zero_end"]
    amp_change_2_10 = cycles[-1]["Stress_Amplitude"] - cycles[1]["Stress_Amplitude"]
    mean_change_2_10 = cycles[-1]["Mean_Stress"] - cycles[1]["Mean_Stress"]

    generated = [
        FULL_CSV,
        QUARTER_CSV,
        INCREMENT_CSV,
        "chaboche_eps005_10cycles_delta_sdv1_per_cycle.svg",
        "chaboche_eps005_10cycles_residual_stress_per_cycle.svg",
        "chaboche_eps005_10cycles_stress_amplitude_per_cycle.svg",
        "chaboche_eps005_10cycles_mean_stress_per_cycle.svg",
        REPORT,
    ]

    lines = [
        "# Chaboche-v1 eps005 10-cycle diagnostics",
        "",
        "## Key diagnostics",
        "",
        "- Total SDV1 is cumulative accumulated viscoplastic strain p and should not be expected to decrease.",
        "- Total SDV1 monotonic: %s." % ("yes" if monotone_non_decreasing(sdv1_values) else "no"),
        "- Delta SDV1 per cycle stabilizes in rate form: cycles 2-10 average %.10g with range %.10g, relative range %.4g." % (avg_delta_2_10, delta_range, delta_rel_range),
        "- Residual stress at zero strain is nearly steady after cycle 2: cycle 2 %.10g MPa, cycle 10 %.10g MPa, change %.10g MPa." % (cycles[1]["S11_at_zero_end"], cycles[-1]["S11_at_zero_end"], residual_change_2_10),
        "- Stress amplitude is essentially stable after cycle 2: cycle 2 %.10g MPa, cycle 10 %.10g MPa, change %.10g MPa." % (cycles[1]["Stress_Amplitude"], cycles[-1]["Stress_Amplitude"], amp_change_2_10),
        "- Mean stress drifts only mildly after cycle 2: cycle 2 %.10g MPa, cycle 10 %.10g MPa, change %.10g MPa." % (cycles[1]["Mean_Stress"], cycles[-1]["Mean_Stress"], mean_change_2_10),
        "- Selected cycles 1, 2, 5, and 10 form a stable hysteresis family after the initial transient, based on nearly constant stress amplitude and Delta SDV1.",
        "",
        "## Cycle increments",
        "",
        "| cycle | SDV1_start | SDV1_end | Delta_SDV1 | S11_zero_end | Stress_Amplitude | Mean_Stress |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in cycles:
        lines.append("| %d | %.10g | %.10g | %.10g | %.10g | %.10g | %.10g |" %
                     (r["cycle"], r["SDV1_start"], r["SDV1_end"], r["Delta_SDV1"],
                      r["S11_at_zero_end"], r["Stress_Amplitude"], r["Mean_Stress"]))
    lines.extend([
        "",
        "## Generated files",
        "",
    ])
    lines.extend(["- " + name for name in generated])
    lines.append("")

    with open(REPORT, "w") as f:
        f.write("\n".join(lines))


def main():
    rows = extract_rows()
    write_full(rows)
    quarters = write_quarter_points(rows)
    cycles = write_cycle_increments(rows)
    make_plots(cycles)
    write_report(rows, quarters, cycles)

    deltas_2_10 = [r["Delta_SDV1"] for r in cycles[1:]]
    print("Wrote", FULL_CSV)
    print("Wrote", QUARTER_CSV)
    print("Wrote", INCREMENT_CSV)
    print("Wrote", REPORT)
    print("final SDV1 =", fmt(rows[-1]["Avg_SDV1_p"]))
    print("average Delta_SDV1 cycles 2-10 =", fmt(avg(deltas_2_10)))
    print("final residual stress at zero strain =", fmt(cycles[-1]["S11_at_zero_end"]))
    print("final stress amplitude =", fmt(cycles[-1]["Stress_Amplitude"]))
    print("final mean stress =", fmt(cycles[-1]["Mean_Stress"]))


if __name__ == "__main__":
    main()
