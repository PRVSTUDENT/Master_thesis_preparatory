#!/usr/bin/env python3
"""Prepare Stage 16N-B exact state reinjection verification cases.

This script does not extrapolate state.  It creates no-jump continuation decks
from exact states extracted at selected base cycles.  The cases are the gate
that verifies SDVINI/SIGINI mapping before any cycle-jump extrapolation is used.
"""

from __future__ import print_function

import argparse
import os
import re
import shutil
from pathlib import Path

from prepare_stage16_plate_with_hole_model import chunks, make_mesh
from prepare_stage16n_neml_plate_with_hole_1000cycles import PARAMS


STAGE_DIR = Path(__file__).resolve().parent
BASE_UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
READER = STAGE_DIR / "stage16n_sdvini_sigini_state_reader.for"
OUT_DIR = STAGE_DIR / "stage16n_exact_reinjection"
STATE_DIR = OUT_DIR / "state"
CASES_DIR = OUT_DIR / "cases"

CASES = [
    ("B0_100_to_250", 100, 250),
    ("B0_250_to_500", 250, 500),
    ("B0_500_to_1000", 500, 1000),
]


def write_set(lines, keyword, values):
    lines.append(keyword)
    for chunk in chunks(values):
        lines.append(", ".join(str(v) for v in chunk))


def strip_empty_hooks(text):
    marker = "C Empty initialization hooks."
    index = text.find(marker)
    if index < 0:
        raise RuntimeError("Could not locate empty SIGINI/SDVINI hooks in %s" % BASE_UMAT)
    return text[:index].rstrip() + "\n\n"


def write_case_umat(case_dir, state_filename):
    base = strip_empty_hooks(BASE_UMAT.read_text())
    hooks = READER.read_text().replace("__STATE_FILE__", state_filename)
    path = case_dir / "stage16n_sdvini_sigini_state_reader.for"
    path.write_text(base + hooks + "\n")
    return path


def write_deck(path, job, base_cycle, compare_cycle):
    mesh = make_mesh(20.0, 10.0, 1.0, 1.0, 0.25, 0.25)
    lines = [
        "** Stage 16N-B exact reinjection verification",
        "** Exact state at cycle %d, normal continuation to cycle %d" % (base_cycle, compare_cycle),
        "*HEADING",
        "Stage 16N-B exact reinjection %d to %d" % (base_cycle, compare_cycle),
        "*PART, NAME=PLATE_HOLE",
        "*NODE",
    ]
    for nid, x, y, z in mesh["nodes"]:
        lines.append("%d, %.8g, %.8g, %.8g" % (nid, x, y, z))
    lines.append("*ELEMENT, TYPE=C3D8, ELSET=PLATE_ALL")
    for elem in mesh["elements"]:
        lines.append(", ".join(str(v) for v in elem))
    write_set(lines, "*ELSET, ELSET=HOLE_RING", mesh["hole_ring"])
    lines.extend([
        "*SOLID SECTION, ELSET=PLATE_ALL, MATERIAL=NEML_EQUIV_CHABOCHE",
        "*END PART",
        "*ASSEMBLY, NAME=ASSEMBLY",
        "*INSTANCE, NAME=PLATE_INST, PART=PLATE_HOLE",
        "*END INSTANCE",
    ])
    write_set(lines, "*NSET, NSET=LEFT_EDGE, INSTANCE=PLATE_INST", mesh["left_nodes"])
    write_set(lines, "*NSET, NSET=RIGHT_EDGE, INSTANCE=PLATE_INST", mesh["right_nodes"])
    lines.extend([
        "*NSET, NSET=ANCHOR_A, INSTANCE=PLATE_INST",
        str(mesh["anchor_a"]),
        "*NSET, NSET=ANCHOR_B, INSTANCE=PLATE_INST",
        str(mesh["anchor_b"]),
        "*ELSET, ELSET=HOLE_RING, INSTANCE=PLATE_INST",
    ])
    for chunk in chunks(mesh["hole_ring"]):
        lines.append(", ".join(str(v) for v in chunk))
    lines.extend([
        "*END ASSEMBLY",
        "*MATERIAL, NAME=NEML_EQUIV_CHABOCHE",
        "*DEPVAR",
        "27",
        "*USER MATERIAL, CONSTANTS=11",
        "{E}, {nu}, {yield}, {Q}, {b}, {C1}, {g1}, {C2}, {g2}, {C3}, {g3}".format(**PARAMS),
        "*INITIAL CONDITIONS, TYPE=SOLUTION, USER",
        "*INITIAL CONDITIONS, TYPE=STRESS, USER",
        "*AMPLITUDE, NAME=AMP_ONE_CYCLE, DEFINITION=TABULAR",
        "0.00, 0.0",
        "0.25, 1.0",
        "0.50, 0.0",
        "0.75, -1.0",
        "1.00, 0.0",
    ])

    for cycle in range(base_cycle + 1, compare_cycle + 1):
        lines.extend([
            "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
            "*STATIC",
            "0.005, 1.0, 1.0E-08, 0.025",
        ])
        if cycle == base_cycle + 1:
            lines.extend([
                "*BOUNDARY",
                "LEFT_EDGE, 1, 1, 0.0",
                "ANCHOR_A, 2, 3, 0.0",
                "ANCHOR_B, 3, 3, 0.0",
            ])
        lines.extend([
            "*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE",
            "RIGHT_EDGE, 1, 1, 0.10",
            "*OUTPUT, HISTORY, FREQUENCY=1",
            "*NODE OUTPUT, NSET=RIGHT_EDGE",
            "U1, RF1",
        ])
        if cycle == compare_cycle:
            lines.extend([
                "*OUTPUT, FIELD, NUMBER INTERVAL=4",
                "*NODE OUTPUT",
                "U, RF",
                "*ELEMENT OUTPUT",
                "S, SDV",
            ])
        lines.append("*END STEP")

    path.write_text("\n".join(lines) + "\n")
    return mesh


