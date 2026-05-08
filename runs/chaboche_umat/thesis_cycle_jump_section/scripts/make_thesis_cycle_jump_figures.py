from pathlib import Path
import csv
import shutil
import subprocess


ROOT = Path(r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat")
MILESTONE = ROOT / "milestone_cycle_jump_validated"
OUT = ROOT / "thesis_cycle_jump_section"
FIG = OUT / "figures"
TAB = OUT / "tables"
LATEX = OUT / "latex"
SCRIPTS = OUT / "scripts"

PREDICTED_SDV1_CYCLE20 = 0.1421214351
EXPLICIT_SDV1_CYCLE20 = 0.1420256943
ABS_ERROR = -9.574084894e-05
REL_ERROR_PERCENT = 0.06741093536

SOURCE_CSV = [
    "chaboche_vp_v1_amplitude_sweep_summary.csv",
    "chaboche_vp_v1_cyclic_eps005_10cycles_summary.csv",
    "chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv",
    "chaboche_cycle_jump_predictions.csv",
    "chaboche_cycle_jump_curve_1_to_1000.csv",
    "chaboche_vp_v1_cyclic_eps005_20cycles_summary.csv",
    "chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv",
]

SOURCE_SVG = [
    "chaboche_vp_v1_amplitude_sweep_stress_strain.svg",
    "chaboche_vp_v1_cyclic_eps005_10cycles_selected_loops.svg",
    "chaboche_eps005_10cycles_delta_sdv1_per_cycle.svg",
    "chaboche_cycle_jump_sdv1_prediction.svg",
    "chaboche_cycle_jump_vs_explicit_20cycles.svg",
]


def ensure_dirs():
    for path in [FIG, TAB, LATEX, SCRIPTS]:
        path.mkdir(parents=True, exist_ok=True)


def find_source(name):
    for base in [ROOT, MILESTONE]:
        path = base / name
        if path.exists():
            return path
    return None


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def copy_sources():
    missing = []
    copied = []
    for name in SOURCE_CSV:
        src = find_source(name)
        if src is None:
            missing.append(name)
            continue
        dst = TAB / name
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(OUT)))
    for name in SOURCE_SVG:
        src = find_source(name)
        if src is None:
            missing.append(name)
            continue
        dst = FIG / ("source_" + name)
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(OUT)))
    return copied, missing


def data_path(name):
    path = TAB / name
    if path.exists():
        return path
    src = find_source(name)
    if src is None:
        raise FileNotFoundError(name)
    return src


def bounds(series, hlines=None):
    xs = [x for item in series for x, y in item["data"]]
    ys = [y for item in series for x, y in item["data"]]
    if hlines:
        ys.extend(hlines)
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax += 1.0
    if ymin == ymax:
        ymax += 1.0
    xr = xmax - xmin
    yr = ymax - ymin
    return xmin - 0.04 * xr, xmax + 0.04 * xr, ymin - 0.06 * yr, ymax + 0.06 * yr


