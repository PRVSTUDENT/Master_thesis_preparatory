#!/usr/bin/env python3
"""Generate figures for the Stage 16N adaptive cycle-jump boundary."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


TRUE_JUMP_MODES = {
    "repeat_true_jump",
    "diagnostic_repeat",
    "8core_calibration",
}


def read_rows(csv_path):
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["target"] = int(row["target"])
        row["max_global_error"] = float(row["max_global_error"])
        row["max_primary_local_error"] = float(row["max_primary_local_error"])
        row["s11_error"] = float(row["s11_error"])
    return rows


def aggregate_true_jump_rows(rows):
    """Return one worst-case true-jump row per target."""
    grouped = {}
    for row in rows:
        if row["mode"] not in TRUE_JUMP_MODES:
            continue
        target = row["target"]
        current = grouped.get(target)
        if current is None or row["max_primary_local_error"] > current["max_primary_local_error"]:
            grouped[target] = row
    return [grouped[target] for target in sorted(grouped)]


def annotate_boundary(ax):
    ax.axvline(271, color="#2f9e44", linestyle="--", linewidth=1.4, alpha=0.9)
    ax.axvline(272, color="#d9480f", linestyle="--", linewidth=1.4, alpha=0.9)
    ax.text(271, 15.1, "target271 accepted", color="#2f9e44", ha="right", va="top", fontsize=9)
    ax.text(272, 15.1, "target272 rejected", color="#d9480f", ha="left", va="top", fontsize=9)


def plot_error_vs_target(rows, output_path):
    true_jump_rows = aggregate_true_jump_rows(rows)
    targets = [row["target"] for row in true_jump_rows]

    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=160)
    ax.plot(
        targets,
        [row["max_global_error"] for row in true_jump_rows],
        marker="o",
        linewidth=2,
        color="#1c7ed6",
        label="Max global error",
    )
    ax.plot(
        targets,
        [row["max_primary_local_error"] for row in true_jump_rows],
        marker="s",
        linewidth=2,
        color="#6741d9",
        label="Max primary-local error",
    )
    ax.plot(
        targets,
        [row["s11_error"] for row in true_jump_rows],
        marker="^",
        linewidth=2,
        color="#e67700",
        label="S11 error",
    )

    annotate_boundary(ax)
    ax.set_title("Stage 16N adaptive boundary errors")
    ax.set_xlabel("Target cycle")
    ax.set_ylabel("Error (%)")
    ax.set_xticks(targets)
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def draw_jump(ax, y, target, status, label, color):
    ax.plot([250, target], [y, y], color=color, linewidth=4, solid_capstyle="round")
    ax.scatter([250], [y], s=80, color="#495057", zorder=3)
    ax.scatter([target], [y], s=130, color=color, edgecolor="white", linewidth=1.5, zorder=4)
    ax.annotate(
        "",
        xy=(target, y),
        xytext=(250, y),
        arrowprops={"arrowstyle": "->", "color": color, "lw": 2.2, "shrinkA": 8, "shrinkB": 8},
    )
    ax.text(248.5, y, "source250", ha="right", va="center", fontsize=9, color="#343a40")
    ax.text(target + 1.0, y, "target{} {}".format(target, status), ha="left", va="center", fontsize=10, color=color)
    ax.text(261, y + 0.16, label, ha="center", va="bottom", fontsize=9, color="#343a40")


def plot_cycle_jump_boundary(rows, output_path):
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=160)
    pass_color = "#2f9e44"
    fail_color = "#d9480f"
    control_color = "#0b7285"

    draw_jump(ax, 3.0, 270, "pass", "true jump", pass_color)
    draw_jump(ax, 2.0, 271, "pass", "accepted true-jump boundary", pass_color)
    draw_jump(ax, 1.0, 272, "fail", "first rejected true jump", fail_color)

    ax.plot([250, 272], [0.0, 0.0], color=control_color, linewidth=4, solid_capstyle="round")
    ax.scatter([250, 272], [0.0, 0.0], s=[80, 130], color=[("#495057"), control_color], edgecolor="white", linewidth=1.5, zorder=4)
    ax.annotate(
        "",
        xy=(272, 0.0),
        xytext=(250, 0.0),
        arrowprops={"arrowstyle": "->", "color": control_color, "lw": 2.2, "shrinkA": 8, "shrinkB": 8},
    )
    ax.text(248.5, 0.0, "source250", ha="right", va="center", fontsize=9, color="#343a40")
    ax.text(273.0, 0.0, "target272 exact/native pass", ha="left", va="center", fontsize=10, color=control_color)
    ax.text(261, 0.16, "restart-continuity control", ha="center", va="bottom", fontsize=9, color="#343a40")

    ax.set_title("Stage 16N adaptive cycle-jump boundary")
    ax.set_xlim(247, 278)
    ax.set_ylim(-0.55, 3.6)
    ax.set_xlabel("Cycle")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.grid(True, axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "stage16n_boundary_summary.csv"
    figures_dir = project_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    rows = read_rows(csv_path)
    plot_error_vs_target(rows, figures_dir / "error_vs_target.png")
    plot_cycle_jump_boundary(rows, figures_dir / "cycle_jump_boundary.png")

    print("Wrote {}".format(figures_dir / "error_vs_target.png"))
    print("Wrote {}".format(figures_dir / "cycle_jump_boundary.png"))


if __name__ == "__main__":
    main()
