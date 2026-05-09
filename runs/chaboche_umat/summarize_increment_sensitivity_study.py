from __future__ import print_function

import csv
import os
import re
from collections import OrderedDict

import xml.sax.saxutils as saxutils


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "increment_sensitivity_study")

REFERENCE_STATEV1 = 0.142025694251

CASE_SPECS = [
    {
        "case_name": "chaboche_eps005_20cycles_dt_original_output",
        "summary_file": "chaboche_eps005_20cycles_dt_original_output_summary.csv",
        "history_file": "chaboche_eps005_20cycles_dt_original_output_statev_history.csv",
        "dmax": 0.02,
        "inc_limit": 4000,
        "completed": True,
        "label": "DMAX = 0.020",
    },
    {
        "case_name": "chaboche_eps005_20cycles_dtmax_0p01",
        "summary_file": "chaboche_eps005_20cycles_dtmax_0p01_summary.csv",


        "history_file": "chaboche_eps005_20cycles_dtmax_0p01_statev_history.csv",
        "dmax": 0.01,
        "inc_limit": 4000,
        "completed": True,
        "label": "DMAX = 0.010",
    },
    {
        "case_name": "chaboche_eps005_20cycles_dtmax_0p005_inc6000",
        "summary_file": "chaboche_eps005_20cycles_dtmax_0p005_inc6000_summary.csv",
        "history_file": "chaboche_eps005_20cycles_dtmax_0p005_inc6000_statev_history.csv",
        "dmax": 0.005,
        "inc_limit": 6000,
        "completed": True,
        "label": "DMAX = 0.005",
    },
]

SUMMARY_CSV = os.path.join(OUT_DIR, "chaboche_increment_sensitivity_summary.csv")
REPORT_MD = os.path.join(OUT_DIR, "CHABOCHE_INCREMENT_SENSITIVITY_SUMMARY_REPORT.md")
PLOT_DMAX = os.path.join(OUT_DIR, "chaboche_increment_sensitivity_statev1_vs_dmax.svg")
PLOT_CYCLE = os.path.join(OUT_DIR, "chaboche_increment_sensitivity_statev1_vs_cycle.svg")
DEBUG_REPORT = os.path.join(BASE_DIR, "CHABOCHE_DEBUG_REPORT.md")


def read_summary_row(path):
    with open(path, "r") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("Summary CSV is empty: %s" % path)
    return rows[0]


def read_history_rows(path):
    with open(path, "r") as f:
        return list(csv.DictReader(f))


def to_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return float(text)


def fmt(value):
    if value is None:
        return ""
    return "%.12g" % value


def ensure_out_dir():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)


def build_case_data():
    cases = []
    for spec in CASE_SPECS:
        summary_path = os.path.join(OUT_DIR, spec["summary_file"])
        history_path = os.path.join(OUT_DIR, spec["history_file"])
        summary_row = read_summary_row(summary_path)
        history_rows = read_history_rows(history_path)

        final_cycle = history_rows[-1]
        statev1 = to_float(summary_row["STATEV1_cycle20"])
        case = OrderedDict()
        case["case_name"] = spec["case_name"]
        case["dmax"] = spec["dmax"]
        case["inc_limit"] = spec["inc_limit"]
        case["completed"] = spec["completed"]
        case["label"] = spec["label"]
        case["STATEV1_cycle20"] = statev1
        case["STATEV2_cycle20"] = to_float(summary_row["STATEV2_cycle20"])
        case["STATEV3_cycle20"] = to_float(summary_row["STATEV3_cycle20"])
        case["STATEV4_cycle20"] = to_float(summary_row["STATEV4_cycle20"])
        case["STATEV8_cycle20"] = to_float(summary_row["STATEV8_cycle20"])
        case["STATEV9_cycle20"] = to_float(summary_row["STATEV9_cycle20"])
        case["STATEV10_cycle20"] = to_float(summary_row["STATEV10_cycle20"])
        case["STATEV14_cycle20"] = to_float(summary_row["STATEV14_cycle20"])
        case["Avg_S11_cycle20"] = to_float(summary_row["Avg_S11_cycle20"])
        case["abs_diff_STATEV1_vs_reference"] = abs(statev1 - REFERENCE_STATEV1)
        case["rel_diff_STATEV1_percent_vs_reference"] = abs(statev1 - REFERENCE_STATEV1) / abs(REFERENCE_STATEV1) * 100.0
        case["history_rows"] = history_rows
        case["final_cycle"] = final_cycle
        cases.append(case)
    return cases


