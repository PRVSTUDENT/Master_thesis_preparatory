#!/usr/bin/env python3
"""Create reduced target-cycle summary for Stage 15I."""

import argparse
import csv
from pathlib import Path

import pandas as pd

from stage15i_case_definitions import PRESERVED_TARGET_CYCLES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="case_outputs")
    parser.add_argument("--output", default="STAGE15I_TARGET_CYCLE_VALUES.csv")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    frames = []
    keep = set(PRESERVED_TARGET_CYCLES)
    for path in sorted(input_dir.glob("*_cycle_summary.csv")):
        if path.stat().st_size == 0:
            continue
        df = pd.read_csv(path)
        if "cycle" not in df.columns:
            continue
        target_rows = df[df["cycle"].isin(keep)].copy()
        if len(df):
            final_row = df.iloc[[-1]].copy()
            target_rows = pd.concat([target_rows, final_row], ignore_index=True).drop_duplicates(
                subset=["case_name", "cycle"], keep="last"
            )
        frames.append(target_rows)

    if frames:
        out = pd.concat(frames, ignore_index=True).sort_values(["case_name", "cycle"])
    else:
        out = pd.DataFrame()
    out.to_csv(args.output, index=False, quoting=csv.QUOTE_MINIMAL)
    print("wrote %s rows to %s" % (len(out), args.output))


if __name__ == "__main__":
    main()
