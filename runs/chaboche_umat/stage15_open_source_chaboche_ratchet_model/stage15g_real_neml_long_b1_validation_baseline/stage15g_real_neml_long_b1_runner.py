#!/usr/bin/env python3
"""Run the Stage 15G long real-NEML B1 validation baseline."""

from __future__ import print_function

import argparse
import csv
import json
import math
import os
import shlex
import sys
import time
from pathlib import Path

try:
    import numpy as np
    import neml
    from neml import drivers, elasticity, hardening, models, ri_flow, surfaces
except ImportError:
    if os.environ.get("STAGE15G_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15G_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise

from stage15g_checkpoint_utils import atomic_write_json, checkpoint_payload, read_json


P2 = {
    "name": "P2_three_backstress_screen",
    "E": 200000.0,
    "nu": 0.3,
    "yield_stress": 100.0,
    "Q": 50.0,
    "b": 5.0,
    "C": [80000.0, 14000.0, 3333.0],
    "gamma": [900.0, 1500.0, 1.0],
    "A": [0.0, 0.0, 0.0],
    "a": [1.0, 1.0, 1.0],
}

CASE_NAME = "B1_stress_m150_to_250"
STRESS_MIN = -150.0
STRESS_MAX = 250.0
POINTS_PER_CYCLE = 40
PRESERVE_CYCLES = set([1000, 5000, 10000, 15000, 50000, 100000, 106250, 200000, 250000, 279725, 300000, 500000, 750000, 1000000, 1250000, 1500000, 1750000, 2000000])
SELECTED_LOOP_CYCLES = set([1, 2, 5, 10, 20, 50, 100, 500, 1000, 5000, 10000, 15000, 50000, 100000, 106250, 200000, 250000, 279725, 300000, 500000, 750000, 1000000, 1250000, 1500000, 1750000, 2000000])
SUMMARY_FIELDS = [
    "case_name", "cycle", "stress_min", "stress_max", "strain_min", "strain_max",
    "strain_mean", "strain_range", "ratcheting_strain", "hysteresis_area",
    "accumulated_inelastic_strain_end", "backstress_norm_end",
    "points_per_cycle", "walltime_seconds", "cycles_per_hour",
]
LOOP_FIELDS = ["case_name", "cycle", "step_in_cycle", "stress", "strain"]


def build_model():
    elastic = elasticity.IsotropicLinearElasticModel(P2["E"], "youngs", P2["nu"], "poissons")
    surface = surfaces.IsoKinJ2()
    iso = hardening.VoceIsotropicHardeningRule(P2["yield_stress"], P2["Q"], P2["b"])
    gmodels = [hardening.ConstantGamma(g) for g in P2["gamma"]]
    hmodel = hardening.Chaboche(iso, P2["C"], gmodels, P2["A"], P2["a"])
    flow = ri_flow.RateIndependentNonAssociativeHardening(surface, hmodel)
    return models.SmallStrainRateIndependentPlasticity(elastic, flow)


def internal_names(model):
    try:
        return list(model.report_internal_variable_names())
    except Exception:
        return []


def history_metrics(history, names):
    values = {}
    for i, name in enumerate(names):
        if i < len(history):
            values[name] = float(history[i])
    alpha = values.get("alpha", float("nan"))
    backstress = [v for k, v in values.items() if k.startswith("backstress_")]
    norm = math.sqrt(sum(v * v for v in backstress)) if backstress else float("nan")
    return alpha, norm


def trapz(xs, ys):
    area = 0.0
    for i in range(1, len(xs)):
        area += 0.5 * (ys[i] + ys[i - 1]) * (xs[i] - xs[i - 1])
    return area


def should_write_summary(cycle, final_cycle=False):
    return final_cycle or cycle <= 10000 or cycle % 100 == 0 or cycle in PRESERVE_CYCLES or cycle % 1000 == 0


def ensure_header(path, fields):
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as handle:
            csv.DictWriter(handle, fieldnames=fields).writeheader()


def append_csv(path, fields, row):
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writerow(row)
        handle.flush()


def write_status(path, case_name, cycle, target_cycle, elapsed, status, last_checkpoint_cycle):
    cph = cycle / max(elapsed, 1.0e-9) * 3600.0
    estimated_final = int(cycle + cph * max(0.0, (23 * 3600 + 35 * 60 - elapsed)) / 3600.0)
    mem = "unknown"
    try:
        import resource
        mem = str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) + "kb"
    except Exception:
        pass
    with path.open("w") as handle:
        handle.write("case_name=%s\n" % case_name)
        handle.write("cycle=%d\n" % cycle)
        handle.write("target_cycle=%d\n" % target_cycle)
        handle.write("elapsed_seconds=%.3f\n" % elapsed)
        handle.write("cycles_per_hour=%.6f\n" % cph)
        handle.write("estimated_final_cycle_at_stop_guard=%d\n" % estimated_final)
        handle.write("current_memory=%s\n" % mem)
        handle.write("status=%s\n" % status)
        handle.write("last_checkpoint_cycle=%d\n" % last_checkpoint_cycle)


