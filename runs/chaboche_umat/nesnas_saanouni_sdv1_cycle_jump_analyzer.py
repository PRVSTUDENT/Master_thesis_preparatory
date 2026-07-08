import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPLICIT_20_CSV = ROOT / "chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv"

DERIVATIVES_CSV = ROOT / "nesnas_sdv1_cycle_derivatives.csv"
PREDICTIONS_CSV = ROOT / "nesnas_sdv1_first_second_order_predictions.csv"
ADAPTIVE_CSV = ROOT / "nesnas_sdv1_adaptive_jump_recommendations.csv"
ADAPTIVE_VALIDATION_CSV = ROOT / "nesnas_sdv1_adaptive_jump_validation.csv"
REPORT = ROOT / "NESNAS_SDV1_CYCLE_JUMP_ANALYZER_REPORT.md"

DERIVATIVES_SVG = ROOT / "nesnas_sdv1_cycle_derivatives.svg"
PREDICTIONS_SVG = ROOT / "nesnas_sdv1_first_second_order_prediction.svg"
ADAPTIVE_SVG = ROOT / "nesnas_sdv1_adaptive_jump_size.svg"

REFERENCE_START = 2
REFERENCE_END = 10
JUMP_FROM_CYCLE = 10
TARGET_CYCLES = [20, 50, 100, 200, 500, 1000]

# Demonstration settings for the Nesnas-Saanouni-inspired large-time scale.
ETA = 1.0
JUMPMIN = 5
JUMPMAX = 60
CURVATURE_TOL = 0.01


def fmt(value):
    if isinstance(value, str):
        return value
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


def read_cycle_increments(path):
    rows = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append({
                "cycle": int(row["cycle"]),
                "SDV1_start": float(row["SDV1_start"]),
                "SDV1_end": float(row["SDV1_end"]),
                "Delta_SDV1": float(row["Delta_SDV1"]),
                "S11_at_zero_end": float(row["S11_at_zero_end"]),
                "RF1_at_zero_end": float(row["RF1_at_zero_end"]),
                "Max_S11_in_cycle": float(row["Max_S11_in_cycle"]),
                "Min_S11_in_cycle": float(row["Min_S11_in_cycle"]),
                "Stress_Amplitude": float(row["Stress_Amplitude"]),
                "Mean_Stress": float(row["Mean_Stress"]),
            })
    return rows


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: fmt(row.get(key)) for key in fieldnames})


def add_cycle_derivatives(cycles):
    previous_delta = None
    derivative_rows = []
    for row in cycles:
        delta = row["Delta_SDV1"]
        d2 = None if previous_delta is None else delta - previous_delta
        previous_delta = delta
        out = dict(row)
        out["dSDV1_dN"] = delta
        out["d2SDV1_dN2"] = d2
        derivative_rows.append(out)
    return derivative_rows


def reference_stats(derivative_rows):
    ref = [r for r in derivative_rows if REFERENCE_START <= r["cycle"] <= REFERENCE_END]
    deltas = [r["Delta_SDV1"] for r in ref]
    curvatures = [
        r["d2SDV1_dN2"]
        for r in ref
        if r["cycle"] >= 3 and r["d2SDV1_dN2"] is not None
    ]
    delta_mean = mean(deltas)
    delta_range = max(deltas) - min(deltas)
    return {
        "mean_delta": delta_mean,
        "std_delta": sample_std(deltas),
        "relative_range_delta": delta_range / delta_mean if delta_mean else 0.0,
        "mean_curvature": mean(curvatures),
        "std_curvature": sample_std(curvatures),
        "mean_stress_amplitude": mean([r["Stress_Amplitude"] for r in ref]),
        "mean_mean_stress": mean([r["Mean_Stress"] for r in ref]),
        "mean_residual_stress": mean([r["S11_at_zero_end"] for r in ref]),
    }


def first_order(y0, dn, slope):
    return y0 + dn * slope


def second_order(y0, dn, slope, curvature):
    return y0 + dn * slope + 0.5 * dn * dn * curvature


def adaptive_jump_size(y0, slope, curvature, eta, jumpmin, jumpmax, curvature_tol):
    if abs(slope) < 1.0e-30:
        raw = jumpmax
    else:
        raw = int(math.floor(eta * abs(y0) / abs(slope)))

    candidate = max(jumpmin, min(raw, jumpmax))
    candidate = max(1, candidate)

    while candidate > 1:
        p1 = first_order(y0, candidate, slope)
        p2 = second_order(y0, candidate, slope, curvature)
        denom = max(abs(p1), 1.0e-30)
        rel_diff = abs(p2 - p1) / denom
        if rel_diff <= curvature_tol or candidate <= jumpmin:
            return candidate, raw, rel_diff
        candidate -= 1

    p1 = first_order(y0, candidate, slope)
    p2 = second_order(y0, candidate, slope, curvature)
    return candidate, raw, abs(p2 - p1) / max(abs(p1), 1.0e-30)


