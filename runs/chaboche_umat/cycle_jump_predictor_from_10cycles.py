import csv
import math


INCREMENT_CSV = "chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv"
PREDICTIONS_CSV = "chaboche_cycle_jump_predictions.csv"
CURVE_CSV = "chaboche_cycle_jump_curve_1_to_1000.csv"
REPORT = "CHABOCHE_CYCLE_JUMP_PREDICTION_REPORT.md"

TARGET_CYCLES = [20, 50, 100, 200, 500, 1000]


def fmt(v):
    return "%.10g" % v


def mean(values):
    return sum(values) / len(values) if values else 0.0


def sample_std(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def read_cycles():
    rows = []
    with open(INCREMENT_CSV, newline="") as f:
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


def stats(cycles):
    ref = [r for r in cycles if 2 <= r["cycle"] <= 10]
    deltas = [r["Delta_SDV1"] for r in ref]
    delta_mean = mean(deltas)
    delta_std = sample_std(deltas)
    delta_range = max(deltas) - min(deltas)
    delta_rel_range = delta_range / delta_mean if delta_mean else 0.0
    return {
        "reference_start": 2,
        "reference_end": 10,
        "mean_delta": delta_mean,
        "std_delta": delta_std,
        "relative_range_delta": delta_rel_range,
        "mean_stress_amplitude": mean([r["Stress_Amplitude"] for r in ref]),
        "mean_mean_stress": mean([r["Mean_Stress"] for r in ref]),
        "mean_residual_stress": mean([r["S11_at_zero_end"] for r in ref]),
    }


def write_predictions(cycles, s):
    sdv1_10 = next(r["SDV1_end"] for r in cycles if r["cycle"] == 10)
    rows = []
    for n in TARGET_CYCLES:
        predicted = sdv1_10 + (n - 10) * s["mean_delta"]
        rows.append({
            "target_cycle": n,
            "predicted_SDV1": predicted,
            "jump_from_cycle": 10,
            "cycles_skipped": n - 10,
            "mean_Delta_SDV1_used": s["mean_delta"],
            "Delta_SDV1_std_reference": s["std_delta"],
            "Delta_SDV1_relative_range_reference": s["relative_range_delta"],
        })

    fields = ["target_cycle", "predicted_SDV1", "jump_from_cycle", "cycles_skipped",
              "mean_Delta_SDV1_used", "Delta_SDV1_std_reference",
              "Delta_SDV1_relative_range_reference"]
    with open(PREDICTIONS_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for row in rows:
            w.writerow([row["target_cycle"], fmt(row["predicted_SDV1"]),
                        row["jump_from_cycle"], row["cycles_skipped"],
                        fmt(row["mean_Delta_SDV1_used"]),
                        fmt(row["Delta_SDV1_std_reference"]),
                        fmt(row["Delta_SDV1_relative_range_reference"])])
    return rows


def write_curve(cycles, s):
    explicit = {r["cycle"]: r["SDV1_end"] for r in cycles}
    sdv1_10 = explicit[10]
    rows = []
    for n in range(1, 1001):
        if n <= 10:
            rows.append((n, explicit[n], "explicit_abaqus"))
        else:
            rows.append((n, sdv1_10 + (n - 10) * s["mean_delta"], "cycle_jump_prediction"))

    with open(CURVE_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cycle", "SDV1_actual_or_predicted", "source"])
        for n, value, source in rows:
            w.writerow([n, fmt(value), source])
    return rows


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


def make_svg(filename, series, xlabel, ylabel, title, hline=None):
    W, H = 900, 600
    ml, mr, mt, mb = 95, 160, 50, 80
    pw, ph = W - ml - mr, H - mt - mb
    all_series = list(series)
    if hline is not None:
        all_series.append({"data": [(min(x for s in series for x, y in s["data"]), hline),
                                    (max(x for s in series for x, y in s["data"]), hline)]})
    xmin, xmax, ymin, ymax = svg_bounds(all_series)

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

    if hline is not None:
        y = sy(hline)
        svg.append('<line x1="%d" y1="%.2f" x2="%d" y2="%.2f" stroke="#777777" stroke-width="2" stroke-dasharray="7 5"/>' % (ml, y, ml + pw, y))

    ly = mt + 8
    for item in series:
        svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"/>' % (ml + pw + 25, ly, ml + pw + 55, ly, item["color"]))
        svg.append('<text x="%d" y="%d" font-size="14" font-family="Arial">%s</text>' % (ml + pw + 65, ly + 5, item["label"]))
        ly += 24
    if hline is not None:
        svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#777777" stroke-width="2" stroke-dasharray="7 5"/>' % (ml + pw + 25, ly, ml + pw + 55, ly))
        svg.append('<text x="%d" y="%d" font-size="14" font-family="Arial">mean cycles 2-10</text>' % (ml + pw + 65, ly + 5))

    svg.extend([
        '<text x="%.2f" y="%d" text-anchor="middle" font-size="18" font-family="Arial">%s</text>' % (ml + pw / 2.0, H - 25, xlabel),
        '<text x="25" y="%.2f" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 25,%.2f)">%s</text>' % (mt + ph / 2.0, mt + ph / 2.0, ylabel),
        '</svg>',
    ])
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def make_plots(cycles, curve, s):
    explicit = [(n, value) for n, value, source in curve if source == "explicit_abaqus"]
    predicted = [(n, value) for n, value, source in curve if source == "cycle_jump_prediction"]
    make_svg("chaboche_cycle_jump_sdv1_prediction.svg",
             [{"label": "explicit cycles 1-10", "color": "#1f77b4", "data": explicit},
              {"label": "cycle-jump prediction", "color": "#d62728", "data": predicted}],
             "Cycle", "SDV1", "Chaboche cycle-jump SDV1 prediction")

    make_svg("chaboche_cycle_jump_delta_sdv1_reference.svg",
             [{"label": "explicit Delta SDV1", "color": "black",
               "data": [(r["cycle"], r["Delta_SDV1"]) for r in cycles]}],
             "Cycle", "Delta SDV1", "Reference Delta SDV1 per cycle",
             hline=s["mean_delta"])


def write_report(s, predictions):
    generated = [
        "cycle_jump_predictor_from_10cycles.py",
        PREDICTIONS_CSV,
        CURVE_CSV,
        "chaboche_cycle_jump_sdv1_prediction.svg",
        "chaboche_cycle_jump_delta_sdv1_reference.svg",
        REPORT,
    ]
    lines = [
        "# Chaboche-v1 cycle-jump prediction report",
        "",
        "## Purpose",
        "",
        "This postprocessing-level cycle-jump demonstration uses the stabilized per-cycle increment of accumulated viscoplastic strain from the explicit 10-cycle Abaqus baseline to estimate long-cycle SDV1 growth without rerunning Abaqus.",
        "",
        "Total SDV1 is accumulated viscoplastic strain p, so it is cumulative and should increase monotonically. The correct stabilization metric is Delta_SDV1 per cycle, because that measures whether the cyclic plastic strain rate has settled.",
        "",
        "## Reference Window",
        "",
        "- Reference cycles: 2-10",
        "- Mean Delta_SDV1: %s" % fmt(s["mean_delta"]),
        "- Standard deviation of Delta_SDV1: %s" % fmt(s["std_delta"]),
        "- Relative range of Delta_SDV1: %s" % fmt(s["relative_range_delta"]),
        "- Mean stress amplitude: %s MPa" % fmt(s["mean_stress_amplitude"]),
        "- Mean mean-stress: %s MPa" % fmt(s["mean_mean_stress"]),
        "- Mean residual stress at zero strain: %s MPa" % fmt(s["mean_residual_stress"]),
        "",
        "## Predictions",
        "",
        "| target cycle | predicted SDV1 | cycles skipped |",
        "|---:|---:|---:|",
    ]
    for row in predictions:
        lines.append("| %d | %s | %d |" % (row["target_cycle"], fmt(row["predicted_SDV1"]), row["cycles_skipped"]))
    lines.extend([
        "",
        "## Scope",
        "",
        "This is a postprocessing-level cycle-jump predictor, not yet an Abaqus restart with injected STATEV. The next implementation step would be to use SDVINI or initial solution-dependent variables to start Abaqus from a jumped internal state.",
        "",
        "## Generated files",
        "",
    ])
    lines.extend(["- " + name for name in generated])
    lines.append("")
    with open(REPORT, "w") as f:
        f.write("\n".join(lines))


def main():
    cycles = read_cycles()
    s = stats(cycles)
    predictions = write_predictions(cycles, s)
    curve = write_curve(cycles, s)
    make_plots(cycles, curve, s)
    write_report(s, predictions)

    print("Reference statistics")
    print("  mean Delta_SDV1 cycles 2-10 =", fmt(s["mean_delta"]))
    print("  std Delta_SDV1 cycles 2-10 =", fmt(s["std_delta"]))
    print("  relative range Delta_SDV1 cycles 2-10 =", fmt(s["relative_range_delta"]))
    print("  mean stress amplitude cycles 2-10 =", fmt(s["mean_stress_amplitude"]))
    print("  mean mean-stress cycles 2-10 =", fmt(s["mean_mean_stress"]))
    print("  mean residual stress cycles 2-10 =", fmt(s["mean_residual_stress"]))
    print("")
    print("Prediction table")
    for row in predictions:
        print("  N=%d, predicted SDV1=%s, skipped=%d" %
              (row["target_cycle"], fmt(row["predicted_SDV1"]), row["cycles_skipped"]))


if __name__ == "__main__":
    main()
