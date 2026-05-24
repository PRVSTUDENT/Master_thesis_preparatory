#!/usr/bin/env python3
"""Correct Stage 15E best-method ranking with acceptance-first priority."""

import os
import shlex
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    if os.environ.get("STAGE15F_MODULE_REEXEC") != "1":
        command = (
            "source /etc/profile >/dev/null 2>&1; "
            "module purge >/dev/null 2>&1 || true; "
            "module load python/gcc/11.4.0/3.11.7 >/dev/null 2>&1 || true; "
            "export STAGE15F_MODULE_REEXEC=1; "
            "exec python3 "
            + " ".join(shlex.quote(arg) for arg in sys.argv)
        )
        os.execvp("bash", ["bash", "-lc", command])
    raise


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DOC_RESULTS = REPO / "docs" / "stage15_real_neml_cycle_jump_package" / "stage15e_results"
RUN_RESULTS = HERE.parent / "stage15e_real_neml_cycle_jump_benchmark"
OUTPUT_NAME = "STAGE15E_BEST_ACCEPTED_METHODS_BY_TARGET.csv"


def rank_stage15e(acceptance_path, output_path):
    df = pd.read_csv(acceptance_path)
    df["primary_error_score"] = (
        df["mean_normalized_error_percent"].astype(float)
        + df["ratcheting_normalized_error_percent"].astype(float)
        + df["peak_normalized_error_percent"].astype(float)
    )
    df["acceptance_rank"] = 4
    df.loc[df["relaxed_5pct_accept"].astype(bool), "acceptance_rank"] = 3
    df.loc[df["relaxed_2pct_accept"].astype(bool), "acceptance_rank"] = 2
    df.loc[df["strict_1pct_accept"].astype(bool), "acceptance_rank"] = 1
    ranked = df.sort_values(
        [
            "case_name",
            "target_cycle",
            "acceptance_rank",
            "primary_error_score",
            "base_cycle",
            "method",
        ]
    )
    best = ranked.groupby(["case_name", "target_cycle"], as_index=False).first()
    best = best.drop(columns=["acceptance_rank"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best.to_csv(output_path, index=False)
    return best


def main():
    acceptance = DOC_RESULTS / "STAGE15E_ACCEPTANCE_TABLE.csv"
    if not acceptance.exists():
        raise SystemExit("Missing Stage 15E acceptance table: %s" % acceptance)
    best = rank_stage15e(acceptance, DOC_RESULTS / OUTPUT_NAME)
    if (RUN_RESULTS / "STAGE15E_ACCEPTANCE_TABLE.csv").exists():
        rank_stage15e(RUN_RESULTS / "STAGE15E_ACCEPTANCE_TABLE.csv", RUN_RESULTS / OUTPUT_NAME)
    print("Wrote %s rows to %s" % (len(best), DOC_RESULTS / OUTPUT_NAME))


if __name__ == "__main__":
    raise SystemExit(main())