def build_predictions(cycles, stats):
    base = next(r for r in cycles if r["cycle"] == JUMP_FROM_CYCLE)
    actual_by_cycle = {r["cycle"]: r["SDV1_end"] for r in cycles}
    rows = []
    for target in TARGET_CYCLES:
        dn = target - JUMP_FROM_CYCLE
        p1 = first_order(base["SDV1_end"], dn, stats["mean_delta"])
        p2 = second_order(base["SDV1_end"], dn, stats["mean_delta"], stats["mean_curvature"])
        actual = actual_by_cycle.get(target)
        rows.append({
            "target_cycle": target,
            "jump_from_cycle": JUMP_FROM_CYCLE,
            "cycles_skipped": dn,
            "SDV1_base": base["SDV1_end"],
            "mean_dSDV1_dN_used": stats["mean_delta"],
            "mean_d2SDV1_dN2_used": stats["mean_curvature"],
            "first_order_SDV1_pred": p1,
            "second_order_SDV1_pred": p2,
            "explicit_SDV1_reference": actual,
            "first_order_abs_error": None if actual is None else actual - p1,
            "first_order_rel_error_percent": None if actual is None else abs(actual - p1) / actual * 100.0,
            "second_order_abs_error": None if actual is None else actual - p2,
            "second_order_rel_error_percent": None if actual is None else abs(actual - p2) / actual * 100.0,
        })
    return rows


def build_adaptive_rows(derivative_rows):
    rows = []
    for row in derivative_rows:
        if row["cycle"] < 3:
            continue
        y0 = row["SDV1_end"]
        slope = row["dSDV1_dN"]
        curvature = row["d2SDV1_dN2"] or 0.0
        recommended, raw, rel_diff = adaptive_jump_size(
            y0, slope, curvature, ETA, JUMPMIN, JUMPMAX, CURVATURE_TOL
        )
        rows.append({
            "cycle": row["cycle"],
            "SDV1_end": y0,
            "dSDV1_dN": slope,
            "d2SDV1_dN2": curvature,
            "eta": ETA,
            "JUMPMIN": JUMPMIN,
            "JUMPMAX": JUMPMAX,
            "curvature_tolerance": CURVATURE_TOL,
            "raw_DeltaN": raw,
            "recommended_DeltaN": recommended,
            "first_second_order_relative_difference": rel_diff,
        })
    return rows


def build_adaptive_validation(cycles, stats, adaptive_rows):
    base = next(r for r in cycles if r["cycle"] == JUMP_FROM_CYCLE)
    jump_row = next(r for r in adaptive_rows if r["cycle"] == JUMP_FROM_CYCLE)
    actual_by_cycle = {r["cycle"]: r["SDV1_end"] for r in cycles}
    recommended_delta_n = int(jump_row["recommended_DeltaN"])
    target = JUMP_FROM_CYCLE + recommended_delta_n
    p1 = first_order(base["SDV1_end"], recommended_delta_n, stats["mean_delta"])
    p2 = second_order(base["SDV1_end"], recommended_delta_n, stats["mean_delta"], stats["mean_curvature"])
    actual = actual_by_cycle.get(target)
    return [{
        "jump_base_cycle": JUMP_FROM_CYCLE,
        "recommended_DeltaN": recommended_delta_n,
        "adaptive_target_cycle": target,
        "SDV1_base": base["SDV1_end"],
        "mean_dSDV1_dN_used": stats["mean_delta"],
        "mean_d2SDV1_dN2_used": stats["mean_curvature"],
        "first_order_SDV1_pred": p1,
        "second_order_SDV1_pred": p2,
        "explicit_SDV1_reference": actual,
        "first_order_abs_error": None if actual is None else actual - p1,
        "first_order_rel_error_percent": None if actual is None else abs(actual - p1) / actual * 100.0,
        "second_order_abs_error": None if actual is None else actual - p2,
        "second_order_rel_error_percent": None if actual is None else abs(actual - p2) / actual * 100.0,
    }]


def scale(values, lo_px, hi_px, pad=0.05):
    vmin = min(values)
    vmax = max(values)
    if abs(vmax - vmin) < 1.0e-30:
        vmin -= 1.0
        vmax += 1.0
    span = vmax - vmin
    vmin -= span * pad
    vmax += span * pad

    def mapper(v):
        return lo_px + (v - vmin) / (vmax - vmin) * (hi_px - lo_px)

    return mapper, vmin, vmax


