#!/usr/bin/env python3
"""Prepare a Stage 16N restart-enabled checkpoint deck.

This helper is intentionally conservative: it copies an existing Stage 16N
reference input deck and inserts Abaqus restart output requests. It does not
submit a job.
"""

from __future__ import annotations

import argparse
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles.inp"
OUT_DIR = STAGE_DIR / "stage16n_restart_control"


def insert_restart_requests(text: str, frequency: int) -> str:
    marker = "*Output, field"
    restart = f"*Restart, write, frequency={frequency}\n"
    if "*Restart, write" in text:
        return text
    if marker in text:
        return text.replace(marker, restart + marker, 1)
    return text + "\n" + restart


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--frequency", type=int, default=100, help="Abaqus restart write frequency in increments.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    source = args.source
    if not source.exists():
        raise FileNotFoundError(source)

    out = args.output_dir / source.name.replace(".inp", "_restart_enabled.inp")
    text = source.read_text(errors="replace")
    out.write_text(insert_restart_requests(text, args.frequency), encoding="utf-8")

    manifest = args.output_dir / "STAGE16N_RESTART_CONTROL_MANIFEST.md"
    manifest.write_text(
        "\n".join(
            [
                "# Stage 16N Restart Control Manifest",
                "",
                f"- Source deck: `{source.relative_to(STAGE_DIR)}`",
                f"- Restart-enabled deck: `{out.relative_to(STAGE_DIR)}`",
                f"- Restart write frequency: `{args.frequency}` increments",
                "",
                "Review the resulting Abaqus step/increment structure before HPC submission. The target checkpoint cycles are cycle 100, 250, and 500, but Abaqus restart output is increment-based, so the selected frequency must be checked against the generated loading history.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {out}")
    print(f"Wrote {manifest}")


if __name__ == "__main__":
    main()
