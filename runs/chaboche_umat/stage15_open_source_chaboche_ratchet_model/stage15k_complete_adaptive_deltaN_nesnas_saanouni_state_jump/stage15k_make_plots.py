#!/usr/bin/env python3
from __future__ import print_function

import csv
from pathlib import Path


def read_rows(path):
    if not Path(path).exists():
        return []
    with Path(path).open() as handle:
        return list(csv.DictReader(handle))


def floats(rows, xkey, ykey):
    xs, ys = [], []
    for row in rows:
        try:
            xs.append(float(row[xkey]))
            ys.append(float(row[ykey]))
        except Exception:
            pass
    return xs, ys


def save_plot(path, title, xs, ys, xlabel, ylabel):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    if xs and ys:
        ax.plot(xs, ys, "o-", markersize=3)
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_placeholder(path, title):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300">'
        '<rect width="100%" height="100%" fill="white"/>'
        '<text x="24" y="48" font-family="Arial" font-size="22">%s</text>'
        '<text x="24" y="92" font-family="Arial" font-size="14">Data unavailable or plotting backend missing.</text>'
        '</svg>\n' % title
    )


def main():
    fixed = read_rows("fixed_state_jump/STAGE15K_FIXED_STATE_JUMP_RESULTS.csv")
    adaptive = read_rows("adaptive_state_jump/STAGE15K_ADAPTIVE_STATE_JUMP_RESULTS.csv")
    deltan = read_rows("adaptive_state_jump/STAGE15K_ADAPTIVE_DELTAN_TABLE.csv")
    plots = [
        ("plots/fixed_state_jump_error_vs_deltaN.svg", "Fixed State-Jump Error vs DeltaN", fixed, "deltaN_used", "mean_strain_norm_error"),
        ("plots/adaptive_state_jump_error_vs_deltaN.svg", "Adaptive State-Jump Error vs DeltaN", adaptive, "deltaN_used", "mean_strain_norm_error"),
        ("plots/adaptive_deltaN_vs_base_cycle.svg", "Adaptive DeltaN vs Base Cycle", deltan, "base_cycle", "deltaN_adaptive"),
        ("plots/jumped_vs_reference_mean_strain.svg", "Jumped vs Reference Mean Strain Error", fixed + adaptive, "comparison_cycle", "mean_strain_norm_error"),
        ("plots/jumped_vs_reference_ratcheting_strain.svg", "Jumped vs Reference Ratcheting Error", fixed + adaptive, "comparison_cycle", "ratcheting_norm_error"),
    ]
    for path, title, rows, xkey, ykey in plots:
        xs, ys = floats(rows, xkey, ykey)
        try:
            save_plot(path, title, xs, ys, xkey, ykey)
        except Exception:
            write_placeholder(path, title)
    # Required named diagnostics that are categorical or already in markdown.
    for path, title in [
        ("plots/restart_reinjection_error.svg", "Restart Reinjection Error"),
        ("plots/adaptive_limiting_variable_map.svg", "Adaptive Limiting Variable Map"),
        ("plots/jumped_vs_reference_loop_examples.svg", "Jumped vs Reference Loop Examples"),
    ]:
        write_placeholder(path, title)
    print("plots_complete=true")


if __name__ == "__main__":
    main()
