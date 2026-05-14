import csv
import os

from PIL import Image, ImageDraw, ImageFont


ROOT = r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat"

OUT_DIR = os.path.join(ROOT, "stage9_longer_jump_error_accumulation")
SCAN_CSV = os.path.join(
    ROOT,
    "stage9_thousand_cycle_error_accumulation",
    "prediction_scan",
    "stage9_long_horizon_prediction_scan.csv",
)

SUMMARY_CSV = os.path.join(OUT_DIR, "stage9_error_accumulation_summary.csv")
PLOT_ERR = os.path.join(OUT_DIR, "stage9_validated_error_vs_cycle.png")
PLOT_SCAN = os.path.join(OUT_DIR, "stage9_long_horizon_prediction_scan.png")


def nice_limits(values):
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < 1.0e-30:
        pad = abs(hi) * 0.1 if abs(hi) > 1.0e-30 else 1.0
        return lo - pad, hi + pad
    pad = 0.08 * (hi - lo)
    return lo - pad, hi + pad


def draw_plot(path, x_values, series, xlabel, ylabel, title):
    width, height = 1500, 950
    left, right, top, bottom = 150, 90, 95, 145
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    plot_left = left
    plot_right = width - right
    plot_top = top
    plot_bottom = height - bottom
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top

    all_y = []
    for item in series:
        all_y.extend(item["y"])
    xmin, xmax = nice_limits(x_values)
    ymin, ymax = nice_limits(all_y)

    def sx(x):
        return plot_left + (x - xmin) / (xmax - xmin) * plot_width

    def sy(y):
        return plot_bottom - (y - ymin) / (ymax - ymin) * plot_height

    axis_color = (40, 40, 40)
    grid_color = (220, 220, 220)
    draw.rectangle([plot_left, plot_top, plot_right, plot_bottom], outline=axis_color, width=2)

    for i in range(6):
        tx = plot_left + i * plot_width / 5.0
        ty = plot_top + i * plot_height / 5.0
        draw.line([tx, plot_top, tx, plot_bottom], fill=grid_color, width=1)
        draw.line([plot_left, ty, plot_right, ty], fill=grid_color, width=1)
        x_label = "%.0f" % (xmin + i * (xmax - xmin) / 5.0)
        y_label = "%.3g" % (ymax - i * (ymax - ymin) / 5.0)
        draw.text((tx - 18, plot_bottom + 16), x_label, fill=axis_color, font=font)
        draw.text((plot_left - 92, ty - 7), y_label, fill=axis_color, font=font)

    colors = [(31, 119, 180), (214, 39, 40), (44, 160, 44)]
    marker_half = 6
    for index, item in enumerate(series):
        color = colors[index % len(colors)]
        points = [(sx(x), sy(y)) for x, y in zip(x_values, item["y"])]
        if len(points) > 1:
            draw.line(points, fill=color, width=4)
        for px, py in points:
            draw.ellipse(
                [px - marker_half, py - marker_half, px + marker_half, py + marker_half],
                fill=color,
                outline=color,
            )
        legend_x = plot_left + 30 + index * 280
        legend_y = plot_top + 25
        draw.line([legend_x, legend_y + 8, legend_x + 45, legend_y + 8], fill=color, width=4)
        draw.ellipse([legend_x + 16, legend_y + 2, legend_x + 28, legend_y + 14], fill=color, outline=color)
        draw.text((legend_x + 58, legend_y), item["label"], fill=axis_color, font=font)

    draw.text((plot_left, 35), title, fill=axis_color, font=font)
    draw.text((plot_left + plot_width / 2 - 45, height - 70), xlabel, fill=axis_color, font=font)
    draw.text((25, plot_top + plot_height / 2), ylabel, fill=axis_color, font=font)
    image.save(path)

validated = [
    {
        "stage": "5B",
        "route": "10 -> 19 -> 20",
        "target_cycle": 20,
        "delta_n": 9,
        "skipped": 8,
        "statev1_error_percent": 0.049427,
        "s11_error_percent": 0.127013,
        "outcome": "clean_success",
    },
    {
        "stage": "6D",
        "route": "10 -> 29 -> 30",
        "target_cycle": 30,
        "delta_n": 19,
        "skipped": 18,
        "statev1_error_percent": 0.0458269,
        "s11_error_percent": 2.34366,
        "outcome": "accepted_exploratory_success",
    },
    {
        "stage": "7C",
        "route": "10 -> 27 -> 28",
        "target_cycle": 28,
        "delta_n": 17,
        "skipped": 16,
        "statev1_error_percent": 0.0231584782019,
        "s11_error_percent": 2.36494669088,
        "outcome": "accepted_exploratory_success",
    },
    {
        "stage": "9A",
        "route": "10 -> 39 -> 40",
        "target_cycle": 40,
        "delta_n": 29,
        "skipped": 28,
        "statev1_error_percent": 0.148910633675,
        "s11_error_percent": 2.23754024819,
        "outcome": "accepted_exploratory_success",
    },
    {
        "stage": "9B",
        "route": "10 -> 49 -> 50",
        "target_cycle": 50,
        "delta_n": 39,
        "skipped": 38,
        "statev1_error_percent": 0.253071065812,
        "s11_error_percent": 0.0522291978811,
        "outcome": "accepted_clean_success",
    },
]

with open(SUMMARY_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(validated[0].keys()))
    writer.writeheader()
    writer.writerows(validated)

cycles = [r["target_cycle"] for r in validated]
statev1 = [r["statev1_error_percent"] for r in validated]
s11 = [r["s11_error_percent"] for r in validated]

draw_plot(
    PLOT_ERR,
    cycles,
    [
        {"label": "STATEV1 error", "y": statev1},
        {"label": "S11 error", "y": s11},
    ],
    "Reference cycle",
    "Relative error (%)",
    "Validated predicted-FE cycle-jump error accumulation",
)

scan_rows = []
with open(SCAN_CSV, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        scan_rows.append(row)

scan_cycles = [int(r["target_cycle"]) for r in scan_rows]
pred_statev1 = [float(r["pred_STATEV1"]) for r in scan_rows]
pred_s11 = [float(r["pred_S11"]) for r in scan_rows]

draw_plot(
    PLOT_SCAN.replace(".png", "_statev1.png"),
    scan_cycles,
    [{"label": "Predicted STATEV1", "y": pred_statev1}],
    "Target cycle",
    "Predicted STATEV1",
    "Long-horizon predicted accumulated viscoplastic strain",
)

draw_plot(
    PLOT_SCAN.replace(".png", "_s11.png"),
    scan_cycles,
    [{"label": "Predicted S11", "y": pred_s11}],
    "Target cycle",
    "Predicted S11 (MPa)",
    "Long-horizon predicted S11",
)

print("Wrote:", SUMMARY_CSV)
print("Wrote:", PLOT_ERR)
print("Wrote:", PLOT_SCAN.replace(".png", "_statev1.png"))
print("Wrote:", PLOT_SCAN.replace(".png", "_s11.png"))
