from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "stage16n_1000cycle_pilot"
OUT = PILOT / "figures"

JOB = "stage16n_plate_hole_neml_equiv_1000cycles"
LOOPS_CSV = PILOT / f"{JOB}_selected_cycle_loops.csv"
METRICS_CSV = PILOT / f"{JOB}_cycle_metrics.csv"
LOCAL_CSV = PILOT / f"{JOB}_selected_cycle_local_states.csv"


def style_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.28)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    loops = pd.read_csv(LOOPS_CSV)
    metrics = pd.read_csv(METRICS_CSV)
    local = pd.read_csv(LOCAL_CSV)

    # Cycle 593 is incomplete because PBS killed the run mid-step.
    metrics = metrics[metrics["cycle"] <= 592].copy()
    loops = loops[loops["cycle"] <= 592].copy()
    local = local[local["cycle"] <= 592].copy()
    return loops, metrics, local


def plot_hysteresis_overlay(loops: pd.DataFrame) -> Path:
    path = OUT / "stage16n_592ref_hysteresis_selected_cycles.png"
    fig, ax = plt.subplots(figsize=(9.5, 6.5), dpi=180)
    cycles = [1, 2, 10, 50, 100, 250, 500]
    cmap = plt.get_cmap("viridis")

    for i, cycle in enumerate(cycles):
        data = loops[loops["cycle"] == cycle].sort_values("local_time")
        if data.empty:
            continue
        ax.plot(
            data["U1_avg"],
            data["RF1_sum"],
            linewidth=1.7,
            color=cmap(i / max(1, len(cycles) - 1)),
            label=f"cycle {cycle}",
        )

    style_axes(
        ax,
        "Stage 16N hysteresis loop evolution, selected cycles",
        "Average U1 displacement",
        "Summed RF1 reaction force",
    )
    ax.legend(ncols=2, fontsize=9, frameon=True)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_hysteresis_panels(loops: pd.DataFrame) -> Path:
    path = OUT / "stage16n_592ref_hysteresis_cycle_panels.png"
    groups = [(1, 2), (10, 50), (100, 250), (500,)]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), dpi=180, sharex=True, sharey=True)
    cmap = plt.get_cmap("plasma")

    for ax, group in zip(axes.ravel(), groups):
        for i, cycle in enumerate(group):
            data = loops[loops["cycle"] == cycle].sort_values("local_time")
            if data.empty:
                continue
            ax.plot(
                data["U1_avg"],
                data["RF1_sum"],
                linewidth=1.8,
                color=cmap((i + 1) / (len(group) + 1)),
                label=f"cycle {cycle}",
            )
        title = "cycle " + ", ".join(str(c) for c in group)
        style_axes(ax, title, "Average U1", "Summed RF1")
        ax.legend(fontsize=8, frameon=True)

    fig.suptitle("Stage 16N selected hysteresis loops by cycle group", fontsize=14)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_global_evolution(metrics: pd.DataFrame) -> Path:
    path = OUT / "stage16n_592ref_global_loop_metrics.png"
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), dpi=180, sharex=True)

    axes[0].plot(metrics["cycle"], metrics["RF1_max"], color="#0072B2", linewidth=1.5, label="RF1 max")
    axes[0].plot(metrics["cycle"], metrics["RF1_min"], color="#D55E00", linewidth=1.5, label="RF1 min")
    style_axes(axes[0], "Reaction-force envelope", "", "RF1")
    axes[0].legend(fontsize=9)

    axes[1].plot(metrics["cycle"], metrics["loop_area_abs"], color="#009E73", linewidth=1.5)
    style_axes(axes[1], "Absolute hysteresis loop area", "", "|loop area|")

    baseline = metrics.iloc[0]
    loop_change = (metrics["loop_area_abs"] / baseline["loop_area_abs"] - 1.0) * 100.0
    rfmax_change = (metrics["RF1_max"] / baseline["RF1_max"] - 1.0) * 100.0
    axes[2].plot(metrics["cycle"], rfmax_change, color="#0072B2", linewidth=1.4, label="RF1 max change")
    axes[2].plot(metrics["cycle"], loop_change, color="#009E73", linewidth=1.4, label="loop area change")
    axes[2].axhline(5.0, color="#666666", linestyle="--", linewidth=1.0, label="5% threshold")
    style_axes(axes[2], "Change relative to cycle 1", "Cycle", "Change [%]")
    axes[2].legend(fontsize=9)

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_local_evolution(local: pd.DataFrame) -> Path:
    path = OUT / "stage16n_592ref_local_hole_state_evolution.png"
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), dpi=180, sharex=True)

    axes[0].plot(local["cycle"], local["HOLE_RING_MISES_MAX"], marker="o", color="#CC79A7", label="Hole-ring Mises max")
    axes[0].plot(local["cycle"], local["HOLE_RING_S11_MAX_ABS"], marker="s", color="#E69F00", label="Hole-ring |S11| max")
    style_axes(axes[0], "Local hole-ring stress evolution", "", "Stress")
    axes[0].legend(fontsize=9)

    for column, label, color in [
        ("HOLE_RING_SDV1_MAX", "SDV1 max", "#0072B2"),
        ("HOLE_RING_SDV11_MAX", "SDV11 max", "#009E73"),
        ("HOLE_RING_SDV8_MAX", "SDV8 max", "#D55E00"),
    ]:
        if column in local.columns:
            axes[1].plot(local["cycle"], local[column], marker="o", linewidth=1.5, color=color, label=label)
    style_axes(axes[1], "Selected local STATEV evolution near hole", "Cycle", "State variable value")
    axes[1].legend(fontsize=9)

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    loops, metrics, local = load_data()
    paths = [
        plot_hysteresis_overlay(loops),
        plot_hysteresis_panels(loops),
        plot_global_evolution(metrics),
        plot_local_evolution(local),
    ]
    for path in paths:
        print(path.relative_to(ROOT.parent.parent.parent))


if __name__ == "__main__":
    main()
