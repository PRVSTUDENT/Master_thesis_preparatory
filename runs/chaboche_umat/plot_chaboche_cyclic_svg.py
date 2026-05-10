import csv

csv_file = "chaboche_vp_v1_cyclic_1cycle_summary.csv"
L0 = 10.0

rows = []
with open(csv_file, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        t = float(row["Time_s"])
        u = float(row["U1_mm"])
        rf = float(row["RF1_N"])
        s11 = float(row["Avg_S11_MPa"])
        p = float(row["Avg_SDV1_p"])
        rows.append((t, u, u / L0, rf, s11, p))

def make_svg(filename, x, y, xlabel, ylabel, title):
    W, H = 900, 600
    ml, mr, mt, mb = 95, 35, 50, 80
    pw, ph = W - ml - mr, H - mt - mb

    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    if xmax == xmin:
        xmax += 1.0
    if ymax == ymin:
        ymax += 1.0

    xr = xmax - xmin
    yr = ymax - ymin
    xmin -= 0.03 * xr
    xmax += 0.03 * xr
    ymin -= 0.05 * yr
    ymax += 0.05 * yr

    def sx(v):
        return ml + (v - xmin) / (xmax - xmin) * pw

    def sy(v):
        return mt + ph - (v - ymin) / (ymax - ymin) * ph

    pts = " ".join(f"{sx(a):.2f},{sy(b):.2f}" for a, b in zip(x, y))

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{W/2}" y="28" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>',
        f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" stroke="black" stroke-width="2"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" stroke="black" stroke-width="2"/>',
    ]

    for i in range(6):
        xv = xmin + i * (xmax - xmin) / 5
        px = sx(xv)
        svg.append(f'<line x1="{px:.2f}" y1="{mt}" x2="{px:.2f}" y2="{mt+ph}" stroke="#dddddd" stroke-width="1"/>')
        svg.append(f'<text x="{px:.2f}" y="{mt+ph+25}" text-anchor="middle" font-size="13" font-family="Arial">{xv:.4g}</text>')

        yv = ymin + i * (ymax - ymin) / 5
        py = sy(yv)
        svg.append(f'<line x1="{ml}" y1="{py:.2f}" x2="{ml+pw}" y2="{py:.2f}" stroke="#dddddd" stroke-width="1"/>')
        svg.append(f'<text x="{ml-10}" y="{py+5:.2f}" text-anchor="end" font-size="13" font-family="Arial">{yv:.4g}</text>')

    svg.extend([
        f'<polyline points="{pts}" fill="none" stroke="black" stroke-width="2.5"/>',
        f'<text x="{ml+pw/2}" y="{H-25}" text-anchor="middle" font-size="18" font-family="Arial">{xlabel}</text>',
        f'<text x="25" y="{mt+ph/2}" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 25,{mt+ph/2})">{ylabel}</text>',
        '</svg>',
    ])

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

time = [r[0] for r in rows]
u = [r[1] for r in rows]
strain = [r[2] for r in rows]
rf = [r[3] for r in rows]
s11 = [r[4] for r in rows]
p = [r[5] for r in rows]

make_svg("chaboche_vp_v1_cyclic_stress_strain.svg", strain, s11,
         "Engineering strain, U1/L0", "Average S11 [MPa]",
         "Chaboche-v1 cyclic: Stress-Strain Response")
make_svg("chaboche_vp_v1_cyclic_force_displacement.svg", u, rf,
         "Displacement U1 [mm]", "Reaction force RF1 [N]",
         "Chaboche-v1 cyclic: Force-Displacement Response")
make_svg("chaboche_vp_v1_cyclic_sdv1_time.svg", time, p,
         "Time [s]", "Accumulated viscoplastic strain SDV1",
         "Chaboche-v1 cyclic: SDV1-Time Response")
make_svg("chaboche_vp_v1_cyclic_sdv1_strain.svg", strain, p,
         "Engineering strain, U1/L0", "Accumulated viscoplastic strain SDV1",
         "Chaboche-v1 cyclic: SDV1-Strain Response")

print("Wrote:")
print("  chaboche_vp_v1_cyclic_stress_strain.svg")
print("  chaboche_vp_v1_cyclic_force_displacement.svg")
print("  chaboche_vp_v1_cyclic_sdv1_time.svg")
print("  chaboche_vp_v1_cyclic_sdv1_strain.svg")
