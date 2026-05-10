import csv


CASES = [
    ("chaboche_vp_v1_cyclic_eps001", "eps_amp = 0.001", "#1f77b4"),
    ("chaboche_vp_v1_cyclic_eps002", "eps_amp = 0.002", "#d62728"),
    ("chaboche_vp_v1_cyclic_eps005", "eps_amp = 0.005", "#2ca02c"),
    ("chaboche_vp_v1_cyclic_eps010", "eps_amp = 0.010", "#9467bd"),
]


def read_rows(job):
    rows = []
    with open(job + "_summary.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append({
                "time": float(row["Time_s"]),
                "u": float(row["U1_mm"]),
                "strain": float(row["EngStrain"]),
                "rf": float(row["RF1_N"]),
                "s11": float(row["Avg_S11_MPa"]),
                "sdv1": float(row["Avg_SDV1_p"]),
            })
    return rows


def bounds(series):
    xs = [x for data in series for x, y in data]
    ys = [y for data in series for x, y in data]
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
    xmin, xmax, ymin, ymax = bounds([s["data"] for s in series])

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
        svg.append('<polyline points="{0}" fill="none" stroke="{1}" stroke-width="2.5"/>'.format(pts, item["color"]))

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


def plot_job(job):
    rows = read_rows(job)
    make_svg(job + "_stress_strain.svg",
             [{"label": job, "color": "black", "data": [(r["strain"], r["s11"]) for r in rows]}],
             "Engineering strain, U1/L0", "Average S11 [MPa]", job + ": stress-strain")
    make_svg(job + "_force_displacement.svg",
             [{"label": job, "color": "black", "data": [(r["u"], r["rf"]) for r in rows]}],
             "Displacement U1 [mm]", "Reaction force RF1 [N]", job + ": force-displacement")
    make_svg(job + "_sdv1_time.svg",
             [{"label": job, "color": "black", "data": [(r["time"], r["sdv1"]) for r in rows]}],
             "Time [s]", "Accumulated viscoplastic strain SDV1", job + ": SDV1-time")


def main():
    combined = []
    for job, label, color in CASES:
        rows = read_rows(job)
        plot_job(job)
        combined.append({"label": label, "color": color, "data": [(r["strain"], r["s11"]) for r in rows]})
    make_svg("chaboche_vp_v1_amplitude_sweep_stress_strain.svg", combined,
             "Engineering strain, U1/L0", "Average S11 [MPa]",
             "Chaboche-v1 amplitude sweep: stress-strain")


if __name__ == "__main__":
    main()