def svg_polyline(points, color, width=2.0, dash=False):
    dash_attr = ' stroke-dasharray="7 5"' if dash else ""
    coords = " ".join("%.2f,%.2f" % (x, y) for x, y in points)
    return (
        f'<polyline points="{coords}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>'
    )


def write_svg(path, series, xlabel, ylabel, legend_items):
    width, height = 760, 520
    left, right, top, bottom = 82, 28, 32, 78
    x_values = [x for item in series for x, _ in item["points"]]
    y_values = [y for item in series for _, y in item["points"]]
    sx, xmin, xmax = scale(x_values, left, width - right)
    sy_raw, ymin, ymax = scale(y_values, bottom, height - top)

    def sy(v):
        return height - sy_raw(v)

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#222" stroke-width="1.2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#222" stroke-width="1.2"/>',
    ]
    for i in range(6):
        gx = left + i * (width - left - right) / 5.0
        gy = top + i * (height - top - bottom) / 5.0
        xv = xmin + i * (xmax - xmin) / 5.0
        yv = ymax - i * (ymax - ymin) / 5.0
        lines.append(f'<line x1="{gx:.2f}" y1="{top}" x2="{gx:.2f}" y2="{height-bottom}" stroke="#ddd" stroke-width="0.8"/>')
        lines.append(f'<line x1="{left}" y1="{gy:.2f}" x2="{width-right}" y2="{gy:.2f}" stroke="#ddd" stroke-width="0.8"/>')
        lines.append(f'<text x="{gx:.2f}" y="{height-bottom+22}" font-family="Arial" font-size="12" text-anchor="middle">{fmt(xv)}</text>')
        lines.append(f'<text x="{left-10}" y="{gy+4:.2f}" font-family="Arial" font-size="12" text-anchor="end">{fmt(yv)}</text>')

    for item in series:
        points = [(sx(x), sy(y)) for x, y in item["points"]]
        lines.append(svg_polyline(points, item["color"], item.get("width", 2.0), item.get("dash", False)))
        if item.get("markers"):
            for x, y in points:
                lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{item["color"]}"/>')

    lines.append(f'<text x="{(left+width-right)/2:.2f}" y="{height-25}" font-family="Arial" font-size="16" text-anchor="middle">{xlabel}</text>')
    lines.append(f'<text x="22" y="{height/2:.2f}" font-family="Arial" font-size="16" text-anchor="middle" transform="rotate(-90 22 {height/2:.2f})">{ylabel}</text>')

    lx, ly = width - 275, top + 12
    for i, (label, color, dash) in enumerate(legend_items):
        y = ly + i * 24
        dash_attr = ' stroke-dasharray="7 5"' if dash else ""
        lines.append(f'<line x1="{lx}" y1="{y}" x2="{lx+38}" y2="{y}" stroke="{color}" stroke-width="2.4"{dash_attr}/>')
        lines.append(f'<text x="{lx+48}" y="{y+5}" font-family="Arial" font-size="13">{label}</text>')

    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def make_plots(cycles, derivative_rows, prediction_rows, adaptive_rows, stats):
    write_svg(
        DERIVATIVES_SVG,
        [
            {
                "points": [(r["cycle"], r["Delta_SDV1"]) for r in derivative_rows],
                "color": "#1f77b4",
                "markers": True,
            },
            {
                "points": [(REFERENCE_START, stats["mean_delta"]), (20, stats["mean_delta"])],
                "color": "#d62728",
                "dash": True,
            },
        ],
        "Cycle",
        "Delta SDV1 per cycle",
        [("Delta SDV1", "#1f77b4", False), ("Mean cycles 2-10", "#d62728", True)],
    )

    actual_points = [(r["cycle"], r["SDV1_end"]) for r in cycles]
    fo_points = [(JUMP_FROM_CYCLE, actual_points[JUMP_FROM_CYCLE - 1][1])] + [
        (r["target_cycle"], r["first_order_SDV1_pred"]) for r in prediction_rows
    ]
    so_points = [(JUMP_FROM_CYCLE, actual_points[JUMP_FROM_CYCLE - 1][1])] + [
        (r["target_cycle"], r["second_order_SDV1_pred"]) for r in prediction_rows
    ]
    write_svg(
        PREDICTIONS_SVG,
        [
            {"points": actual_points, "color": "#1f77b4", "markers": True},
            {"points": fo_points, "color": "#2ca02c", "dash": True},
            {"points": so_points, "color": "#9467bd", "dash": True},
        ],
        "Cycle",
        "Accumulated viscoplastic strain SDV1",
        [
            ("Explicit Abaqus 1-20", "#1f77b4", False),
            ("First-order jump", "#2ca02c", True),
            ("Second-order jump", "#9467bd", True),
        ],
    )

    write_svg(
        ADAPTIVE_SVG,
        [
            {
                "points": [(r["cycle"], r["recommended_DeltaN"]) for r in adaptive_rows],
                "color": "#ff7f0e",
                "markers": True,
            }
        ],
        "Cycle used as jump base",
        "Recommended Delta N",
        [("Adaptive Delta N", "#ff7f0e", False)],
    )