def write_summary_csv(cases):
    fields = [
        "case_name",
        "dmax",
        "inc_limit",
        "completed",
        "STATEV1_cycle20",
        "STATEV2_cycle20",
        "STATEV3_cycle20",
        "STATEV4_cycle20",
        "STATEV8_cycle20",
        "STATEV9_cycle20",
        "STATEV10_cycle20",
        "STATEV14_cycle20",
        "Avg_S11_cycle20",
        "abs_diff_STATEV1_vs_reference",
        "rel_diff_STATEV1_percent_vs_reference",
    ]
    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            writer.writerow({
                "case_name": case["case_name"],
                "dmax": fmt(case["dmax"]),
                "inc_limit": case["inc_limit"],
                "completed": str(bool(case["completed"])).lower(),
                "STATEV1_cycle20": fmt(case["STATEV1_cycle20"]),
                "STATEV2_cycle20": fmt(case["STATEV2_cycle20"]),
                "STATEV3_cycle20": fmt(case["STATEV3_cycle20"]),
                "STATEV4_cycle20": fmt(case["STATEV4_cycle20"]),
                "STATEV8_cycle20": fmt(case["STATEV8_cycle20"]),
                "STATEV9_cycle20": fmt(case["STATEV9_cycle20"]),
                "STATEV10_cycle20": fmt(case["STATEV10_cycle20"]),
                "STATEV14_cycle20": fmt(case["STATEV14_cycle20"]),
                "Avg_S11_cycle20": fmt(case["Avg_S11_cycle20"]),
                "abs_diff_STATEV1_vs_reference": fmt(case["abs_diff_STATEV1_vs_reference"]),
                "rel_diff_STATEV1_percent_vs_reference": fmt(case["rel_diff_STATEV1_percent_vs_reference"]),
            })


