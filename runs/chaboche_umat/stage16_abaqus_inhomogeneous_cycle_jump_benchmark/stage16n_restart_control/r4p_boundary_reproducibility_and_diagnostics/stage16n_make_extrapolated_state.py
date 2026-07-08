#!/usr/bin/env python3
"""Build an extrapolated Stage 16N restart-overwrite state table.

The input CSVs must use the format written by
stage16n_extract_exact_state_for_reinjection.py.  The output uses the same
CSV and direct-access binary record layout, so the R3E UMAT read hook can be
reused for R3J.
"""

import argparse
import csv
import struct
from pathlib import Path


NSTATEV = 27
STRESS_COMPONENTS = 6
RECORD_DOUBLES = STRESS_COMPONENTS + NSTATEV


def read_state(path):
    if not path.exists():
        raise FileNotFoundError(path)
    rows = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = (int(row["NOEL"]), int(row["NPT"]))
            rows[key] = {
                name: float(row[name])
                for name in row
                if name not in {"NOEL", "NPT"} and row[name] != ""
            }
    return rows


def fmt(value):
    return "%.16g" % value


def write_outputs(
    previous,
    base,
    previous_cycle,
    base_cycle,
    jump_cycles,
    output_cycle,
    output_csv,
    output_bin,
    output_summary,
):
    if set(previous) != set(base):
        missing_previous = sorted(set(base) - set(previous))[:5]
        missing_base = sorted(set(previous) - set(base))[:5]
        raise RuntimeError(
            "State record keys differ; missing in previous=%s, missing in base=%s"
            % (missing_previous, missing_base)
        )

    slope_denominator = float(base_cycle - previous_cycle)
    if slope_denominator <= 0.0:
        raise ValueError("base_cycle must be greater than previous_cycle")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_bin.parent.mkdir(parents=True, exist_ok=True)
    fields = ["NOEL", "NPT"]
    fields += ["S%d" % i for i in range(1, STRESS_COMPONENTS + 1)]
    fields += ["SDV%d" % i for i in range(1, NSTATEV + 1)]

    keys = sorted(base)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for noel, npt in keys:
            row = {"NOEL": noel, "NPT": npt}
            for i in range(1, STRESS_COMPONENTS + 1):
                field = "S%d" % i
                row[field] = fmt(base[(noel, npt)].get(field, 0.0))
            for i in range(1, NSTATEV + 1):
                field = "SDV%d" % i
                base_value = base[(noel, npt)][field]
                previous_value = previous[(noel, npt)][field]
                slope = (base_value - previous_value) / slope_denominator
                row[field] = fmt(base_value + float(jump_cycles) * slope)
            writer.writerow(row)

    max_record = max((noel - 1) * 8 + npt for noel, npt in keys)
    with output_bin.open("wb") as handle:
        handle.truncate(max_record * RECORD_DOUBLES * 8)
        for noel, npt in keys:
            recno = (noel - 1) * 8 + npt
            values = []
            for i in range(1, STRESS_COMPONENTS + 1):
                values.append(base[(noel, npt)].get("S%d" % i, 0.0))
            for i in range(1, NSTATEV + 1):
                field = "SDV%d" % i
                base_value = base[(noel, npt)][field]
                previous_value = previous[(noel, npt)][field]
                slope = (base_value - previous_value) / slope_denominator
                values.append(base_value + float(jump_cycles) * slope)
            handle.seek((recno - 1) * RECORD_DOUBLES * 8)
            handle.write(struct.pack("<33d", *values))

    lines = [
        "# Stage 16N-R3J Extrapolated State",
        "",
        "- Previous cycle: `%d`" % previous_cycle,
        "- Base cycle: `%d`" % base_cycle,
        "- Slope pair: `%d -> %d`" % (previous_cycle, base_cycle),
        "- Jump cycles: `%d`" % jump_cycles,
        "- Extrapolated material-state cycle: `%d`" % output_cycle,
        "- Formula: `STATEV_jump = STATEV_base + jump_cycles * dSTATEV/dN`",
        "- Overwrite payload includes `SDV1-SDV27`; the R3J UMAT overwrites only `STATEV(1:25)`.",
        "- Stress columns are copied from the base cycle and are not used by the R3J UMAT overwrite.",
        "- Element/IP records: `%d`" % len(keys),
        "- State CSV: `%s`" % output_csv.name,
        "- State binary: `%s`" % output_bin.name,
    ]
    output_summary.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous-csv", type=Path, required=True)
    parser.add_argument("--base-csv", type=Path, required=True)
    parser.add_argument("--previous-cycle", type=int, required=True)
    parser.add_argument("--base-cycle", type=int, required=True)
    parser.add_argument("--jump-cycles", type=int, required=True)
    parser.add_argument("--output-cycle", type=int, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-bin", type=Path, required=True)
    parser.add_argument("--output-summary", type=Path, required=True)
    args = parser.parse_args()

    write_outputs(
        previous=read_state(args.previous_csv),
        base=read_state(args.base_csv),
        previous_cycle=args.previous_cycle,
        base_cycle=args.base_cycle,
        jump_cycles=args.jump_cycles,
        output_cycle=args.output_cycle,
        output_csv=args.output_csv,
        output_bin=args.output_bin,
        output_summary=args.output_summary,
    )


if __name__ == "__main__":
    main()