def write_report(stats, prediction_rows, adaptive_rows, adaptive_validation_rows):
    cycle20 = next(r for r in prediction_rows if r["target_cycle"] == 20)
    jump10 = next(r for r in adaptive_rows if r["cycle"] == JUMP_FROM_CYCLE)
    adaptive_validation = adaptive_validation_rows[0]
    lines = [
        "# Nesnas-Saanouni-Inspired SDV1 Cycle-Jump Analyzer",
        "",
        "This postprocessing script bridges the validated Chaboche-v1 milestone to the Nesnas-Saanouni two-time-scale idea. It does not rerun Abaqus, modify the UMAT, or inject jumped STATEV values.",
        "",
        "## Input",
        "",
        f"- Explicit reference CSV: `{EXPLICIT_20_CSV.name}`",
        f"- Scalar cycle-evolution marker: `SDV1 = accumulated viscoplastic strain p`",
        f"- Stabilized reference window: cycles `{REFERENCE_START}-{REFERENCE_END}`",
        "",
        "## Reference Statistics",
        "",
        f"- Mean dSDV1/dN over cycles 2-10: `{fmt(stats['mean_delta'])}`",
        f"- Std dSDV1/dN over cycles 2-10: `{fmt(stats['std_delta'])}`",
        f"- Relative range over cycles 2-10: `{fmt(stats['relative_range_delta'])}` (`{fmt(stats['relative_range_delta'] * 100.0)}%`)",
        f"- Mean d2SDV1/dN2 over cycles 2-10: `{fmt(stats['mean_curvature'])}`",
        "",
        "## Adaptive Jump Settings",
        "",
        f"- eta: `{ETA}`",
        f"- JUMPMIN: `{JUMPMIN}`",
        f"- JUMPMAX: `{JUMPMAX}`",
        f"- Curvature check tolerance: `{CURVATURE_TOL}`",
        f"- Recommended Delta N when cycle 10 is used as the jump base: `{jump10['recommended_DeltaN']}`",
        "",
        "## Cycle-20 Validation",
        "",
        f"- First-order predicted SDV1 at cycle 20: `{fmt(cycle20['first_order_SDV1_pred'])}`",
        f"- Second-order predicted SDV1 at cycle 20: `{fmt(cycle20['second_order_SDV1_pred'])}`",
        f"- Explicit SDV1 at cycle 20: `{fmt(cycle20['explicit_SDV1_reference'])}`",
        f"- First-order relative error: `{fmt(cycle20['first_order_rel_error_percent'])}%`",
        f"- Second-order relative error: `{fmt(cycle20['second_order_rel_error_percent'])}%`",
        "",
        "## Adaptive Jump Validation",
        "",
        "The adaptive estimator recommends a conservative jump from cycle 10 to cycle 19. The fixed cycle-20 target is kept separately because an explicit 20-cycle Abaqus reference is available for the original validation.",
        "",
        f"- Jump base cycle: `{adaptive_validation['jump_base_cycle']}`",
        f"- Recommended Delta N: `{adaptive_validation['recommended_DeltaN']}`",
        f"- Adaptive target cycle: `{adaptive_validation['adaptive_target_cycle']}`",
        f"- First-order predicted SDV1: `{fmt(adaptive_validation['first_order_SDV1_pred'])}`",
        f"- Second-order predicted SDV1: `{fmt(adaptive_validation['second_order_SDV1_pred'])}`",
        f"- Explicit SDV1 reference: `{fmt(adaptive_validation['explicit_SDV1_reference'])}`",
        f"- First-order relative error: `{fmt(adaptive_validation['first_order_rel_error_percent'])}%`",
        f"- Second-order relative error: `{fmt(adaptive_validation['second_order_rel_error_percent'])}%`",
        "",
        "## Interpretation",
        "",
        "The first-order SDV1 extrapolation reproduces the explicit 20-cycle result with the already validated error level. The second-order estimate is also reported, but for the nearly stabilized response the curvature term is small and mainly serves as a jump-size control diagnostic.",
        "",
        "This is still a Level-1 postprocessing cycle-jump method. A Nesnas-Saanouni-style FE acceleration would require jumping the complete material state and resuming Abaqus from the extrapolated STATEV field.",
        "",
        "## Generated Files",
        "",
        f"- `{DERIVATIVES_CSV.name}`",
        f"- `{PREDICTIONS_CSV.name}`",
        f"- `{ADAPTIVE_CSV.name}`",
        f"- `{ADAPTIVE_VALIDATION_CSV.name}`",
        f"- `{DERIVATIVES_SVG.name}`",
        f"- `{PREDICTIONS_SVG.name}`",
        f"- `{ADAPTIVE_SVG.name}`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    cycles = read_cycle_increments(EXPLICIT_20_CSV)
    derivative_rows = add_cycle_derivatives(cycles)
    stats = reference_stats(derivative_rows)
    prediction_rows = build_predictions(cycles, stats)
    adaptive_rows = build_adaptive_rows(derivative_rows)
    adaptive_validation_rows = build_adaptive_validation(cycles, stats, adaptive_rows)

    write_csv(
        DERIVATIVES_CSV,
        derivative_rows,
        [
            "cycle",
            "SDV1_start",
            "SDV1_end",
            "Delta_SDV1",
            "dSDV1_dN",
            "d2SDV1_dN2",
            "S11_at_zero_end",
            "RF1_at_zero_end",
            "Max_S11_in_cycle",
            "Min_S11_in_cycle",
            "Stress_Amplitude",
            "Mean_Stress",
        ],
    )
    write_csv(
        PREDICTIONS_CSV,
        prediction_rows,
        [
            "target_cycle",
            "jump_from_cycle",
            "cycles_skipped",
            "SDV1_base",
            "mean_dSDV1_dN_used",
            "mean_d2SDV1_dN2_used",
            "first_order_SDV1_pred",
            "second_order_SDV1_pred",
            "explicit_SDV1_reference",
            "first_order_abs_error",
            "first_order_rel_error_percent",
            "second_order_abs_error",
            "second_order_rel_error_percent",
        ],
    )
    write_csv(
        ADAPTIVE_CSV,
        adaptive_rows,
        [
            "cycle",
            "SDV1_end",
            "dSDV1_dN",
            "d2SDV1_dN2",
            "eta",
            "JUMPMIN",
            "JUMPMAX",
            "curvature_tolerance",
            "raw_DeltaN",
            "recommended_DeltaN",
            "first_second_order_relative_difference",
        ],
    )
    write_csv(
        ADAPTIVE_VALIDATION_CSV,
        adaptive_validation_rows,
        [
            "jump_base_cycle",
            "recommended_DeltaN",
            "adaptive_target_cycle",
            "SDV1_base",
            "mean_dSDV1_dN_used",
            "mean_d2SDV1_dN2_used",
            "first_order_SDV1_pred",
            "second_order_SDV1_pred",
            "explicit_SDV1_reference",
            "first_order_abs_error",
            "first_order_rel_error_percent",
            "second_order_abs_error",
            "second_order_rel_error_percent",
        ],
    )
    make_plots(cycles, derivative_rows, prediction_rows, adaptive_rows, stats)
    write_report(stats, prediction_rows, adaptive_rows, adaptive_validation_rows)

    cycle20 = next(r for r in prediction_rows if r["target_cycle"] == 20)
    jump10 = next(r for r in adaptive_rows if r["cycle"] == JUMP_FROM_CYCLE)
    adaptive_validation = adaptive_validation_rows[0]
    print("Nesnas-style SDV1 analyzer complete")
    print("Mean dSDV1/dN cycles 2-10:", fmt(stats["mean_delta"]))
    print("Mean d2SDV1/dN2 cycles 2-10:", fmt(stats["mean_curvature"]))
    print("Recommended DeltaN from cycle 10:", jump10["recommended_DeltaN"])
    print("Cycle 20 first-order prediction:", fmt(cycle20["first_order_SDV1_pred"]))
    print("Cycle 20 explicit:", fmt(cycle20["explicit_SDV1_reference"]))
    print("Cycle 20 first-order relative error percent:", fmt(cycle20["first_order_rel_error_percent"]))
    print("Adaptive target cycle:", adaptive_validation["adaptive_target_cycle"])
    print("Adaptive first-order relative error percent:", fmt(adaptive_validation["first_order_rel_error_percent"]))


if __name__ == "__main__":
    main()
