#!/usr/bin/env python3
"""Stage 15F adaptive real NEML cycle-jump refinement from B1 reference data."""

import csv
import math
import os
import shlex
import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ImportError:
    if os.environ.get("STAGE15F_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15F_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PACKAGE = REPO / "docs" / "stage15_real_neml_cycle_jump_package"
B1_PATH = PACKAGE / "baseline" / "B1_stress_m150_to_250_cycle_summary.csv"
CASE_NAME = "B1_stress_m150_to_250"
ROUTES = [(500, 1000), (1000, 5000), (5000, 10000), (10000, 50000), (50000, 100000), (100000, 200000)]
VARIABLES = ["strain_mean", "ratcheting_strain", "strain_max"]
METHODS = [
    "local_linear",
    "least_squares_local_linear",
    "power_law_fit",
    "log_cycle_fit",
    "quadratic_curvature_limited",
]
TINY = 1.0e-12


def load_reference():
    if not B1_PATH.exists():
        raise SystemExit("Missing B1 reference: %s" % B1_PATH)
    df = pd.read_csv(B1_PATH)
    required = ["cycle", "strain_mean", "ratcheting_strain", "strain_max", "strain_range"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise SystemExit("B1 reference missing columns: %s" % missing)
    for column in required:
        df[column] = pd.to_numeric(df[column], errors="raise")
    if not np.isfinite(df[required].to_numpy(dtype=float)).all():
        raise SystemExit("B1 reference contains NaN/inf in required columns")
    return df.sort_values("cycle").reset_index(drop=True)


def row_at(df, cycle):
    rows = df.loc[df["cycle"] == int(cycle)]
    if rows.empty:
        raise KeyError("cycle %s not found" % cycle)
    return rows.iloc[0]


def fit_window(df, base_cycle, max_points):
    sample = df.loc[df["cycle"] <= int(base_cycle)].tail(int(max_points))
    if len(sample) < 3:
        raise ValueError("need at least three cycles before base %s" % base_cycle)
    return sample


def local_linear(sample, variable, base_cycle, target_cycle):
    use = sample.tail(min(20, len(sample)))
    x = use["cycle"].to_numpy(dtype=float)
    y = use[variable].to_numpy(dtype=float)
    slope = (y[-1] - y[0]) / max(x[-1] - x[0], TINY)
    base = float(y[-1])
    return base + slope * (target_cycle - base_cycle)


def least_squares_local_linear(sample, variable, base_cycle, target_cycle):
    use = sample.tail(min(100, len(sample)))
    x = use["cycle"].to_numpy(dtype=float)
    y = use[variable].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    base = float(row_at(sample, base_cycle)[variable]) if (sample["cycle"] == base_cycle).any() else float(y[-1])
    fitted_base = slope * base_cycle + intercept
    return base + (slope * target_cycle + intercept - fitted_base)


def power_law_fit(sample, variable, base_cycle, target_cycle):
    use = sample.tail(min(200, len(sample)))
    x = use["cycle"].to_numpy(dtype=float)
    y = use[variable].to_numpy(dtype=float)
    base_value = float(use.iloc[-1][variable])
    shift = 0.0
    if y.min() <= 0:
        shift = abs(float(y.min())) + 1.0e-9
    logx = np.log(np.maximum(x, 1.0))
    logy = np.log(np.maximum(y + shift, TINY))
    exponent, loga = np.polyfit(logx, logy, 1)
    pred = math.exp(loga) * (target_cycle ** exponent) - shift
    base_fit = math.exp(loga) * (base_cycle ** exponent) - shift
    return base_value + (pred - base_fit)


def log_cycle_fit(sample, variable, base_cycle, target_cycle):
    use = sample.tail(min(200, len(sample)))
    x = np.log(np.maximum(use["cycle"].to_numpy(dtype=float), 1.0))
    y = use[variable].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    base_value = float(use.iloc[-1][variable])
    fitted_base = slope * math.log(max(base_cycle, 1.0)) + intercept
    fitted_target = slope * math.log(max(target_cycle, 1.0)) + intercept
    return base_value + (fitted_target - fitted_base)


def quadratic_curvature_limited(sample, variable, base_cycle, target_cycle):
    use = sample.tail(min(200, len(sample)))
    x = use["cycle"].to_numpy(dtype=float)
    y = use[variable].to_numpy(dtype=float)
    coeff = np.polyfit(x, y, 2)
    linear_slope = (y[-1] - y[0]) / max(x[-1] - x[0], TINY)
    curvature = coeff[0]
    max_curvature = abs(linear_slope) / max((x[-1] - x[0]) * 10.0, TINY)
    curvature = max(-max_curvature, min(max_curvature, curvature))
    slope = coeff[1]
    base_value = float(y[-1])
    delta = target_cycle - base_cycle
    return base_value + slope * delta + curvature * delta * delta


PREDICTORS = {
    "local_linear": local_linear,
    "least_squares_local_linear": least_squares_local_linear,
    "power_law_fit": power_law_fit,
    "log_cycle_fit": log_cycle_fit,
    "quadratic_curvature_limited": quadratic_curvature_limited,
}


def evaluate(df, base_cycle, target_cycle, method):
    sample = fit_window(df, base_cycle, 300)
    base = row_at(df, base_cycle)
    ref = row_at(df, target_cycle)
    strain_range_ref = max(abs(float(ref["strain_range"])), TINY)
    out = {
        "case_name": CASE_NAME,
        "base_cycle": base_cycle,
        "target_cycle": target_cycle,
        "jump_size": target_cycle - base_cycle,
        "method": method,
        "strain_range_reference": strain_range_ref,
    }
    errors = []
    drift_ok = True
    for variable in VARIABLES:
        pred = float(PREDICTORS[method](sample, variable, base_cycle, target_cycle))
        reference = float(ref[variable])
        base_value = float(base[variable])
        norm_error = 100.0 * abs(pred - reference) / strain_range_ref
        drift_pred = pred - base_value
        drift_ref = reference - base_value
        if abs(drift_ref) > TINY and drift_pred * drift_ref < 0:
            drift_ok = False
        out["predicted_" + variable] = pred
        out["reference_" + variable] = reference
        out[variable + "_normalized_error_percent"] = norm_error
        errors.append(norm_error)
    finite = np.isfinite(np.array([out[k] for k in out if isinstance(out[k], float)], dtype=float)).all()
    accepted = bool(finite and drift_ok and max(errors) <= 1.0)
    out["max_normalized_error_percent"] = max(errors)
    out["drift_direction_ok"] = drift_ok
    out["finite"] = bool(finite)
    out["accepted"] = accepted
    return out


def candidate_targets(base, target):
    candidates = []
    current = int(target)
    while current > base:
        candidates.append(current)
        current = base + max(1, (current - base) // 2)
        if candidates[-1] == current:
            break
    return sorted(set(candidates), reverse=True)


def write_csv(path, rows):
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def svg_line(path, title, points, xlabel, ylabel):
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height, margin = 920, 520, 70
    if not points:
        points = [(0.0, 0.0)]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax += 1.0
    if ymin == ymax:
        ymax += 1.0

    def sx(x):
        return margin + (x - xmin) / (xmax - xmin) * (width - 2 * margin)

    def sy(y):
        return height - margin - (y - ymin) / (ymax - ymin) * (height - 2 * margin)

    poly = " ".join("%.2f,%.2f" % (sx(x), sy(y)) for x, y in sorted(points))
    dots = "\n".join('<circle cx="%.2f" cy="%.2f" r="4" fill="#1f6f8b"/>' % (sx(x), sy(y)) for x, y in points)
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n'
        '<rect width="100%%" height="100%%" fill="white"/>\n'
        '<text x="%d" y="32" text-anchor="middle" font-family="Arial" font-size="20">%s</text>\n'
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333"/>\n'
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333"/>\n'
        '<text x="%d" y="%d" text-anchor="middle" font-family="Arial" font-size="14">%s</text>\n'
        '<text x="18" y="%d" transform="rotate(-90 18,%d)" text-anchor="middle" font-family="Arial" font-size="14">%s</text>\n'
        '<polyline points="%s" fill="none" stroke="#1f6f8b" stroke-width="2"/>\n%s\n</svg>\n'
        % (
            width,
            height,
            width,
            height,
            width // 2,
            title,
            margin,
            height - margin,
            width - margin,
            height - margin,
            margin,
            margin,
            margin,
            height - margin,
            width // 2,
            height - 18,
            xlabel,
            height // 2,
            height // 2,
            ylabel,
            poly,
            dots,
        )
    )


def main():
    df = load_reference()
    routes = []
    accepted_summary = []
    for base, target in ROUTES:
        route_rows = []
        for method in METHODS:
            for candidate in candidate_targets(base, target):
                row = evaluate(df, base, candidate, method)
                row["requested_target_cycle"] = target
                row["adaptive_candidate"] = candidate != target
                routes.append(row)
                route_rows.append(row)
        accepted = [row for row in route_rows if row["accepted"]]
        if accepted:
            accepted.sort(key=lambda row: (-row["target_cycle"], row["max_normalized_error_percent"], row["method"]))
            choice = accepted[0]
            status = "accepted"
        else:
            route_rows.sort(key=lambda row: (row["max_normalized_error_percent"], -row["target_cycle"], row["method"]))
            choice = route_rows[0]
            status = "rejected_min_error"
        accepted_summary.append(
            {
                "case_name": CASE_NAME,
                "base_cycle": base,
                "requested_target_cycle": target,
                "chosen_target_cycle": choice["target_cycle"],
                "chosen_jump_size": choice["target_cycle"] - base,
                "method": choice["method"],
                "max_normalized_error_percent": choice["max_normalized_error_percent"],
                "accepted": choice["accepted"],
                "adaptive_status": status,
            }
        )

    write_csv(HERE / "STAGE15F_ADAPTIVE_JUMP_ROUTES.csv", routes)
    write_csv(HERE / "STAGE15F_ADAPTIVE_JUMP_ERRORS.csv", routes)
    write_csv(HERE / "STAGE15F_ACCEPTED_ROUTE_SUMMARY.csv", accepted_summary)

    plots = HERE / "plots"
    svg_line(
        plots / "B1_adaptive_route_prediction.svg",
        "B1 adaptive chosen ratcheting prediction",
        [(row["chosen_target_cycle"], row["max_normalized_error_percent"]) for row in accepted_summary],
        "chosen target cycle",
        "max normalized error percent",
    )
    svg_line(
        plots / "B1_error_vs_jump_size.svg",
        "B1 error vs jump size",
        [(row["jump_size"], row["max_normalized_error_percent"]) for row in routes],
        "jump size",
        "max normalized error percent",
    )
    svg_line(
        plots / "B1_accepted_jump_map.svg",
        "B1 accepted jump map",
        [(row["chosen_jump_size"], 1.0 if row["accepted"] else 0.0) for row in accepted_summary],
        "chosen jump size",
        "accepted",
    )

    accepted_count = sum(1 for row in accepted_summary if row["accepted"])
    lines = [
        "# Stage 15F Adaptive Real NEML Cycle-Jump Summary",
        "",
        "Reference-data-based adaptive refinement using Stage 15D B1 cycle summary.",
        "",
        "No long NEML simulations were run.",
        "",
        "## Route Summary",
        "",
        "| Base | Requested target | Chosen target | Method | Max normalized error % | Accepted |",
        "|---:|---:|---:|---|---:|---|",
    ]
    for row in accepted_summary:
        lines.append(
            "| {base_cycle} | {requested_target_cycle} | {chosen_target_cycle} | {method} | {max_normalized_error_percent:.6g} | {accepted} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Totals",
            "",
            "- Requested routes: %d" % len(ROUTES),
            "- Accepted adaptive routes: %d" % accepted_count,
            "- Output rows: %d" % len(routes),
            "",
        ]
    )
    (HERE / "STAGE15F_MASTER_SUMMARY.md").write_text("\n".join(lines))
    print("Stage 15F complete: %d rows, %d accepted routes" % (len(routes), accepted_count))
    return 0 if routes and accepted_summary else 1


if __name__ == "__main__":
    raise SystemExit(main())