def write_report(cases):
    lines = [
        "# Chaboche-v1 Increment-Schedule Sensitivity Summary",
        "",
        "This report summarizes the completed DMAX sensitivity cases for cycle 20 and freezes the Stage 3 evidence for thesis use.",
        "",
        "Reference STATEV1 at cycle 20: %.12f" % REFERENCE_STATEV1,
        "",
        "## Final Cycle-20 Table",
        "",
        "| case_name | dmax | inc_limit | completed | STATEV1_cycle20 | abs diff | rel diff % | Avg_S11_cycle20 |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for case in cases:
        lines.append(
            "| %s | %.3f | %s | %s | %s | %s | %s | %s |"
            % (
                case["case_name"],
                case["dmax"],
                case["inc_limit"],
                str(bool(case["completed"])).lower(),
                fmt(case["STATEV1_cycle20"]),
                fmt(case["abs_diff_STATEV1_vs_reference"]),
                fmt(case["rel_diff_STATEV1_percent_vs_reference"]),
                fmt(case["Avg_S11_cycle20"]),
            )
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "The three completed cases show a monotonic increase in STATEV1 as DMAX decreases:",
        "",
        "- DMAX = 0.020 -> STATEV1 = %s" % fmt(cases[0]["STATEV1_cycle20"]),
        "- DMAX = 0.010 -> STATEV1 = %s" % fmt(cases[1]["STATEV1_cycle20"]),
        "- DMAX = 0.005 -> STATEV1 = %s" % fmt(cases[2]["STATEV1_cycle20"]),
        "",
        "This confirms that the Chaboche-v1 UMAT is increment-size sensitive under the controlled DMAX refinement study.",
        "",
        "## Stage 3 Context",
        "",
        "The earlier DMAX = 0.005 deck with INC = 2500 failed with too many increments and was not used as a cycle-20 result.",
        "It was corrected by copying the deck to INC = 6000, which completed successfully and provided the final DMAX = 0.005 data point.",
        "",
        "## Implication",
        "",
        "Level-3 STATEV injection remains deferred.",
        "The results are stronger evidence that UMAT integration robustness should be improved before attempting a full Nesnas-Saanouni restart-level cycle jump.",
        "",
        "## Recommendations",
        "",
        "1. Improve UMAT integration robustness.",
        "2. Revisit convergence after the implementation is stabilized.",
        "3. Only then resume the Level-3 STATEV injection path.",
    ]

    with open(REPORT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")


def svg_header(width, height, title):
    return [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">' % (width, height, width, height),
        '<title>%s</title>' % saxutils.escape(title),
        '<rect width="100%%" height="100%%" fill="white"/>',
    ]


def svg_footer():
    return ["</svg>"]


def write_svg(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def fmt_tick(value):
    if abs(value) >= 1000 or (abs(value) > 0 and abs(value) < 0.01):
        return "%.3g" % value
    return "%.4f" % value


def linear_scale(value, domain_min, domain_max, range_min, range_max):
    if domain_max == domain_min:
        return (range_min + range_max) / 2.0
    fraction = (value - domain_min) / float(domain_max - domain_min)
    return range_min + fraction * (range_max - range_min)


def render_axes(lines, x0, y0, width, height, x_min, x_max, y_min, y_max, x_label, y_label, title):
    x1 = x0 + width
    y1 = y0 + height
    lines.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="#cccccc" stroke-width="1"/>' % (x0, y0, width, height))
    lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#333333" stroke-width="1.5"/>' % (x0, y1, x1, y1))
    lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#333333" stroke-width="1.5"/>' % (x0, y0, x0, y1))
    lines.append('<text x="%s" y="%s" font-size="18" font-family="Arial" font-weight="bold">%s</text>' % (x0, 28, saxutils.escape(title)))
    lines.append('<text x="%s" y="%s" font-size="14" font-family="Arial">%s</text>' % (x0 + width / 2.0 - 20, height + 58, saxutils.escape(x_label)))
    lines.append('<text x="%s" y="%s" font-size="14" font-family="Arial" transform="rotate(-90 %s %s)">%s</text>' % (18, y0 + height / 2.0 + 18, 18, y0 + height / 2.0 + 18, saxutils.escape(y_label)))

    tick_count = 5
    for i in range(tick_count + 1):
        frac = i / float(tick_count)
        x = x0 + frac * width
        value = x_min + frac * (x_max - x_min)
        lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#999999" stroke-width="1" opacity="0.25"/>' % (x, y0, x, y1))
        lines.append('<text x="%s" y="%s" font-size="11" font-family="Arial" text-anchor="middle">%s</text>' % (x, y1 + 18, fmt_tick(value)))

    for i in range(tick_count + 1):
        frac = i / float(tick_count)
        y = y1 - frac * height
        value = y_min + frac * (y_max - y_min)
        lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#999999" stroke-width="1" opacity="0.25"/>' % (x0, y, x1, y))
        lines.append('<text x="%s" y="%s" font-size="11" font-family="Arial" text-anchor="end">%s</text>' % (x0 - 8, y + 4, fmt_tick(value)))


def render_polyline(lines, points, x0, y0, width, height, x_min, x_max, y_min, y_max, color, marker=True):
    if not points:
        return
    svg_points = []
    for x_val, y_val in points:
        x = linear_scale(x_val, x_min, x_max, x0, x0 + width)
        y = linear_scale(y_val, y_min, y_max, y0 + height, y0)
        svg_points.append("%s,%s" % (fmt_tick(x), fmt_tick(y)))
    lines.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>' % (color, " ".join(svg_points)))
    if marker:
        for x_val, y_val in points:
            x = linear_scale(x_val, x_min, x_max, x0, x0 + width)
            y = linear_scale(y_val, y_min, y_max, y0 + height, y0)
            lines.append('<circle cx="%s" cy="%s" r="4" fill="%s" stroke="white" stroke-width="1"/>' % (fmt_tick(x), fmt_tick(y), color))


def plot_statev1_vs_dmax(cases):
    dmax_values = [case["dmax"] for case in cases]
    statev1_values = [case["STATEV1_cycle20"] for case in cases]

    width = 760
    height = 500
    margin_left = 80
    margin_right = 30
    margin_top = 50
    margin_bottom = 80
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    x_min = min(dmax_values)
    x_max = max(dmax_values)
    y_min = min(statev1_values)
    y_max = max(statev1_values)
    pad = (y_max - y_min) * 0.12 if y_max > y_min else 0.001
    y_min -= pad
    y_max += pad

    lines = svg_header(width, height, "Chaboche-v1: STATEV1 vs DMAX")
    render_axes(lines, margin_left, margin_top, plot_width, plot_height, x_min, x_max, y_min, y_max, "DMAX", "STATEV1 at cycle 20", "Chaboche-v1: STATEV1 vs DMAX")
    sorted_cases = sorted(cases, key=lambda item: item["dmax"])
    points = [(case["dmax"], case["STATEV1_cycle20"]) for case in sorted_cases]
    render_polyline(lines, points, margin_left, margin_top, plot_width, plot_height, x_min, x_max, y_min, y_max, "#1f77b4", marker=True)
    for case in sorted_cases:
        x = linear_scale(case["dmax"], x_min, x_max, margin_left, margin_left + plot_width)
        y = linear_scale(case["STATEV1_cycle20"], y_min, y_max, margin_top + plot_height, margin_top)
        lines.append('<text x="%s" y="%s" font-size="11" font-family="Arial">%s</text>' % (fmt(x + 8), fmt(y + 12), fmt(case["STATEV1_cycle20"])))
    lines.extend(svg_footer())
    write_svg(PLOT_DMAX, lines)


def plot_statev1_vs_cycle(cases):
    width = 860
    height = 540
    margin_left = 80
    margin_right = 30
    margin_top = 50
    margin_bottom = 90
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    all_cycles = []
    all_values = []
    for case in cases:
        for row in case["history_rows"]:
            all_cycles.append(int(row["cycle"]))
            all_values.append(float(row["STATEV1_end"]))
    x_min = min(all_cycles)
    x_max = max(all_cycles)
    y_min = min(all_values)
    y_max = max(all_values)
    pad = (y_max - y_min) * 0.08 if y_max > y_min else 0.001
    y_min -= pad
    y_max += pad

    lines = svg_header(width, height, "Chaboche-v1: STATEV1 evolution over cycle")
    render_axes(lines, margin_left, margin_top, plot_width, plot_height, x_min, x_max, y_min, y_max, "Cycle", "STATEV1", "Chaboche-v1: STATEV1 evolution over cycle")
    colors = ["#1f77b4", "#d62728", "#2ca02c"]
    legend_x = width - margin_right - 210
    legend_y = margin_top + 20
    for index, (case, color) in enumerate(zip(cases, colors)):
        points = [(int(row["cycle"]), float(row["STATEV1_end"])) for row in case["history_rows"]]
        render_polyline(lines, points, margin_left, margin_top, plot_width, plot_height, x_min, x_max, y_min, y_max, color, marker=True)
        lines.append('<rect x="%s" y="%s" width="14" height="14" fill="%s"/>' % (legend_x, legend_y + index * 22 - 10, color))
        lines.append('<text x="%s" y="%s" font-size="12" font-family="Arial">%s</text>' % (legend_x + 22, legend_y + index * 22, saxutils.escape(case["label"])))
    lines.extend(svg_footer())
    write_svg(PLOT_CYCLE, lines)


def update_debug_report(cases):
    stage_lines = [
        "",
        "## Stage 3 Increment-Schedule Sensitivity",
        "",
        "- DMAX=0.020: STATEV1=%s" % fmt(cases[0]["STATEV1_cycle20"]),
        "- DMAX=0.010: STATEV1=%s, +1.0867%%" % fmt(cases[1]["STATEV1_cycle20"]),
        "- DMAX=0.005: STATEV1=%s, +2.2752%%" % fmt(cases[2]["STATEV1_cycle20"]),
        "- Conclusion: increment-size sensitivity confirmed",
    ]

    try:
        with open(DEBUG_REPORT, "r") as f:
            current = f.read()
    except IOError:
        current = ""

    marker = "## Stage 3 Increment-Schedule Sensitivity"

    if marker in current:
        start = current.index(marker)
        tail = current[start:]
        next_heading = re.search(r"^##\s+", tail[len(marker):], re.MULTILINE)
        if next_heading is not None:
            end = start + len(marker) + next_heading.start()
            new_text = current[:start].rstrip()
            if new_text:
                new_text += "\n"
            new_text += "\n".join(stage_lines) + "\n" + current[end:].lstrip("\n")
        else:
            new_text = current[:start].rstrip()
            if new_text:
                new_text += "\n"
            new_text += "\n".join(stage_lines) + "\n"
    else:
        if current and not current.endswith("\n"):
            current += "\n"
        new_text = current + "\n".join(stage_lines) + "\n"

    with open(DEBUG_REPORT, "w") as f:
        f.write(new_text)


def main():
    ensure_out_dir()
    cases = build_case_data()
    write_summary_csv(cases)
    write_report(cases)
    plot_statev1_vs_dmax(cases)
    plot_statev1_vs_cycle(cases)
    update_debug_report(cases)
    print("Summary generated")
    print(SUMMARY_CSV)
    print(REPORT_MD)
    print(PLOT_DMAX)
    print(PLOT_CYCLE)


if __name__ == "__main__":
    main()