def make_svg(name, series, xlabel, ylabel, hlines=None):
    hlines = hlines or []
    W, H = 1000, 680
    ml, mr, mt, mb = 115, 210, 45, 95
    pw, ph = W - ml - mr, H - mt - mb
    xmin, xmax, ymin, ymax = bounds(series, [h[0] for h in hlines])

    def sx(v):
        return ml + (v - xmin) / (xmax - xmin) * pw

    def sy(v):
        return mt + ph - (v - ymin) / (ymax - ymin) * ph

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" stroke="black" stroke-width="1.8"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" stroke="black" stroke-width="1.8"/>',
    ]
    for i in range(6):
        xv = xmin + i * (xmax - xmin) / 5
        px = sx(xv)
        svg.append(f'<line x1="{px:.2f}" y1="{mt}" x2="{px:.2f}" y2="{mt+ph}" stroke="#dddddd" stroke-width="1"/>')
        svg.append(f'<text x="{px:.2f}" y="{mt+ph+28}" text-anchor="middle" font-size="15" font-family="Arial">{xv:.4g}</text>')
        yv = ymin + i * (ymax - ymin) / 5
        py = sy(yv)
        svg.append(f'<line x1="{ml}" y1="{py:.2f}" x2="{ml+pw}" y2="{py:.2f}" stroke="#dddddd" stroke-width="1"/>')
        svg.append(f'<text x="{ml-12}" y="{py+5:.2f}" text-anchor="end" font-size="15" font-family="Arial">{yv:.4g}</text>')

    for y, label in hlines:
        py = sy(y)
        svg.append(f'<line x1="{ml}" y1="{py:.2f}" x2="{ml+pw}" y2="{py:.2f}" stroke="#666666" stroke-width="2" stroke-dasharray="8 6"/>')

    for item in series:
        pts = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in item["data"])
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{item["color"]}" stroke-width="2.4"/>')
        if item.get("markers"):
            for x, y in item["data"]:
                svg.append(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="3.2" fill="{item["color"]}"/>')

    ly = mt + 12
    for item in series:
        svg.append(f'<line x1="{ml+pw+28}" y1="{ly}" x2="{ml+pw+60}" y2="{ly}" stroke="{item["color"]}" stroke-width="3"/>')
        svg.append(f'<text x="{ml+pw+70}" y="{ly+5}" font-size="15" font-family="Arial">{item["label"]}</text>')
        ly += 26
    for y, label in hlines:
        svg.append(f'<line x1="{ml+pw+28}" y1="{ly}" x2="{ml+pw+60}" y2="{ly}" stroke="#666666" stroke-width="2" stroke-dasharray="8 6"/>')
        svg.append(f'<text x="{ml+pw+70}" y="{ly+5}" font-size="15" font-family="Arial">{label}</text>')
        ly += 26

    svg.extend([
        f'<text x="{ml+pw/2}" y="{H-35}" text-anchor="middle" font-size="20" font-family="Arial">{xlabel}</text>',
        f'<text x="32" y="{mt+ph/2}" text-anchor="middle" font-size="20" font-family="Arial" transform="rotate(-90 32,{mt+ph/2})">{ylabel}</text>',
        '</svg>',
    ])
    path = FIG / f"{name}.svg"
    path.write_text("\n".join(svg), encoding="utf-8")
    return path


def convert_png(svg_path):
    png_path = svg_path.with_suffix(".png")
    try:
        subprocess.run(
            ["magick", "-density", "300", str(svg_path), str(png_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception:
        return False
    return png_path.exists()


def save(name, series, xlabel, ylabel, hlines=None):
    svg = make_svg(name, series, xlabel, ylabel, hlines=hlines)
    return svg.exists(), convert_png(svg)


def make_fig01():
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    cases = [
        ("+/-0.1%", "chaboche_vp_v1_cyclic_eps001_summary.csv"),
        ("+/-0.2%", "chaboche_vp_v1_cyclic_eps002_summary.csv"),
        ("+/-0.5%", "chaboche_vp_v1_cyclic_eps005_summary.csv"),
        ("+/-1.0%", "chaboche_vp_v1_cyclic_eps010_summary.csv"),
    ]
    series = []
    for idx, (label, fname) in enumerate(cases):
        src = find_source(fname)
        if src is None:
            continue
        rows = read_csv(src)
        series.append({
            "label": label,
            "color": colors[idx],
            "data": [(float(r["EngStrain"]), float(r["Avg_S11_MPa"])) for r in rows],
        })
    return save("fig01_amplitude_sweep_stress_strain", series, "Engineering strain", "Average S11 [MPa]")


def make_fig02():
    rows = read_csv(data_path("chaboche_vp_v1_cyclic_eps005_10cycles_summary.csv"))
    colors = {1: "#1f77b4", 2: "#d62728", 5: "#2ca02c", 10: "#9467bd"}
    series = []
    for cycle in [1, 2, 5, 10]:
        subset = [r for r in rows if cycle - 1 <= float(r["Time_s"]) <= cycle]
        series.append({
            "label": f"Cycle {cycle}",
            "color": colors[cycle],
            "data": [(float(r["EngStrain"]), float(r["Avg_S11_MPa"])) for r in subset],
        })
    return save("fig02_10cycle_selected_hysteresis_loops", series, "Engineering strain", "Average S11 [MPa]")


def make_fig03():
    rows = read_csv(data_path("chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv"))
    data = [(int(r["cycle"]), float(r["Delta_SDV1"])) for r in rows]
    ref = [y for x, y in data if x >= 2]
    mean_ref = sum(ref) / len(ref)
    return save(
        "fig03_delta_sdv1_per_cycle",
        [{"label": "Delta SDV1", "color": "black", "markers": True, "data": data}],
        "Cycle",
        "Delta SDV1 per cycle",
        hlines=[(mean_ref, "Mean cycles 2-10")],
    )


def make_fig04():
    rows = read_csv(data_path("chaboche_cycle_jump_curve_1_to_1000.csv"))
    exp, pred = [], []
    for row in rows:
        item = (int(row["cycle"]), float(row["SDV1_actual_or_predicted"]))
        if row["source"] == "explicit_abaqus":
            exp.append(item)
        else:
            pred.append(item)
    return save(
        "fig04_cycle_jump_sdv1_prediction",
        [
            {"label": "Explicit Abaqus", "color": "#1f77b4", "markers": True, "data": exp},
            {"label": "Cycle-jump prediction", "color": "#d62728", "data": pred},
        ],
        "Cycle",
        "Accumulated viscoplastic strain SDV1",
    )


def make_fig05():
    exp_rows = read_csv(data_path("chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv"))
    pred_rows = read_csv(data_path("chaboche_cycle_jump_curve_1_to_1000.csv"))
    exp = [(int(r["cycle"]), float(r["SDV1_end"])) for r in exp_rows]
    pred = [
        (int(r["cycle"]), float(r["SDV1_actual_or_predicted"]))
        for r in pred_rows
        if int(r["cycle"]) <= 20
    ]
    return save(
        "fig05_cycle_jump_vs_explicit_20cycles",
        [
            {"label": "Explicit 20-cycle Abaqus", "color": "#1f77b4", "markers": True, "data": exp},
            {"label": "Cycle-jump prediction", "color": "#d62728", "data": pred},
        ],
        "Cycle",
        "Accumulated viscoplastic strain SDV1",
    )


def make_tables():
    amp = read_csv(data_path("chaboche_vp_v1_amplitude_sweep_summary.csv"))
    fields = ["eps_amp", "U_amp", "max_S11", "min_S11", "final_SDV1", "analysis_completed"]
    write_csv(TAB / "table01_amplitude_sweep_summary.csv", [{k: r[k] for k in fields} for r in amp], fields)
    val_fields = ["predicted_SDV1_cycle20", "explicit_SDV1_cycle20", "absolute_error", "relative_error_percent"]
    write_csv(
        TAB / "table02_cycle_jump_validation_summary.csv",
        [{
            "predicted_SDV1_cycle20": f"{PREDICTED_SDV1_CYCLE20:.10g}",
            "explicit_SDV1_cycle20": f"{EXPLICIT_SDV1_CYCLE20:.10g}",
            "absolute_error": f"{ABS_ERROR:.10g}",
            "relative_error_percent": f"{REL_ERROR_PERCENT:.10g}",
        }],
        val_fields,
    )
    return ["tables/table01_amplitude_sweep_summary.csv", "tables/table02_cycle_jump_validation_summary.csv"]


def figure_env(label, stem, caption):
    return rf"""\begin{{figure}}[htbp]
    \centering
    \includegraphics[width=0.82\textwidth]{{figures/{stem}.png}}
    \caption{{{caption}}}
    \label{{fig:{label}}}
\end{{figure}}"""


def make_latex():
    fig_caps = [
        ("amplitude_sweep", "fig01_amplitude_sweep_stress_strain",
         "Amplitude sweep for the Chaboche-v1 UMAT. The smaller amplitudes remain mainly elastic, while the $\\pm0.5\\%$ case activates viscoplasticity at a moderate stress level and was selected for the cycle-jump demonstration."),
        ("ten_cycle_loops", "fig02_10cycle_selected_hysteresis_loops",
         "Selected hysteresis loops from the explicit 10-cycle Abaqus simulation at $\\pm0.5\\%$ strain amplitude. The loop shape becomes nearly repeatable after the initial transient."),
        ("delta_sdv1", "fig03_delta_sdv1_per_cycle",
         "Per-cycle increment of accumulated viscoplastic strain. After the first cycle, the increment remains nearly constant, supporting the use of a cycle-jump predictor."),
        ("jump_prediction", "fig04_cycle_jump_sdv1_prediction",
         "Cycle-jump prediction of accumulated viscoplastic strain using the stabilized per-cycle increment obtained from explicit cycles 2--10."),
        ("jump_validation", "fig05_cycle_jump_vs_explicit_20cycles",
         "Validation of the cycle-jump predictor against an independent explicit 20-cycle Abaqus simulation. The predicted and explicit SDV1 values agree closely, with a relative error of 0.0674\\% at cycle 20."),
    ]
    figures_only = "\n\n".join(figure_env(*item) for item in fig_caps)
    (LATEX / "cycle_jump_chaboche_figures_only.tex").write_text(figures_only + "\n", encoding="utf-8")

    section = rf"""\section{{Cycle-Jump Demonstration Using a Chaboche Unified Viscoplastic UMAT}}

\subsection{{Motivation}}

Long cyclic simulations are computationally expensive when every loading cycle is resolved explicitly. A cycle-jump approach reduces the cost by identifying a stabilized per-cycle evolution of selected internal variables and extrapolating this evolution over many cycles. In the present demonstration, the cycle-jump variable is the accumulated viscoplastic strain stored by the UMAT as SDV1.

\subsection{{Abaqus--UMAT Model}}

The model was implemented in Abaqus/Standard using a single C3D8 block element smoke-test geometry. The material response was described by a Chaboche-v1 unified viscoplastic UMAT and loaded under displacement-controlled fully reversed cyclic loading. The state variable SDV1 represents the accumulated viscoplastic strain \(p\), while SDV15 stores the last viscoplastic increment. This compact setup was selected to isolate the UMAT response, the Abaqus interface, and the cycle-jump postprocessing workflow.

\subsection{{Amplitude Selection}}

An amplitude sweep was first performed to identify a physically useful validation amplitude. The \(\pm0.1\%\) and \(\pm0.2\%\) cases remained elastic or near-elastic, whereas the \(\pm0.5\%\) case activated viscoplasticity at a moderate stress level. The \(\pm1.0\%\) case produced stronger plastic cycling. Therefore, the \(\pm0.5\%\) strain amplitude was selected for the cycle-jump demonstration.

{figure_env(*fig_caps[0])}

\subsection{{Explicit 10-Cycle Baseline}}

The selected \(\pm0.5\%\) case was simulated explicitly for 10 cycles. The analysis completed with 507 increments, 0 cutbacks, 0 warnings, and 0 errors. The simulation produced nonzero stress, nonzero reaction force, and monotonic accumulated state-variable evolution. The selected hysteresis loops show that the loop shape becomes nearly repeatable after the first-cycle transient.

{figure_env(*fig_caps[1])}

\subsection{{Stabilized Internal-Variable Increment}}

The total SDV1 value is cumulative because it represents accumulated viscoplastic strain. It should therefore increase monotonically and should not be used directly as a stabilization criterion. Instead, stabilization was assessed using the per-cycle increment \(\Delta\mathrm{{SDV1}}\). Cycles 2--10 were used as the stabilized reference window. Over this window, the mean increment was \(0.007185465191\), the standard deviation was \(3.368213202\times10^{{-6}}\), and the relative range was \(0.001429037192\), corresponding to approximately \(0.1429\%\).

{figure_env(*fig_caps[2])}

\subsection{{Cycle-Jump Predictor}}

The postprocessing-level cycle-jump predictor was defined as

\[
p_N^{{\mathrm{{pred}}}} =
p_{{10}} + (N-10)\,\overline{{\Delta p}}_{{2-10}},
\]

where \(p_N^{{\mathrm{{pred}}}}\) is the predicted accumulated viscoplastic strain at cycle \(N\), \(p_{{10}}\) is the explicit value at cycle 10, and \(\overline{{\Delta p}}_{{2-10}}\) is the mean per-cycle increment from cycles 2--10. The resulting predictions were \(p_{{20}}=0.1421214351\), \(p_{{50}}=0.3576853909\), \(p_{{100}}=0.7169586504\), \(p_{{200}}=1.435505169\), \(p_{{500}}=3.591144727\), and \(p_{{1000}}=7.183877322\).

{figure_env(*fig_caps[3])}

\subsection{{Explicit 20-Cycle Validation}}

A separate explicit 20-cycle Abaqus simulation was performed to validate the cycle-jump prediction. This analysis completed with 1007 increments, 0 cutbacks, 0 warnings, and 0 errors. The predicted SDV1 value at cycle 20 was 0.1421214351, while the explicit Abaqus result was 0.1420256943. The absolute error was \(-9.574084894\times10^{{-5}}\), corresponding to a relative error of 0.0674\%.

{figure_env(*fig_caps[4])}

\subsection{{Discussion and Limitations}}

This result validates a postprocessing-level cycle-jump predictor for the simplified Chaboche-v1 model and the selected \(\pm0.5\%\) strain-amplitude test case. The method does not yet inject jumped STATEV values into Abaqus and is not yet a calibrated fatigue-life model. The next implementation step would be state-variable injection using SDVINI, restart analysis, or another Abaqus workflow that initializes the material state after a cycle jump.

\subsection{{Summary}}

The Chaboche-v1 UMAT, cyclic Abaqus workflow, postprocessing scripts, and cycle-jump predictor were validated. Explicit cycles 2--10 provided a stabilized per-cycle increment of accumulated viscoplastic strain, and the explicit 20-cycle check confirmed the prediction accuracy with only 0.0674\% relative error in SDV1 at cycle 20.
"""
    (LATEX / "cycle_jump_chaboche_section.tex").write_text(section + "\n", encoding="utf-8")
    return ["latex/cycle_jump_chaboche_section.tex", "latex/cycle_jump_chaboche_figures_only.tex"]


def make_report(copied, missing, figures, tables, latex_files, png_ok):
    lines = [
        "# Thesis Section Build Report",
        "",
        f"Output folder: `{OUT}`",
        "",
        "## Copied files",
        "",
    ]
    lines.extend(f"- `{item}`" for item in copied)
    lines.extend(["", "## Generated figures", ""])
    lines.extend(f"- `{item}`" for item in figures)
    lines.extend(["", "## Generated tables", ""])
    lines.extend(f"- `{item}`" for item in tables)
    lines.extend(["", "## LaTeX files", ""])
    lines.extend(f"- `{item}`" for item in latex_files)
    lines.extend(["", "## Missing source files", ""])
    lines.extend([f"- `{item}`" for item in missing] if missing else ["- None"])
    lines.extend([
        "",
        "## PNG conversion",
        "",
        f"- PNG generation succeeded: {'yes' if png_ok else 'no'}",
        "",
        "## Final validation result",
        "",
        "- Predicted SDV1 at cycle 20: `0.1421214351`",
        "- Explicit SDV1 at cycle 20: `0.1420256943`",
        "- Relative error: `0.0674%`",
        "",
    ])
    (OUT / "THESIS_SECTION_BUILD_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ensure_dirs()
    copied, missing = copy_sources()
    tables = make_tables()
    figure_results = {
        "fig01_amplitude_sweep_stress_strain": make_fig01(),
        "fig02_10cycle_selected_hysteresis_loops": make_fig02(),
        "fig03_delta_sdv1_per_cycle": make_fig03(),
        "fig04_cycle_jump_sdv1_prediction": make_fig04(),
        "fig05_cycle_jump_vs_explicit_20cycles": make_fig05(),
    }
    figures = []
    png_ok = True
    for name, (svg_ok, png_file_ok) in figure_results.items():
        figures.append(f"figures/{name}.svg")
        figures.append(f"figures/{name}.png")
        png_ok = png_ok and png_file_ok
    latex_files = make_latex()
    make_report(copied, missing, figures, tables, latex_files, png_ok)
    print("Generated thesis section in:", OUT)
    print("PNG generation succeeded:", png_ok)
    print("Missing sources:", ", ".join(missing) if missing else "none")


if __name__ == "__main__":
    main()
