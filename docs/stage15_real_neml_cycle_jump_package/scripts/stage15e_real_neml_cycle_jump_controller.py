#!/usr/bin/env python3
"""Stage 15E prediction-only cycle-jump benchmark controller."""

import argparse
import csv
import math
import os
import shlex
import sys
import time
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    if os.environ.get("STAGE15E_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15E_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise

from stage15e_cycle_jump_methods import (
    BASE_CYCLES,
    BASELINE_FILES,
    METHODS,
    TARGET_CYCLES,
    VARIABLES,
    drift_direction_ok,
    error_metrics,
    estimate_prediction,
    load_cycle_summary,
    row_at_cycle,
)


HERE = Path(__file__).resolve().parent
BASELINE_DIR = HERE.parent / "stage15d_real_neml_full_baseline" / "case_outputs"
DEFAULT_STOP_SECONDS = 23 * 3600 + 35 * 60

MATRIX_FIELDS = [
    "case_name",
    "base_cycle",
    "target_cycle",
    "method",
    "variable",
    "effective_window",
    "slope",
    "base_value",
    "predicted_value",
    "reference_value",
    "strain_range_reference",
    "absolute_error",
    "relative_error_percent",
    "normalized_error_percent",
    "drift_direction_ok",
    "finite",
    "status",
]

ACCEPTANCE_FIELDS = [
    "case_name",
    "base_cycle",
    "target_cycle",
    "method",
    "mean_normalized_error_percent",
    "ratcheting_normalized_error_percent",
    "peak_normalized_error_percent",
    "strict_1pct_accept",
    "relaxed_2pct_accept",
    "relaxed_5pct_accept",
    "drift_direction_ok",
    "finite",
]


def parse_ints(value, default):
    if not value:
        return list(default)
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def parse_strings(value, default):
    if not value:
        return list(default)
    return [part.strip() for part in value.split(",") if part.strip()]


def open_writer(path, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    handle = path.open("a", newline="")
    writer = csv.DictWriter(handle, fieldnames=fields)
    if not exists:
        writer.writeheader()
        handle.flush()
    return handle, writer


def finite_row(values):
    return all(math.isfinite(float(value)) for value in values)


def write_status(output_dir, message):
    status = output_dir / "STAGE15E_STATUS.txt"
    status.write_text(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{message}\n")


def write_checkpoint(output_dir, row_count, lane):
    checkpoint = output_dir / "STAGE15E_CHECKPOINT.txt"
    checkpoint.write_text(
        "\n".join(
            [
                f"time={time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"rows={row_count}",
                f"last_lane={lane}",
                "",
            ]
        )
    )


def aggregate_acceptance(matrix_path, acceptance_path, best_path, errors_path):
    matrix = pd.read_csv(matrix_path)
    matrix.to_csv(errors_path, index=False)

    rows = []
    grouped = matrix.groupby(["case_name", "base_cycle", "target_cycle", "method"], sort=True)
    for key, group in grouped:
        case_name, base_cycle, target_cycle, method = key
        by_var = {row["variable"]: row for _, row in group.iterrows()}
        mean_error = float(by_var["strain_mean"]["normalized_error_percent"]) if "strain_mean" in by_var else float("nan")
        ratchet_error = float(by_var["ratcheting_strain"]["normalized_error_percent"]) if "ratcheting_strain" in by_var else float("nan")
        peak_errors = []
        for variable in ("strain_max", "strain_min"):
            if variable in by_var:
                peak_errors.append(float(by_var[variable]["normalized_error_percent"]))
        peak_error = max(peak_errors) if peak_errors else float("nan")
        drift_ok = bool(group["drift_direction_ok"].astype(bool).all())
        finite = bool(group["finite"].astype(bool).all())
        strict = finite and drift_ok and mean_error <= 1.0 and ratchet_error <= 1.0 and (math.isnan(peak_error) or peak_error <= 1.0)
        relaxed_2 = finite and drift_ok and mean_error <= 2.0 and ratchet_error <= 2.0 and (math.isnan(peak_error) or peak_error <= 2.0)
        relaxed_5 = finite and drift_ok and mean_error <= 5.0 and ratchet_error <= 5.0 and (math.isnan(peak_error) or peak_error <= 5.0)
        rows.append(
            {
                "case_name": case_name,
                "base_cycle": int(base_cycle),
                "target_cycle": int(target_cycle),
                "method": method,
                "mean_normalized_error_percent": mean_error,
                "ratcheting_normalized_error_percent": ratchet_error,
                "peak_normalized_error_percent": peak_error,
                "strict_1pct_accept": strict,
                "relaxed_2pct_accept": relaxed_2,
                "relaxed_5pct_accept": relaxed_5,
                "drift_direction_ok": drift_ok,
                "finite": finite,
            }
        )
    acceptance = pd.DataFrame(rows)
    acceptance.to_csv(acceptance_path, index=False)

    if acceptance.empty:
        acceptance.to_csv(best_path, index=False)
        return acceptance

    scoring = acceptance.copy()
    scoring["score"] = scoring["mean_normalized_error_percent"] + scoring["ratcheting_normalized_error_percent"]
    scoring = scoring.sort_values(["case_name", "target_cycle", "score", "base_cycle", "method"])
    best = scoring.groupby(["case_name", "target_cycle"], as_index=False).first()
    best.drop(columns=["score"]).to_csv(best_path, index=False)
    return acceptance


def simple_svg(path, title, points, x_label, y_label):
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 920, 520
    margin = 70
    if not points:
        points = [(0.0, 0.0)]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax = xmin + 1.0
    if ymin == ymax:
        ymax = ymin + 1.0

    def sx(x):
        return margin + (x - xmin) / (xmax - xmin) * (width - 2 * margin)

    def sy(y):
        return height - margin - (y - ymin) / (ymax - ymin) * (height - 2 * margin)

    polyline = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in sorted(points))
    circles = "\n".join(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="3" fill="#1f6f8b" />' for x, y in points)
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="{width / 2}" y="32" text-anchor="middle" font-family="Arial" font-size="20">{title}</text>
<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#333"/>
<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#333"/>
<text x="{width / 2}" y="{height - 18}" text-anchor="middle" font-family="Arial" font-size="14">{x_label}</text>
<text x="18" y="{height / 2}" transform="rotate(-90 18,{height / 2})" text-anchor="middle" font-family="Arial" font-size="14">{y_label}</text>
<polyline points="{polyline}" fill="none" stroke="#1f6f8b" stroke-width="2"/>
{circles}
</svg>
"""
    )


def generate_plots(output_dir):
    matrix_path = output_dir / "STAGE15E_CYCLE_JUMP_MATRIX.csv"
    if not matrix_path.exists():
        return
    matrix = pd.read_csv(matrix_path)
    plots_dir = output_dir / "plots"
    for case_name, prefix in (("B1_stress_m150_to_250", "B1"), ("B2_stress_0_to_300", "B2")):
        case = matrix.loc[matrix["case_name"] == case_name]
        primary = case.loc[case["variable"].isin(["strain_mean", "ratcheting_strain"])]
        error_points = (
            primary.groupby("target_cycle")["normalized_error_percent"].min().reset_index().itertuples(index=False, name=None)
        )
        simple_svg(plots_dir / f"{prefix}_error_vs_target.svg", f"{prefix} best normalized error vs target", list(error_points), "target cycle", "normalized error percent")
        for variable, suffix in (("strain_mean", "mean_strain"), ("ratcheting_strain", "ratcheting")):
            var_rows = case.loc[case["variable"] == variable].copy()
            if var_rows.empty:
                points = []
            else:
                var_rows["combo_error"] = var_rows["normalized_error_percent"]
                best = var_rows.sort_values(["target_cycle", "combo_error"]).groupby("target_cycle").first().reset_index()
                points = list(best[["target_cycle", "predicted_value"]].itertuples(index=False, name=None))
            simple_svg(plots_dir / f"{prefix}_{suffix}_prediction.svg", f"{prefix} {variable} best prediction", points, "target cycle", variable)

    acceptance_path = output_dir / "STAGE15E_ACCEPTANCE_TABLE.csv"
    if acceptance_path.exists():
        acceptance = pd.read_csv(acceptance_path)
        acceptance["score"] = acceptance["mean_normalized_error_percent"] + acceptance["ratcheting_normalized_error_percent"]
        heat = acceptance.groupby("method")["score"].median().reset_index()
        points = [(idx + 1, float(row["score"])) for idx, row in heat.iterrows()]
        simple_svg(plots_dir / "method_comparison_heatmap.svg", "Method comparison median primary error", points, "method index", "median normalized error score")


def write_summary(output_dir, acceptance, incomplete):
    lines = [
        "# Stage 15E Real NEML Cycle-Jump Benchmark Summary",
        "",
        "Prediction-only cycle-jump benchmark against the Stage 15D walltime-limited baseline.",
        "",
        f"Run status: {'incomplete by stop guard' if incomplete else 'complete'}",
        "",
        "## Acceptance Counts",
        "",
        "| Case | Strict <=1% | Relaxed <=2% | Relaxed <=5% | Total lanes |",
        "|---|---:|---:|---:|---:|",
    ]
    if not acceptance.empty:
        for case_name, group in acceptance.groupby("case_name"):
            lines.append(
                "| {case} | {strict} | {relaxed2} | {relaxed5} | {total} |".format(
                    case=case_name,
                    strict=int(group["strict_1pct_accept"].sum()),
                    relaxed2=int(group["relaxed_2pct_accept"].sum()),
                    relaxed5=int(group["relaxed_5pct_accept"].sum()),
                    total=len(group),
                )
            )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- STAGE15E_CYCLE_JUMP_MATRIX.csv",
            "- STAGE15E_CYCLE_JUMP_ERRORS.csv",
            "- STAGE15E_ACCEPTANCE_TABLE.csv",
            "- STAGE15E_BEST_METHODS_BY_TARGET.csv",
            "- plots/*.svg",
            "",
        ]
    )
    (output_dir / "STAGE15E_MASTER_SUMMARY.md").write_text("\n".join(lines))


def run(args):
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_status(output_dir, "starting")

    cases = parse_strings(args.cases, list(BASELINE_FILES.keys()))
    methods = parse_strings(args.methods, METHODS)
    variables = parse_strings(args.variables, VARIABLES)
    base_cycles = parse_ints(args.base_cycles, BASE_CYCLES)

    matrix_path = output_dir / "STAGE15E_CYCLE_JUMP_MATRIX.csv"
    acceptance_path = output_dir / "STAGE15E_ACCEPTANCE_TABLE.csv"
    best_path = output_dir / "STAGE15E_BEST_METHODS_BY_TARGET.csv"
    errors_path = output_dir / "STAGE15E_CYCLE_JUMP_ERRORS.csv"
    if not args.resume:
        for path in (matrix_path, acceptance_path, best_path, errors_path):
            if path.exists():
                path.unlink()

    handle, writer = open_writer(matrix_path, MATRIX_FIELDS)
    start = time.time()
    row_count = 0
    incomplete = False

    try:
        for case_name in cases:
            df = load_cycle_summary(str(BASELINE_DIR / BASELINE_FILES[case_name]))
            max_cycle = int(df["cycle"].max())
            targets = parse_ints(args.target_cycles, TARGET_CYCLES[case_name])
            for base_cycle in base_cycles:
                if base_cycle > max_cycle:
                    continue
                for target_cycle in targets:
                    if target_cycle <= base_cycle or target_cycle > max_cycle:
                        continue
                    reference_row = row_at_cycle(df, target_cycle)
                    strain_range_reference = float(reference_row["strain_range"])
                    for method in methods:
                        for variable in variables:
                            if time.time() - start > args.stop_after_seconds:
                                incomplete = True
                                raise TimeoutError("stop guard reached")
                            try:
                                prediction = estimate_prediction(df, variable, method, base_cycle, target_cycle)
                                reference_value = float(reference_row[variable])
                                errors = error_metrics(prediction.predicted_value, reference_value, strain_range_reference)
                                drift_ok = drift_direction_ok(prediction.base_value, prediction.predicted_value, reference_value)
                                finite = finite_row(
                                    [
                                        prediction.slope,
                                        prediction.base_value,
                                        prediction.predicted_value,
                                        reference_value,
                                        errors["absolute_error"],
                                        errors["relative_error_percent"],
                                        errors["normalized_error_percent"],
                                    ]
                                )
                                status = "ok"
                            except Exception as exc:
                                prediction = None
                                reference_value = float("nan")
                                errors = {
                                    "absolute_error": float("nan"),
                                    "relative_error_percent": float("nan"),
                                    "normalized_error_percent": float("nan"),
                                }
                                drift_ok = False
                                finite = False
                                status = f"error: {exc}"
                            row = {
                                "case_name": case_name,
                                "base_cycle": base_cycle,
                                "target_cycle": target_cycle,
                                "method": method,
                                "variable": variable,
                                "effective_window": prediction.effective_window if prediction else "",
                                "slope": prediction.slope if prediction else "",
                                "base_value": prediction.base_value if prediction else "",
                                "predicted_value": prediction.predicted_value if prediction else "",
                                "reference_value": reference_value,
                                "strain_range_reference": strain_range_reference,
                                "absolute_error": errors["absolute_error"],
                                "relative_error_percent": errors["relative_error_percent"],
                                "normalized_error_percent": errors["normalized_error_percent"],
                                "drift_direction_ok": drift_ok,
                                "finite": finite,
                                "status": status,
                            }
                            writer.writerow(row)
                            handle.flush()
                            row_count += 1
                    lane = f"{case_name} base={base_cycle} target={target_cycle} method={method}"
                    write_checkpoint(output_dir, row_count, lane)
                    write_status(output_dir, f"running\nrows={row_count}\nlast_lane={lane}")
    except TimeoutError:
        write_status(output_dir, f"stop guard reached\nrows={row_count}")
    finally:
        handle.close()

    acceptance = aggregate_acceptance(matrix_path, acceptance_path, best_path, errors_path)
    generate_plots(output_dir)
    write_summary(output_dir, acceptance, incomplete)
    write_status(output_dir, f"{'incomplete' if incomplete else 'complete'}\nrows={row_count}")
    return 0 if row_count > 0 else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--cases", help="Comma-separated case names")
    parser.add_argument("--base-cycles", help="Comma-separated base cycles")
    parser.add_argument("--target-cycles", help="Comma-separated target cycles")
    parser.add_argument("--methods", help="Comma-separated method names")
    parser.add_argument("--variables", help="Comma-separated variable names")
    parser.add_argument("--stop-after-seconds", type=int, default=int(os.environ.get("STAGE15E_STOP_SECONDS", DEFAULT_STOP_SECONDS)))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
