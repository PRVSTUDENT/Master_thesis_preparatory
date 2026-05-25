#!/usr/bin/env python3
"""Run Stage 15I multi-case real-NEML long validation sweep."""

from __future__ import print_function

import argparse
import csv
import json
import math
import os
import shlex
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, TimeoutError, as_completed
from pathlib import Path

try:
    import numpy as np
    import neml
    from neml import drivers, elasticity, hardening, models, ri_flow, surfaces
except ImportError:
    if os.environ.get("STAGE15I_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15I_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise

from stage15i_case_definitions import (
    CASES,
    DEFAULT_ACTIVE_WORKERS,
    EXTENSION_TARGET_CYCLES,
    P2_MODEL,
    POINTS_PER_CYCLE,
    PRESERVED_TARGET_CYCLES,
    PRIMARY_TARGET_CYCLES,
    SELECTED_LOOP_CYCLES,
    STOP_GUARD_SECONDS,
)
from stage15i_checkpoint_utils import atomic_write_json, checkpoint_payload, read_json

SUMMARY_FIELDS = [
    "case_name", "cycle", "stress_min", "stress_max", "strain_min", "strain_max",
    "strain_mean", "strain_range", "ratcheting_strain", "hysteresis_area",
    "accumulated_inelastic_strain_end", "backstress_norm_end",
    "points_per_cycle", "walltime_seconds", "cycles_per_hour", "backend",
]
LOOP_FIELDS = ["case_name", "cycle", "step_in_cycle", "stress", "strain"]


def build_model():
    elastic = elasticity.IsotropicLinearElasticModel(P2_MODEL["E"], "youngs", P2_MODEL["nu"], "poissons")
    surface = surfaces.IsoKinJ2()
    iso = hardening.VoceIsotropicHardeningRule(P2_MODEL["yield_stress"], P2_MODEL["Q"], P2_MODEL["b"])
    gmodels = [hardening.ConstantGamma(g) for g in P2_MODEL["gamma"]]
    hmodel = hardening.Chaboche(iso, P2_MODEL["C"], gmodels, P2_MODEL["A"], P2_MODEL["a"])
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
    return (
        final_cycle
        or cycle <= 10000
        or cycle % 100 == 0
        or cycle in set(PRESERVED_TARGET_CYCLES)
    )


def ensure_header(path, fields):
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as handle:
            csv.DictWriter(handle, fieldnames=fields).writeheader()


def append_csv(path, fields, row):
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writerow(row)
        handle.flush()


def current_memory():
    try:
        import resource
        return str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) + "kb"
    except Exception:
        return "unknown"


def write_status(path, case_name, cycle, target_cycle, elapsed, status, last_checkpoint_cycle, stop_at_epoch):
    cph = cycle / max(elapsed, 1.0e-9) * 3600.0
    remaining = max(0.0, stop_at_epoch - time.time())
    estimated_final = int(cycle + cph * remaining / 3600.0)
    with path.open("w") as handle:
        handle.write("case_name=%s\n" % case_name)
        handle.write("cycle=%d\n" % cycle)
        handle.write("target_cycle=%d\n" % target_cycle)
        handle.write("elapsed_seconds=%.3f\n" % elapsed)
        handle.write("cycles_per_hour=%.6f\n" % cph)
        handle.write("estimated_final_cycle_at_stop_guard=%d\n" % estimated_final)
        handle.write("current_memory=%s\n" % current_memory())
        handle.write("status=%s\n" % status)
        handle.write("last_checkpoint_cycle=%d\n" % last_checkpoint_cycle)


def restore_driver_state(driver, checkpoint):
    state = checkpoint.get("driver_state", {})
    for attr, key in [("stress_int", "stress"), ("strain_int", "strain"), ("stored_int", "history")]:
        values = state.get(key)
        if values is not None:
            setattr(driver, attr, [np.array(values, dtype=float)])


