from pathlib import Path
import math
import subprocess


ROOT = Path(r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat")
SECTION = ROOT / "thesis_cycle_jump_section"
FIG = SECTION / "figures"
INP = ROOT / "chaboche_vp_v1_cyclic_eps005_20cycles.inp"


def parse_inp(path):
    nodes = {}
    elements = {}
    mode = None
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("**"):
                continue
            upper = line.upper()
            if upper.startswith("*NODE"):
                mode = "node"
                continue
            if upper.startswith("*ELEMENT"):
                mode = "element"
                continue
            if line.startswith("*"):
                mode = None
                continue
            if mode == "node":
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 4:
                    nodes[int(parts[0])] = tuple(float(v) for v in parts[1:4])
            elif mode == "element":
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 9:
                    elements[int(parts[0])] = [int(v) for v in parts[1:9]]
    return nodes, elements


def project(point):
    x, y, z = point
    # Isometric-like orthographic projection from real Abaqus coordinates.
    px = x - 0.55 * z
    py = -0.65 * y - 0.38 * z
    return px, py


def scaled_projector(nodes, width, height, margin):
    projected = {label: project(coord) for label, coord in nodes.items()}
    xs = [p[0] for p in projected.values()]
    ys = [p[1] for p in projected.values()]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    sx = (width - 2 * margin) / (xmax - xmin)
    sy = (height - 2 * margin) / (ymax - ymin)
    scale = min(sx, sy)

    def p(label):
        x, y = projected[label]
        return margin + (x - xmin) * scale, height - margin - (y - ymin) * scale

    return p


def face_depth(face, nodes):
    return sum(nodes[n][0] + nodes[n][1] + nodes[n][2] for n in face) / len(face)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    nodes, elements = parse_inp(INP)
    if not nodes or not elements:
        raise RuntimeError("Could not parse nodes/elements from %s" % INP)

    elem = elements[1]
    # Abaqus C3D8 node order for this block: bottom face, top face, and four side faces.
    faces = [
        [elem[i] for i in [0, 1, 2, 3]],
        [elem[i] for i in [4, 5, 6, 7]],
        [elem[i] for i in [0, 1, 5, 4]],
        [elem[i] for i in [1, 2, 6, 5]],
        [elem[i] for i in [2, 3, 7, 6]],
        [elem[i] for i in [3, 0, 4, 7]],
    ]
    # Draw far faces first.
    faces = sorted(faces, key=lambda face: face_depth(face, nodes))

    W, H = 1050, 720
    p = scaled_projector(nodes, 620, 410, 60)

    def pts(face):
        return " ".join("%.2f,%.2f" % p(n) for n in face)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        """
<defs>
  <marker id="arrow-red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#d62728"/>
  </marker>
  <marker id="arrow-black" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
  </marker>
</defs>
""",
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="525" y="42" text-anchor="middle" font-size="26" font-family="Arial" font-weight="bold">Actual Abaqus C3D8 geometry extracted from input deck</text>',
    ]

    palette = ["#e8f4ff", "#d9ecff", "#cce4fa", "#bdd9f2", "#d7e9fa", "#eef7ff"]
    for i, face in enumerate(faces):
        svg.append(f'<polygon points="{pts(face)}" fill="{palette[i % len(palette)]}" stroke="#1f4e79" stroke-width="2.2"/>')

    # Edges for a C3D8 brick.
    edges = [(1, 2), (2, 3), (3, 4), (4, 1), (5, 6), (6, 7), (7, 8), (8, 5), (1, 5), (2, 6), (3, 7), (4, 8)]
    for a, b in edges:
        x1, y1 = p(a)
        x2, y2 = p(b)
        svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#1f4e79" stroke-width="2.4"/>')

    # Nodes with labels.
    for label in sorted(nodes):
        x, y = p(label)
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#173f5f"/>')
        svg.append(f'<text x="{x+8:.2f}" y="{y-7:.2f}" font-size="14" font-family="Arial" fill="#173f5f">N{label}</text>')

    # Actual coordinate table.
    tx, ty = 690, 110
    svg.append(f'<text x="{tx}" y="{ty}" font-size="19" font-family="Arial" font-weight="bold">Extracted node coordinates [mm]</text>')
    ty += 28
    svg.append(f'<text x="{tx}" y="{ty}" font-size="15" font-family="Consolas">node    x      y      z</text>')
    ty += 20
    for label in sorted(nodes):
        x, y, z = nodes[label]
        svg.append(f'<text x="{tx}" y="{ty}" font-size="15" font-family="Consolas">{label:>4} {x:6.2f} {y:6.2f} {z:6.2f}</text>')
        ty += 20

    # Dimensions and boundary/load note.
    svg.extend([
        '<text x="310" y="520" text-anchor="middle" font-size="18" font-family="Arial">Element type: C3D8, single brick element</text>',
        '<text x="310" y="550" text-anchor="middle" font-size="18" font-family="Arial">Dimensions: 10 mm × 2 mm × 2 mm, cross-section = 4 mm²</text>',
        '<text x="310" y="580" text-anchor="middle" font-size="18" font-family="Arial">LEFT_FACE nodes: 1, 4, 5, 8; RIGHT_FACE nodes: 2, 3, 6, 7</text>',
        '<text x="310" y="610" text-anchor="middle" font-size="18" font-family="Arial">Cyclic displacement on RIGHT_FACE: U1 amplitude = ±0.05 mm</text>',
    ])

    # Mini amplitude sketch.
    ax0, ay0 = 720, 500
    svg.extend([
        f'<line x1="{ax0}" y1="{ay0+70}" x2="{ax0+250}" y2="{ay0+70}" stroke="#333" stroke-width="1.8"/>',
        f'<line x1="{ax0}" y1="{ay0+20}" x2="{ax0}" y2="{ay0+120}" stroke="#333" stroke-width="1.8"/>',
        f'<polyline points="{ax0},{ay0+70} {ax0+62},{ay0+25} {ax0+125},{ay0+70} {ax0+187},{ay0+115} {ax0+250},{ay0+70}" fill="none" stroke="#d62728" stroke-width="3"/>',
        f'<text x="{ax0+125}" y="{ay0+155}" text-anchor="middle" font-size="16" font-family="Arial">one cycle: 0 → +1 → 0 → -1 → 0</text>',
        f'<text x="{ax0+125}" y="{ay0+5}" text-anchor="middle" font-size="18" font-family="Arial" font-weight="bold">Cyclic amplitude shape</text>',
    ])

    svg.append('</svg>')
    svg_path = FIG / "fig00b_actual_abaqus_geometry.svg"
    png_path = FIG / "fig00b_actual_abaqus_geometry.png"
    svg_path.write_text("\n".join(svg), encoding="utf-8")
    subprocess.run(["magick", "-density", "300", str(svg_path), str(png_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Wrote", svg_path)
    print("Wrote", png_path)


if __name__ == "__main__":
    main()
