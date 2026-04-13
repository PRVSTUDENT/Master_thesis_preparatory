"""
plot_results.py
===============
Standalone post-processing script: reads a force-displacement CSV produced by
``extract_results.py`` and generates hysteresis-loop and peak-force evolution
plots.

Usage (standard Python — no Abaqus required)
--------------------------------------------
    python scripts/plot_results.py \\
        --data   results/<job_name>_fd.csv \\
        --output results/<job_name>_hysteresis.png

Dependencies
------------
    pip install numpy matplotlib
"""

import argparse
import csv
import os
import sys


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot force-displacement data from a cyclic-jump simulation."
    )
    parser.add_argument(
        "--data", required=True,
        help="Path to the CSV file produced by extract_results.py."
    )
    parser.add_argument(
        "--output",
        help=(
            "Output image path (PNG or PDF). "
            "Defaults to the same directory as --data with a .png extension."
        ),
    )
    parser.add_argument(
        "--last-loop", action="store_true",
        help="If set, plot only the last hysteresis loop (last loading cycle)."
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_csv(csv_path):
    """Return lists of (time, displacement_mm, force_N) read from a CSV file."""
    times, disps, forces = [], [], []
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            times.append(float(row["time"]))
            disps.append(float(row["displacement_mm"]))
            forces.append(float(row["force_N"]))
    return times, disps, forces


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot(times, disps, forces, output_path, last_loop_only=False):
    """Generate and save the force-displacement plots."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # non-interactive backend for HPC / headless runs
        import matplotlib.pyplot as plt
    except ImportError:
        sys.exit(
            "matplotlib is required for plotting.\n"
            "Install it with:  pip install matplotlib"
        )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Cyclic Jump Simulation — Force-Displacement Analysis", fontsize=13)

    # --- Left panel: hysteresis loop ----------------------------------------
    ax = axes[0]
    if last_loop_only:
        # Find the last sign-reversal pair to isolate the final loop
        idx_start = _find_last_loop_start(disps)
        d_plot = disps[idx_start:]
        f_plot = forces[idx_start:]
        ax.set_title("Last Hysteresis Loop")
    else:
        d_plot = disps
        f_plot = forces
        ax.set_title("Force-Displacement (all data)")

    ax.plot(d_plot, f_plot, linewidth=0.8, color="steelblue")
    ax.set_xlabel("Displacement (mm)")
    ax.set_ylabel("Force (N)")
    ax.axhline(0, color="k", linewidth=0.5, linestyle="--")
    ax.axvline(0, color="k", linewidth=0.5, linestyle="--")
    ax.grid(True, linestyle=":", alpha=0.6)

    # --- Right panel: peak force vs. time ------------------------------------
    ax2 = axes[1]
    # Compute simple rolling maximum of |force| per "half cycle"
    peak_times, peak_forces = _rolling_peak(times, forces)
    ax2.plot(peak_times, peak_forces, marker="o", markersize=3,
             linewidth=0.8, color="tomato")
    ax2.set_title("Peak Force Evolution")
    ax2.set_xlabel("Time (Abaqus pseudo-time)")
    ax2.set_ylabel("|Force| peak (N)")
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print("Figure saved to: {}".format(output_path))


def _find_last_loop_start(disps, n_points_loop=20):
    """Return the index of the start of the last complete loop (heuristic)."""
    if len(disps) <= n_points_loop:
        return 0
    return max(0, len(disps) - n_points_loop)


def _rolling_peak(times, forces, window=10):
    """Return (times, peaks) sampled at the end of each window."""
    peak_t, peak_f = [], []
    n = len(forces)
    for i in range(0, n, window):
        block = forces[i : i + window]
        if block:
            peak_t.append(times[min(i + window - 1, n - 1)])
            peak_f.append(max(abs(f) for f in block))
    return peak_t, peak_f


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args.data):
        sys.exit("Data file not found: {}".format(args.data))

    if args.output is None:
        base = os.path.splitext(args.data)[0]
        args.output = base + "_plot.png"

    times, disps, forces = load_csv(args.data)
    plot(times, disps, forces, args.output, last_loop_only=args.last_loop)