def initialize_driver(case, args, checkpoint=None):
    model = build_model()
    names = internal_names(model)
    driver = drivers.Driver_sd(model, T_init=args["temperature"])
    sdir = np.array([1.0, 0, 0, 0, 0, 0])
    half_steps = max(2, args["points_per_cycle"] // 2)
    if checkpoint:
        restore_driver_state(driver, checkpoint)
        return names, driver, sdir, half_steps
    ramp_inc = case["stress_max"] / float(half_steps)
    for _ in range(half_steps):
        driver.srate_sinc_step(sdir, args["srate"], ramp_inc, args["temperature"])
    return names, driver, sdir, half_steps


def run_case(case, args):
    case_name = case["case_name"]
    output_dir = Path(args["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / ("%s_cycle_summary.csv" % case_name)
    loops_path = output_dir / ("%s_selected_loops.csv" % case_name)
    checkpoint_path = output_dir / ("%s_checkpoint.json" % case_name)
    status_path = output_dir / ("%s_status.txt" % case_name)
    ensure_header(summary_path, SUMMARY_FIELDS)
    ensure_header(loops_path, LOOP_FIELDS)

    checkpoint = None
    resume_cycle = 0
    first_mean = None
    if args["resume"] and checkpoint_path.exists():
        checkpoint = read_json(str(checkpoint_path))
        resume_cycle = int(checkpoint.get("cycle", 0))
        first_mean = checkpoint.get("first_mean")

    names, driver, sdir, half_steps = initialize_driver(case, args, checkpoint)
    start = time.time()
    cycle = resume_cycle
    last_checkpoint_cycle = resume_cycle
    last_status_time = 0.0
    status = "running"
    last_row = checkpoint.get("last_row") if checkpoint else None
    stop_at_epoch = args["stop_at_epoch"]

    try:
        while cycle < args["target_cycles"]:
            if time.time() >= stop_at_epoch:
                status = "stopped_by_time_guard"
                break
            cycle += 1
            strains = []
            stresses = []
            for inc in [
                (case["stress_min"] - case["stress_max"]) / float(half_steps),
                (case["stress_max"] - case["stress_min"]) / float(half_steps),
            ]:
                for _ in range(half_steps):
                    driver.srate_sinc_step(sdir, args["srate"], inc, args["temperature"])
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
                "case_name": case_name,
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
                "points_per_cycle": args["points_per_cycle"],
                "walltime_seconds": elapsed,
                "cycles_per_hour": (cycle - resume_cycle) / max(elapsed, 1.0e-9) * 3600.0,
                "backend": "real_neml",
            }
            if should_write_summary(cycle):
                append_csv(summary_path, SUMMARY_FIELDS, last_row)
            if cycle in set(SELECTED_LOOP_CYCLES):
                for i, pair in enumerate(zip(strains, stresses), 1):
                    eps, sig = pair
                    append_csv(loops_path, LOOP_FIELDS, {
                        "case_name": case_name,
                        "cycle": cycle,
                        "step_in_cycle": i,
                        "stress": sig,
                        "strain": eps,
                    })
            if cycle % args["checkpoint_every"] == 0:
                atomic_write_json(str(checkpoint_path), checkpoint_payload(case_name, cycle, args["target_cycles"], driver, elapsed, first_mean, last_row, status))
                last_checkpoint_cycle = cycle
            if elapsed - last_status_time >= args["status_every_seconds"]:
                write_status(status_path, case_name, cycle, args["target_cycles"], elapsed, status, last_checkpoint_cycle, stop_at_epoch)
                last_status_time = elapsed

        if cycle >= args["target_cycles"]:
            status = "completed"
        elapsed = time.time() - start
        if last_row:
            if not should_write_summary(cycle, final_cycle=True):
                append_csv(summary_path, SUMMARY_FIELDS, last_row)
            atomic_write_json(str(checkpoint_path), checkpoint_payload(case_name, cycle, args["target_cycles"], driver, elapsed, first_mean, last_row, status))
            last_checkpoint_cycle = cycle
        write_status(status_path, case_name, cycle, args["target_cycles"], elapsed, status, last_checkpoint_cycle, stop_at_epoch)
        return {
            "case_name": case_name,
            "group": case["group"],
            "stress_min": case["stress_min"],
            "stress_max": case["stress_max"],
            "final_cycle": cycle,
            "target_cycle": args["target_cycles"],
            "status": status,
            "elapsed_seconds": elapsed,
            "cycles_per_hour": (cycle - resume_cycle) / max(elapsed, 1.0e-9) * 3600.0,
            "summary_path": str(summary_path),
            "selected_loops_path": str(loops_path),
            "checkpoint_path": str(checkpoint_path),
            "status_path": str(status_path),
        }
    except Exception as exc:
        elapsed = time.time() - start
        write_status(status_path, case_name, cycle, args["target_cycles"], elapsed, "failed", last_checkpoint_cycle, stop_at_epoch)
        return {
            "case_name": case_name,
            "group": case["group"],
            "stress_min": case["stress_min"],
            "stress_max": case["stress_max"],
            "final_cycle": cycle,
            "target_cycle": args["target_cycles"],
            "status": "failed",
            "elapsed_seconds": elapsed,
            "cycles_per_hour": 0.0,
            "error": "%s: %s" % (type(exc).__name__, exc),
            "traceback": traceback.format_exc(),
        }


def parse_status(path):
    values = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def write_global_status(stage_dir, output_dir, active_workers, total_cases, start_time, results=None):
    results = results or []
    status_files = sorted(Path(output_dir).glob("*_status.txt"))
    statuses = [parse_status(path) for path in status_files]
    completed = len([r for r in results if r.get("status") == "completed"])
    failed = len([r for r in results if r.get("status") == "failed"])
    running = len([s for s in statuses if s.get("status") == "running"])
    with (stage_dir / "STAGE15I_GLOBAL_STATUS.txt").open("w") as handle:
        handle.write("active_worker_count=%d\n" % active_workers)
        handle.write("completed_case_count=%d\n" % completed)
        handle.write("running_case_count=%d\n" % running)
        handle.write("failed_case_count=%d\n" % failed)
        handle.write("total_case_count=%d\n" % total_cases)
        handle.write("total_elapsed_seconds=%.3f\n" % (time.time() - start_time))
        handle.write("current_memory=%s\n" % current_memory())
        handle.write("case_name,cycle,target_cycle,status,last_checkpoint_cycle\n")
        for status in sorted(statuses, key=lambda item: item.get("case_name", "")):
            handle.write("%s,%s,%s,%s,%s\n" % (
                status.get("case_name", ""),
                status.get("cycle", ""),
                status.get("target_cycle", ""),
                status.get("status", ""),
                status.get("last_checkpoint_cycle", ""),
            ))


def write_final_outputs(stage_dir, results, args, started_at):
    completion_path = stage_dir / "STAGE15I_CASE_COMPLETION_SUMMARY.csv"
    fields = ["case_name", "group", "stress_min", "stress_max", "final_cycle", "target_cycle", "status", "elapsed_seconds", "cycles_per_hour", "summary_path", "selected_loops_path", "checkpoint_path", "status_path", "error"]
    with completion_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(results, key=lambda item: item["case_name"]):
            writer.writerow(row)

    metadata = {
        "backend": "real_neml",
        "neml_path": neml.__file__,
        "model": P2_MODEL,
        "target_cycles": args["target_cycles"],
        "points_per_cycle": args["points_per_cycle"],
        "active_workers": args["active_workers"],
        "stop_after_seconds": args["stop_after_seconds"],
        "started_at": started_at,
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "case_count": len(results),
        "results": results,
    }
    with (stage_dir / "STAGE15I_RUN_METADATA.json").open("w") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")

    completed = len([r for r in results if r.get("status") == "completed"])
    stopped = len([r for r in results if r.get("status") == "stopped_by_time_guard"])
    failed = len([r for r in results if r.get("status") == "failed"])
    max_cycle = max([int(r.get("final_cycle", 0)) for r in results] or [0])
    lines = [
        "# Stage 15I Real NEML Multi-Case Long Validation Sweep Summary",
        "",
        "Stage 15I ran real NEML `P2_three_backstress_screen` long-cycle baselines for B1-neighbouring and B2 diagnostic stress paths.",
        "",
        "| Field | Value |",
        "|---|---:|",
        "| Case count | %d |" % len(results),
        "| Completed cases | %d |" % completed,
        "| Stopped by time guard | %d |" % stopped,
        "| Failed cases | %d |" % failed,
        "| Maximum final cycle | %d |" % max_cycle,
        "| Target cycle | %d |" % args["target_cycles"],
        "| Active workers | %d |" % args["active_workers"],
    ]
    (stage_dir / "STAGE15I_MASTER_SUMMARY.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-cycles", type=int, default=PRIMARY_TARGET_CYCLES)
    parser.add_argument("--extension-target-cycles", type=int, default=EXTENSION_TARGET_CYCLES)
    parser.add_argument("--auto-extension", action="store_true")
    parser.add_argument("--points-per-cycle", type=int, default=POINTS_PER_CYCLE)
    parser.add_argument("--srate", type=float, default=1000.0)
    parser.add_argument("--temperature", type=float, default=300.0)
    parser.add_argument("--stop-after-seconds", type=float, default=STOP_GUARD_SECONDS)
    parser.add_argument("--status-every-seconds", type=float, default=60.0)
    parser.add_argument("--checkpoint-every", type=int, default=1000)
    parser.add_argument("--output-dir", default="case_outputs")
    parser.add_argument("--active-workers", type=int, default=int(os.environ.get("STAGE15I_ACTIVE_WORKERS", DEFAULT_ACTIVE_WORKERS)))
    parser.add_argument("--case", action="append", dest="case_names")
    parser.add_argument("--resume", action="store_true")
    args_ns = parser.parse_args()

    if args_ns.points_per_cycle != 40:
        raise SystemExit("Stage 15I requires points_per_cycle=40")
    target_cycles = args_ns.extension_target_cycles if args_ns.auto_extension else args_ns.target_cycles
    selected_cases = [case for case in CASES if not args_ns.case_names or case["case_name"] in set(args_ns.case_names)]
    if not selected_cases:
        raise SystemExit("No cases selected")

    stage_dir = Path(__file__).resolve().parent
    Path(args_ns.output_dir).mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    stop_at_epoch = start_time + args_ns.stop_after_seconds
    started_at = time.strftime("%Y-%m-%d %H:%M:%S")
    worker_args = {
        "target_cycles": target_cycles,
        "points_per_cycle": args_ns.points_per_cycle,
        "srate": args_ns.srate,
        "temperature": args_ns.temperature,
        "status_every_seconds": args_ns.status_every_seconds,
        "checkpoint_every": args_ns.checkpoint_every,
        "output_dir": args_ns.output_dir,
        "resume": args_ns.resume,
        "stop_at_epoch": stop_at_epoch,
    }

    results = []
    active_workers = min(args_ns.active_workers, len(selected_cases))
    with ProcessPoolExecutor(max_workers=active_workers) as executor:
        futures = [executor.submit(run_case, case, worker_args) for case in selected_cases]
        while futures:
            try:
                for future in as_completed(futures, timeout=30):
                    results.append(future.result())
                    futures.remove(future)
                    break
            except TimeoutError:
                pass
            write_global_status(stage_dir, args_ns.output_dir, active_workers, len(selected_cases), start_time, results)
    write_global_status(stage_dir, args_ns.output_dir, active_workers, len(selected_cases), start_time, results)
    write_final_outputs(stage_dir, results, {
        "target_cycles": target_cycles,
        "points_per_cycle": args_ns.points_per_cycle,
        "active_workers": active_workers,
        "stop_after_seconds": args_ns.stop_after_seconds,
    }, started_at)
    print("Stage 15I finished: %d cases" % len(results))
    return 1 if any(row.get("status") == "failed" for row in results) else 0


if __name__ == "__main__":
    sys.exit(main())
