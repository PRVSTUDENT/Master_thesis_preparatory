import csv


JOB = "chaboche_vp_v1_cyclic_eps005_10cycles"


def read_summary():
    rows = []
    with open(JOB + "_summary.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append({
                "time": float(row["Time_s"]),
                "cycle": float(row["Cycle_Number"]),
                "u": float(row["U1_mm"]),
                "strain": float(row["EngStrain"]),
                "rf": float(row["RF1_N"]),
                "s11": float(row["Avg_S11_MPa"]),
                "sdv1": float(row["Avg_SDV1_p"]),
            })
    return rows


def read_cycle_end():
    rows = []
    with open(JOB + "_cycle_end.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append({
                "cycle": float(row["cycle"]),
                "sdv1": float(row["Avg_SDV1"]),
            })
    return rows


def bounds(series):
    xs = [x for item in series for x, y in item["data"]]
    ys = [y for item in series for x, y in item["data"]]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax += 1.0
    if ymax == ymin:
        ymax += 1.0
    xr = xmax - xmin
    yr = ymax - ymin
    return xmin - 0.03 * xr, xmax + 0.03 * xr, ymin - 0.05 * yr, ymax + 0.05 * yr


def make_svg(filename, series, xlabel, ylabel, title):
    W, H = 900, 600
    ml, mr, mt, mb = 95, 150, 50, 80
    pw, ph = W - ml - mr, H - mt - mb
    xmin, xmax, ymin, ymax = bounds(series)

    def sx(v):
        return ml + (v - xmin) / (xmax - xmin) * pw

    def sy(v):
        return mt + ph - (v - ymin) / (ymax - ymin) * ph

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{1}" viewBox="0 0 {0} {1}">'.format(W, H),
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="{0}" y="28" text-anchor="middle" font-size="22" font-family="Arial">{1}</text>'.format(W / 2, title),
        '<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="black" stroke-width="2"/>'.format(ml, mt + ph, ml + pw),
        '<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" stroke="black" stroke-width="2"/>'.format(ml, mt, mt + ph),
    ]
    for i in range(6):
        xv = xmin + i * (xmax - xmin) / 5
        px = sx(xv)
        svg.append('<line x1="{0:.2f}" y1="{1}" x2="{0:.2f}" y2="{2}" stroke="#dddddd" stroke-width="1"/>'.format(px, mt, mt + ph))
        svg.append('<text x="{0:.2f}" y="{1}" text-anchor="middle" font-size="13" font-family="Arial">{2:.4g}</text>'.format(px, mt + ph + 25, xv))

        yv = ymin + i * (ymax - ymin) / 5
        py = sy(yv)
        svg.append('<line x1="{0}" y1="{1:.2f}" x2="{2}" y2="{1:.2f}" stroke="#dddddd" stroke-width="1"/>'.format(ml, py, ml + pw))
        svg.append('<text x="{0}" y="{1:.2f}" text-anchor="end" font-size="13" font-family="Arial">{2:.4g}</text>'.format(ml - 10, py + 5, yv))

    for item in series:
        pts = " ".join("{0:.2f},{1:.2f}".format(sx(x), sy(y)) for x, y in item["data"])
        svg.append('<polyline points="{0}" fill="none" stroke="{1}" stroke-width="{2}"/>'.format(
            pts, item["color"], item.get("width", "2.5")))

    ly = mt + 8
    for item in series:
        svg.append('<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="{3}" stroke-width="3"/>'.format(ml + pw + 25, ly, ml + pw + 55, item["color"]))
        svg.append('<text x="{0}" y="{1}" font-size="14" font-family="Arial">{2}</text>'.format(ml + pw + 65, ly + 5, item["label"]))
        ly += 24

    svg.extend([
        '<text x="{0}" y="{1}" text-anchor="middle" font-size="18" font-family="Arial">{2}</text>'.format(ml + pw / 2, H - 25, xlabel),
        '<text x="25" y="{0}" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 25,{0})">{1}</text>'.format(mt + ph / 2, ylabel),
        '</svg>',
    ])
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("Wrote", filename)


def main():
    rows = read_summary()
    cycle_end = read_cycle_end()
    make_svg(JOB + "_stress_strain.svg",
             [{"label": "10 cycles", "color": "black", "data": [(r["strain"], r["s11"]) for r in rows]}],
             "Engineering strain, U1/L0", "Average S11 [MPa]", "eps005 10 cycles: stress-strain")
    make_svg(JOB + "_force_displacement.svg",
             [{"label": "10 cycles", "color": "black", "data": [(r["u"], r["rf"]) for r in rows]}],
             "Displacement U1 [mm]", "Reaction force RF1 [N]", "eps005 10 cycles: force-displacement")
    make_svg(JOB + "_sdv1_time.svg",
             [{"label": "SDV1", "color": "black", "data": [(r["time"], r["sdv1"]) for r in rows]}],
             "Time [s]", "Accumulated viscoplastic strain SDV1", "eps005 10 cycles: SDV1-time")
    make_svg(JOB + "_cycle_end_sdv1.svg",
             [{"label": "cycle end", "color": "black", "data": [(r["cycle"], r["sdv1"]) for r in cycle_end]}],
             "Cycle", "Cycle-end SDV1", "eps005 10 cycles: cycle-end SDV1")

    colors = {1: "#1f77b4", 2: "#d62728", 5: "#2ca02c", 10: "#9467bd"}
    selected = []
    for cycle in [1, 2, 5, 10]:
        lo = cycle - 1
        hi = cycle
        data = [(r["strain"], r["s11"]) for r in rows if lo <= r["time"] <= hi]
        selected.append({"label": "cycle {0}".format(cycle), "color": colors[cycle], "data": data})
    make_svg(JOB + "_selected_loops.svg", selected,
             "Engineering strain, U1/L0", "Average S11 [MPa]",
             "eps005 10 cycles: selected hysteresis loops")


if __name__ == "__main__":
    main()
