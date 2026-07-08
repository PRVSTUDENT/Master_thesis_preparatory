import csv

csv_file = "chaboche_vp_v1_summary.csv"
L0 = 10.0  # mm

rows = []
with open(csv_file, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        t = float(row["Time_s"])
        u = float(row["U1_mm"])
        rf = float(row["RF1_N"])
        s11 = float(row["Avg_S11_MPa"])
        p = float(row["Avg_SDV1_p"])
        rows.append((t, u, u/L0, rf, s11, p))

def make_svg(filename, x, y, xlabel, ylabel, title):
    W, H = 900, 600
    ml, mr, mt, mb = 90, 30, 50, 80
    pw, ph = W - ml - mr, H - mt - mb

    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    if xmax == xmin:
        xmax += 1.0
    if ymax == ymin:
        ymax += 1.0

    # Add small padding
    yr = ymax - ymin
    ymin -= 0.05 * yr
    ymax += 0.05 * yr

    def sx(v):
        return ml + (v - xmin) / (xmax - xmin) * pw

    def sy(v):
        return mt + ph - (v - ymin) / (ymax - ymin) * ph

    pts = " ".join(f"{sx(a):.2f},{sy(b):.2f}" for a, b in zip(x, y))

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    svg.append('<rect width="100%" height="100%" fill="white"/>')
    svg.append(f'<text x="{W/2}" y="28" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>')

    # Axes
    svg.append(f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" stroke="black" stroke-width="2"/>')
    svg.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" stroke="black" stroke-width="2"/>')

    # Grid/ticks
    for i in range(6):
        xv = xmin + i*(xmax-xmin)/5
        px = sx(xv)
        svg.append(f'<line x1="{px:.2f}" y1="{mt}" x2="{px:.2f}" y2="{mt+ph}" stroke="#dddddd" stroke-width="1"/>')
        svg.append(f'<text x="{px:.2f}" y="{mt+ph+25}" text-anchor="middle" font-size="13" font-family="Arial">{xv:.4g}</text>')

        yv = ymin + i*(ymax-ymin)/5
        py = sy(yv)
        svg.append(f'<line x1="{ml}" y1="{py:.2f}" x2="{ml+pw}" y2="{py:.2f}" stroke="#dddddd" stroke-width="1"/>')
        svg.append(f'<text x="{ml-10}" y="{py+5:.2f}" text-anchor="end" font-size="13" font-family="Arial">{yv:.4g}</text>')

    # Curve
    svg.append(f'<polyline points="{pts}" fill="none" stroke="black" stroke-width="2.5"/>')

    # Labels
    svg.append(f'<text x="{ml+pw/2}" y="{H-25}" text-anchor="middle" font-size="18" font-family="Arial">{xlabel}</text>')
    svg.append(f'<text x="25" y="{mt+ph/2}" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 25,{mt+ph/2})">{ylabel}</text>')

    svg.append('</svg>')

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

strain = [r[2] for r in rows]
u = [r[1] for r in rows]
rf = [r[3] for r in rows]
s11 = [r[4] for r in rows]
p = [r[5] for r in rows]

make_svg("chaboche_vp_v1_stress_strain.svg", strain, s11,
         "Engineering strain, U1/L0", "Average S11 [MPa]",
         "Chaboche-v1: Stress-Strain Response")

make_svg("chaboche_vp_v1_force_displacement.svg", u, rf,
         "Displacement U1 [mm]", "Reaction force RF1 [N]",
         "Chaboche-v1: Force-Displacement Response")

make_svg("chaboche_vp_v1_sdv1_strain.svg", strain, p,
         "Engineering strain, U1/L0", "Accumulated viscoplastic strain SDV1",
         "Chaboche-v1: SDV1 Evolution")

print("Wrote:")
print("  chaboche_vp_v1_stress_strain.svg")
print("  chaboche_vp_v1_force_displacement.svg")
print("  chaboche_vp_v1_sdv1_strain.svg")
print()
print("Final strain =", strain[-1])
print("Final S11 MPa =", s11[-1])
print("Final RF1 N =", rf[-1])
print("Final SDV1 =", p[-1])
