from pathlib import Path
import subprocess


ROOT = Path(r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat\thesis_cycle_jump_section")
FIG = ROOT / "figures"


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    svg_path = FIG / "fig00_geometry_material_model.svg"
    png_path = FIG / "fig00_geometry_material_model.png"

    W, H = 1200, 720
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="600" y="45" text-anchor="middle" font-size="28" font-family="Arial" font-weight="bold">Single-element cyclic UMAT validation model</text>',
        '<text x="310" y="92" text-anchor="middle" font-size="20" font-family="Arial" font-weight="bold">Abaqus geometry and boundary conditions</text>',
        '<text x="895" y="92" text-anchor="middle" font-size="20" font-family="Arial" font-weight="bold">Chaboche-v1 unified viscoplastic material model</text>',
    ]

    # 3D block, approximate isometric projection.
    front = [(150, 255), (470, 255), (470, 385), (150, 385)]
    dx, dy = 95, -70
    back = [(x + dx, y + dy) for x, y in front]
    def pts(poly):
        return " ".join(f"{x},{y}" for x, y in poly)

    svg.extend([
        f'<polygon points="{pts([back[0], back[1], front[1], front[0]])}" fill="#d8ecff" stroke="#1f4e79" stroke-width="2"/>',
        f'<polygon points="{pts([front[1], back[1], back[2], front[2]])}" fill="#c3def7" stroke="#1f4e79" stroke-width="2"/>',
        f'<polygon points="{pts(front)}" fill="#eaf4ff" stroke="#1f4e79" stroke-width="2.5"/>',
        f'<polygon points="{pts(back)}" fill="none" stroke="#1f4e79" stroke-width="2"/>',
    ])
    for i in range(4):
        svg.append(f'<line x1="{front[i][0]}" y1="{front[i][1]}" x2="{back[i][0]}" y2="{back[i][1]}" stroke="#1f4e79" stroke-width="2"/>')

    # Node hints.
    for x, y in front + back:
        svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#1f4e79"/>')

    # Left fixed face markers.
    for y in [250, 285, 320, 355, 390]:
        svg.append(f'<line x1="116" y1="{y}" x2="150" y2="{y-18}" stroke="#555" stroke-width="2"/>')
    svg.append('<text x="95" y="410" text-anchor="start" font-size="17" font-family="Arial">LEFT_FACE fixed in U1</text>')

    # Right cyclic loading arrow.
    svg.extend([
        '<line x1="470" y1="318" x2="610" y2="318" stroke="#d62728" stroke-width="5" marker-end="url(#arrow-red)"/>',
        '<line x1="610" y1="340" x2="470" y2="340" stroke="#d62728" stroke-width="5" marker-end="url(#arrow-red)"/>',
        '<text x="545" y="296" text-anchor="middle" font-size="17" font-family="Arial" fill="#9b1b1b">cyclic U1</text>',
        '<text x="545" y="370" text-anchor="middle" font-size="17" font-family="Arial" fill="#9b1b1b">Uamp = ±0.05 mm</text>',
    ])

    # Dimensions.
    svg.extend([
        '<line x1="150" y1="430" x2="470" y2="430" stroke="#333" stroke-width="1.8" marker-start="url(#arrow-black)" marker-end="url(#arrow-black)"/>',
        '<text x="310" y="458" text-anchor="middle" font-size="17" font-family="Arial">L0 = 10 mm</text>',
        '<line x1="500" y1="255" x2="500" y2="385" stroke="#333" stroke-width="1.8" marker-start="url(#arrow-black)" marker-end="url(#arrow-black)"/>',
        '<text x="530" y="325" text-anchor="middle" font-size="17" font-family="Arial" transform="rotate(-90 530,325)">2 mm</text>',
        '<line x1="475" y1="230" x2="568" y2="160" stroke="#333" stroke-width="1.8" marker-start="url(#arrow-black)" marker-end="url(#arrow-black)"/>',
        '<text x="555" y="185" text-anchor="middle" font-size="17" font-family="Arial">2 mm</text>',
        '<text x="310" y="505" text-anchor="middle" font-size="17" font-family="Arial">One C3D8 element, cross-section = 4 mm²</text>',
        '<text x="310" y="535" text-anchor="middle" font-size="17" font-family="Arial">Fully reversed displacement-controlled loading, εamp = ±0.5%</text>',
    ])

    # Material model panel.
    box = [
        (710, 145, 1050, 210, "Elastic predictor", "E = 210000 MPa, ν = 0.3"),
        (710, 245, 1050, 310, "Yield / overstress check", "σy = 520 MPa, Perzyna K = 1000, m = 5"),
        (710, 345, 1050, 410, "Chaboche kinematic hardening", "C = 120000 MPa, γ = 800"),
        (710, 445, 1050, 510, "State variables", "SDV1 = p, SDV15 = Δp"),
    ]
    for x1, y1, x2, y2, title, subtitle in box:
        svg.extend([
            f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="6" fill="#f7f7f7" stroke="#333" stroke-width="1.8"/>',
            f'<text x="{(x1+x2)/2}" y="{y1+25}" text-anchor="middle" font-size="18" font-family="Arial" font-weight="bold">{title}</text>',
            f'<text x="{(x1+x2)/2}" y="{y1+50}" text-anchor="middle" font-size="15" font-family="Arial">{subtitle}</text>',
        ])
    for y in [210, 310, 410]:
        svg.append(f'<line x1="880" y1="{y+5}" x2="880" y2="{y+30}" stroke="#333" stroke-width="2.5" marker-end="url(#arrow-black)"/>')

    svg.extend([
        '<text x="880" y="570" text-anchor="middle" font-size="17" font-family="Arial">Cycle-jump variable: stabilized per-cycle increment ΔSDV1</text>',
        '<text x="880" y="602" text-anchor="middle" font-size="17" font-family="Arial">Mean ΔSDV1 cycles 2–10 = 0.007185465191</text>',
    ])

    # Arrow definitions last are still valid in SVG.
    svg.insert(1, """
<defs>
  <marker id="arrow-red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#d62728"/>
  </marker>
  <marker id="arrow-black" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
  </marker>
</defs>
""")
    svg.append('</svg>')
    svg_path.write_text("\n".join(svg), encoding="utf-8")

    subprocess.run(
        ["magick", "-density", "300", str(svg_path), str(png_path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print("Wrote", svg_path)
    print("Wrote", png_path)


if __name__ == "__main__":
    main()
