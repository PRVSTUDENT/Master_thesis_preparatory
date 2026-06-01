#!/usr/bin/env python3
from __future__ import print_function

import csv
from pathlib import Path


def count_rows(path):
    if not path.exists():
        return 0
    with path.open() as handle:
        return max(0, sum(1 for _ in handle) - 1)


def accepted_rows(path):
    if not path.exists():
        return 0
    with path.open() as handle:
        return sum(1 for row in csv.DictReader(handle) if row.get("relaxed_5pct_accepted") == "true")


def main():
    fixed = Path("fixed_state_jump/STAGE15K_FIXED_STATE_JUMP_RESULTS.csv")
    adaptive = Path("adaptive_state_jump/STAGE15K_ADAPTIVE_STATE_JUMP_RESULTS.csv")
    lines = [
        "# Stage 15K Baseline Validation",
        "",
        "- Fixed result rows: `%d`" % count_rows(fixed),
        "- Fixed relaxed 5 pct accepted rows: `%d`" % accepted_rows(fixed),
        "- Adaptive result rows: `%d`" % count_rows(adaptive),
        "- Adaptive relaxed 5 pct accepted rows: `%d`" % accepted_rows(adaptive),
    ]
    Path("STAGE15K_COMPLETE_IMPLEMENTATION_STATUS.md").write_text("\n".join(lines) + "\n")
    print("Wrote STAGE15K_COMPLETE_IMPLEMENTATION_STATUS.md")


if __name__ == "__main__":
    main()