def restore_driver_state(driver, checkpoint):
    state = checkpoint.get("driver_state", {})
    for attr, key in [("stress_int", "stress"), ("strain_int", "strain"), ("stored_int", "history")]:
        values = state.get(key)
        if values is not None:
            setattr(driver, attr, [np.array(values, dtype=float)])


def initialize_driver(args, checkpoint=None):
    model = build_model()
    names = internal_names(model)
    driver = drivers.Driver_sd(model, T_init=args.temperature)
    sdir = np.array([1.0, 0, 0, 0, 0, 0])
    half_steps = max(2, args.points_per_cycle // 2)
    if checkpoint:
        restore_driver_state(driver, checkpoint)
        return model, names, driver, sdir, half_steps
    ramp_inc = args.stress_max / float(half_steps)
    for _ in range(half_steps):
        driver.srate_sinc_step(sdir, args.srate, ramp_inc, args.temperature)
    return model, names, driver, sdir, half_steps


def write_summary(stage_dir, cycle, target_cycle, status, elapsed, last_row, metadata):
    lines = [
        "# Stage 15G Real NEML Long B1 Validation Baseline Summary",
        "",
        "Real NEML `P2_three_backstress_screen` B1-only long baseline.",
        "",
        "| Field | Value |",
        "|---|---:|",
        "| Final completed cycle | %d |" % cycle,
        "| Target cycle | %d |" % target_cycle,
        "| Status | %s |" % status,
        "| Elapsed seconds | %.3f |" % elapsed,
        "| Cycles/hour | %.6f |" % (cycle / max(elapsed, 1.0e-9) * 3600.0),
    ]
    if last_row:
        lines.extend([
            "| Final mean strain | %s |" % last_row.get("strain_mean", ""),
            "| Final ratcheting strain | %s |" % last_row.get("ratcheting_strain", ""),
        ])
    (stage_dir / "STAGE15G_MASTER_SUMMARY.md").write_text("\n".join(lines) + "\n")
    with (stage_dir / "STAGE15G_RUN_METADATA.json").open("w") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run(args):
    stage_dir = Path(__file__).resolve().parent
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "B1_long_cycle_summary.csv"
    loops_path = output_dir / "B1_long_selected_loops.csv"
    checkpoint_path = output_dir / "B1_long_checkpoint.json"
    status_path = output_dir / "B1_long_status.txt"
    ensure_header(summary_path, SUMMARY_FIELDS)
    ensure_header(loops_path, LOOP_FIELDS)

    checkpoint = None
    resume_cycle = 0
    first_mean = None
    if args.resume and checkpoint_path.exists():
        checkpoint = read_json(str(checkpoint_path))
        resume_cycle = int(checkpoint.get("cycle", 0))
        first_mean = checkpoint.get("first_mean")

    _, names, driver, sdir, half_steps = initialize_driver(args, checkpoint)
    start = time.time()
    cycle = resume_cycle
    last_checkpoint_cycle = resume_cycle if resume_cycle else 0
    last_status_time = 0.0
    status = "running"
    last_row = checkpoint.get("last_row") if checkpoint else None

    while cycle < args.target_cycles:
        elapsed = time.time() - start
        if elapsed >= args.stop_after_seconds:
            status = "stopped_by_time_guard"
            break
        cycle += 1
        strains = []
        stresses = []
        for inc in [
            (args.stress_min - args.stress_max) / float(half_steps),
            (args.stress_max - args.stress_min) / float(half_steps),
        ]:
            for _ in range(half_steps):
                driver.srate_sinc_step(sdir, args.srate, inc, args.temperature)
                stresses.append(float(np.dot(driver.stress_int[-1], sdir)))
                strains.append(float(np.dot(driver.strain_int[-1], sdir)))

        strain_min = min(strains)
        strain_max = max(strains)
        strain_mean = 0.5 * (strain_min + strain_max)
        if first_mean is None:
            first_mean = strain_mean
        alpha, backstress_norm = history_metrics(driver.stored_int[-1], names)
        elapsed = time.time() - start
        last_row = {
            "case_name": CASE_NAME,
            "cycle": cycle,
            "stress_min": min(stresses),
            "stress_max": max(stresses),
            "strain_min": strain_min,
            "strain_max": strain_max,
            "strain_mean": strain_mean,
            "strain_range": strain_max - strain_min,
            "ratcheting_strain": strain_mean - first_mean,
            "hysteresis_area": trapz(strains, stresses),
            "accumulated_inelastic_strain_end": alpha,
            "backstress_norm_end": backstress_norm,
            "points_per_cycle": args.points_per_cycle,
            "walltime_seconds": elapsed,
            "cycles_per_hour": (cycle - resume_cycle) / max(elapsed, 1.0e-9) * 3600.0,
        }
        if should_write_summary(cycle):
            append_csv(summary_path, SUMMARY_FIELDS, last_row)
        if cycle in SELECTED_LOOP_CYCLES:
            for i, pair in enumerate(zip(strains, stresses), 1):
                eps, sig = pair
                append_csv(loops_path, LOOP_FIELDS, {
                    "case_name": CASE_NAME,
                    "cycle": cycle,
                    "step_in_cycle": i,
                    "stress": sig,
                    "strain": eps,
                })
        if cycle % args.checkpoint_every == 0:
            atomic_write_json(str(checkpoint_path), checkpoint_payload(CASE_NAME, cycle, args.target_cycles, driver, elapsed, first_mean, last_row, status))
            last_checkpoint_cycle = cycle
        if elapsed - last_status_time >= args.status_every_seconds:
            write_status(status_path, CASE_NAME, cycle, args.target_cycles, elapsed, status, last_checkpoint_cycle)
            last_status_time = elapsed

    if cycle >= args.target_cycles:
        status = "completed"
    elapsed = time.time() - start
    if last_row:
        if not should_write_summary(cycle, final_cycle=True):
            append_csv(summary_path, SUMMARY_FIELDS, last_row)
        atomic_write_json(str(checkpoint_path), checkpoint_payload(CASE_NAME, cycle, args.target_cycles, driver, elapsed, first_mean, last_row, status))
        last_checkpoint_cycle = cycle
    write_status(status_path, CASE_NAME, cycle, args.target_cycles, elapsed, status, last_checkpoint_cycle)
    metadata = {
        "backend": "real_neml",
        "neml_path": neml.__file__,
        "model": P2,
        "case_name": CASE_NAME,
        "stress_min": args.stress_min,
        "stress_max": args.stress_max,
        "target_cycles": args.target_cycles,
        "final_cycle": cycle,
        "status": status,
        "elapsed_seconds": elapsed,
        "points_per_cycle": args.points_per_cycle,
        "summary_path": str(summary_path),
        "selected_loops_path": str(loops_path),
        "checkpoint_path": str(checkpoint_path),
        "resume_used": bool(checkpoint),
    }
    write_summary(stage_dir, cycle, args.target_cycles, status, elapsed, last_row, metadata)
    print("Stage 15G %s: cycle=%d target=%d elapsed=%.3f" % (status, cycle, args.target_cycles, elapsed))
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-cycles", type=int, default=2000000)
    parser.add_argument("--stress-min", type=float, default=STRESS_MIN)
    parser.add_argument("--stress-max", type=float, default=STRESS_MAX)
    parser.add_argument("--points-per-cycle", type=int, default=POINTS_PER_CYCLE)
    parser.add_argument("--srate", type=float, default=1000.0)
    parser.add_argument("--temperature", type=float, default=300.0)
    parser.add_argument("--stop-after-seconds", type=float, default=23 * 3600 + 35 * 60)
    parser.add_argument("--status-every-seconds", type=float, default=60.0)
    parser.add_argument("--checkpoint-every", type=int, default=1000)
    parser.add_argument("--output-dir", default="case_outputs")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.points_per_cycle != 40:
        raise SystemExit("Stage 15G requires points_per_cycle=40")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())

