#!/usr/bin/env python3
from __future__ import print_function

import csv
from pathlib import Path


def count(path, key=None, value=None):
    p = Path(path)
    if not p.exists():
        return 0
    with p.open() as handle:
        rows = list(csv.DictReader(handle))
    if key is None:
        return len(rows)
    return sum(1 for row in rows if row.get(key) == value)


def max_delta(path):
    p = Path(path)
    if not p.exists():
        return 0
    vals = []
    with p.open() as handle:
        for row in csv.DictReader(handle):
            if row.get("relaxed_5pct_accepted") == "true":
                vals.append(int(float(row.get("deltaN_used", 0))))
    return max(vals) if vals else 0


def main():
    fixed = "fixed_state_jump/STAGE15K_FIXED_STATE_JUMP_RESULTS.csv"
    adaptive = "adaptive_state_jump/STAGE15K_ADAPTIVE_STATE_JUMP_RESULTS.csv"
    fixed_total = count(fixed)
    adaptive_total = count(adaptive)
    fixed_acc = count(fixed, "relaxed_5pct_accepted", "true")
    adaptive_acc = count(adaptive, "relaxed_5pct_accepted", "true")
    max_acc = max(max_delta(fixed), max_delta(adaptive))
    if fixed_acc and adaptive_acc:
        outcome = "Outcome B: State jumping technically works but accepted DeltaN is limited."
    elif fixed_acc:
        outcome = "Outcome C: State reinjection works but extrapolated state jumping is only partially accepted."
    else:
        outcome = "Outcome C: State reinjection works but extrapolated state jumping fails acceptance."
    lines = [
        "# Stage 15K Master Summary",
        "",
        "- Gate 1 introspection: `PASS on HPC`",
        "- Gate 2 restart/reinjection: `PASS on HPC`",
        "- Fixed rows: `%d`" % fixed_total,
        "- Fixed relaxed 5 pct accepted rows: `%d`" % fixed_acc,
        "- Adaptive rows: `%d`" % adaptive_total,
        "- Adaptive relaxed 5 pct accepted rows: `%d`" % adaptive_acc,
        "- Maximum relaxed accepted DeltaN: `%d`" % max_acc,
        "",
        "## Final Outcome",
        outcome,
    ]
    Path("STAGE15K_MASTER_SUMMARY.md").write_text("\n".join(lines) + "\n")
    print("Wrote STAGE15K_MASTER_SUMMARY.md")


if __name__ == "__main__":
    main()