def prepare_case(name, base_cycle, compare_cycle):
    state_csv = STATE_DIR / ("stage16n_exact_state_cycle%04d.csv" % base_cycle)
    if not state_csv.exists():
        raise RuntimeError(
            "Missing exact state CSV for cycle %d: %s\n"
            "Run stage16n_extract_exact_state_for_reinjection.py first." % (base_cycle, state_csv)
        )

    case_dir = CASES_DIR / name
    case_dir.mkdir(parents=True, exist_ok=True)
    job = "stage16n_exact_%s" % name.lower()
    local_state_name = "state.csv"
    shutil.copy2(state_csv, case_dir / local_state_name)
    umat = write_case_umat(case_dir, local_state_name)
    mesh = write_deck(case_dir / (job + ".inp"), job, base_cycle, compare_cycle)

    manifest = [
        "# Stage 16N-B Exact Reinjection Case",
        "",
        "- Case: `%s`" % name,
        "- Job: `%s`" % job,
        "- Base cycle: `%d`" % base_cycle,
        "- Compare cycle: `%d`" % compare_cycle,
        "- Continuation cycles: `%d`" % (compare_cycle - base_cycle),
        "- Source state CSV: `%s`" % state_csv.name,
        "- Local state CSV used by Fortran: `%s`" % local_state_name,
        "- UMAT with reader hooks: `%s`" % umat.name,
        "- Nodes: `%d`" % len(mesh["nodes"]),
        "- Elements: `%d`" % len(mesh["elements"]),
        "- Hole-ring elements: `%d`" % len(mesh["hole_ring"]),
        "- Production policy: `1 MPI rank x 16 OpenMP threads`",
    ]
    (case_dir / "STAGE16N_EXACT_REINJECTION_CASE_MANIFEST.md").write_text("\n".join(manifest) + "\n")
    print("Prepared %s" % case_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="all", help="all or comma-separated case names")
    args = parser.parse_args()

    selected = None
    if args.cases != "all":
        selected = set(part.strip() for part in args.cases.split(",") if part.strip())

    for name, base_cycle, compare_cycle in CASES:
        if selected is not None and name not in selected:
            continue
        prepare_case(name, base_cycle, compare_cycle)


if __name__ == "__main__":
    main()
