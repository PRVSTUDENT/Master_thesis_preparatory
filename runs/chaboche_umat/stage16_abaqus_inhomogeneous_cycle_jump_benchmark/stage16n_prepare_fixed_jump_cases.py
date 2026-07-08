#!/usr/bin/env python3
"""Prepare Stage 16N-C fixed state-initialized cycle-jump cases.

The first case uses a conservative zero-order jump: the exact cycle-100 state is
used as the initialization state for a run that resumes at cycle 126 and is
interpreted as a jump from cycle 100 to cycle 125.
"""

from __future__ import print_function

import argparse
import os
import shutil
from pathlib import Path

from prepare_stage16_plate_with_hole_model import chunks, make_mesh
from prepare_stage16n_neml_plate_with_hole_1000cycles import PARAMS
from stage16n_prepare_exact_reinjection_cases import strip_empty_hooks


STAGE_DIR = Path(__file__).resolve().parent
BASE_UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
READER = STAGE_DIR / "stage16n_sdvini_sigini_state_reader.for"
REINJECTION_DIR = STAGE_DIR / "stage16n_exact_reinjection"
STATE_DIR = REINJECTION_DIR / "state"
OUT_DIR = STAGE_DIR / "stage16n_fixed_jump_validation"
CASES_DIR = OUT_DIR / "cases"

CASES = [
    {
        "name": "B1_100_to_125_to_250",
        "base_cycle": 100,
        "jump_target_cycle": 125,
        "compare_cycle": 250,
        "state_strategy": "zero_order_hold_from_base_cycle",
    },
    {
        "name": "B2_250_to_300_to_500",
        "base_cycle": 250,
        "jump_target_cycle": 300,
        "compare_cycle": 500,
        "state_strategy": "zero_order_hold_from_base_cycle",
    },
    {
        "name": "B3_500_to_575_to_750",
        "base_cycle": 500,
        "jump_target_cycle": 575,
        "compare_cycle": 750,
        "state_strategy": "zero_order_hold_from_base_cycle",
    },
]


def write_set(lines, keyword, values):
    lines.append(keyword)
    for chunk in chunks(values):
        lines.append(", ".join(str(v) for v in chunk))


def write_case_umat(case_dir, state_filename):
    base = strip_empty_hooks(BASE_UMAT.read_text())
    hooks = READER.read_text().replace("__STATE_FILE__", state_filename)
    path = case_dir / "stage16n_sdvini_sigini_state_reader.for"
    path.write_text(base + hooks + "\n")
    return path


def write_deck(path, job, base_cycle, jump_target_cycle, compare_cycle):
    mesh = make_mesh(20.0, 10.0, 1.0, 1.0, 0.25, 0.25)
    lines = [
        "** Stage 16N-C fixed state-initialized cycle-jump validation",
        "** Zero-order jump from cycle %d to cycle %d, continuation to cycle %d" % (
            base_cycle,
            jump_target_cycle,
            compare_cycle,
        ),
        "*HEADING",
        "Stage 16N-C fixed jump %d to %d to %d" % (base_cycle, jump_target_cycle, compare_cycle),
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
        "*STEP, NAME=FIXED_JUMP_EQUILIBRATE_TO_CYCLE_%04d, NLGEOM=NO, INC=400" % jump_target_cycle,
        "*STATIC",
        "1.0E-06, 1.0, 1.0E-12, 1.0E-02",
        "*BOUNDARY",
        "LEFT_EDGE, 1, 1, 0.0",
        "ANCHOR_A, 2, 3, 0.0",
        "ANCHOR_B, 3, 3, 0.0",
        "RIGHT_EDGE, 1, 1, 0.0",
        "*OUTPUT, FIELD, NUMBER INTERVAL=1",
        "*ELEMENT OUTPUT",
        "S, SDV",
        "*END STEP",
    ])

    for cycle in range(jump_target_cycle + 1, compare_cycle + 1):
        lines.extend([
            "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
            "*STATIC",
            "0.005, 1.0, 1.0E-08, 0.025",
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


def write_submit_script(case_dir, job, name):
    submit_dir = OUT_DIR / "submits"
    submit_dir.mkdir(parents=True, exist_ok=True)
    rel_case = os.path.relpath(str(case_dir), str(STAGE_DIR)).replace(os.sep, "/")
    path = submit_dir / ("submit_stage16n_fixed_%s.pbs" % name.lower())
    lines = [
        "#!/bin/bash",
        "#PBS -N s16n_%s" % name.lower(),
        "#PBS -l select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb",
        "#PBS -l walltime=24:00:00",
        "#PBS -q teachingq",
        "#PBS -j oe",
        "#PBS -m abe",
        "#PBS -M pr21vyci@mailserver.tu-freiberg.de",
        "",
        "set -euo pipefail",
        "REPO_ROOT=\"${REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}\"",
        "cd \"$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/%s\"" % rel_case,
        "export ABAQUS_CPUS=16",
        "export ABAQUS_MP_MODE=threads",
        "export LOG_DIR=_logs",
        "bash ../../../run_stage16n_fixed_jump_cases_hpc.sh %s" % job,
        "",
    ]
    path.write_text("\n".join(lines))
    return path


def prepare_case(spec):
    name = spec["name"]
    base_cycle = spec["base_cycle"]
    jump_target_cycle = spec["jump_target_cycle"]
    compare_cycle = spec["compare_cycle"]
    state_csv = STATE_DIR / ("stage16n_exact_state_cycle%04d.csv" % base_cycle)
    state_bin = STATE_DIR / ("stage16n_exact_state_cycle%04d.bin" % base_cycle)
    if not state_csv.exists() or not state_bin.exists():
        raise RuntimeError(
            "Missing base exact state for cycle %d. Run stage16n_extract_exact_state_for_reinjection.py first."
            % base_cycle
        )

    case_dir = CASES_DIR / name
    case_dir.mkdir(parents=True, exist_ok=True)
    job = "stage16n_fixed_%s" % name.lower()
    shutil.copy2(state_csv, case_dir / "state.csv")
    shutil.copy2(state_bin, case_dir / "state.bin")
    umat = write_case_umat(case_dir, "state.csv")
    mesh = write_deck(case_dir / (job + ".inp"), job, base_cycle, jump_target_cycle, compare_cycle)
    submit = write_submit_script(case_dir, job, name)

    manifest = [
        "# Stage 16N-C Fixed State-Initialized Jump Case",
        "",
        "- Case: `%s`" % name,
        "- Job: `%s`" % job,
        "- Base cycle state: `%d`" % base_cycle,
        "- Interpreted jump target cycle: `%d`" % jump_target_cycle,
        "- Compare cycle: `%d`" % compare_cycle,
        "- Skipped cycles: `%d`" % (jump_target_cycle - base_cycle),
        "- Continued cycles in Abaqus deck: `%d`" % (compare_cycle - jump_target_cycle),
        "- State strategy: `%s`" % spec["state_strategy"],
        "- Source state CSV: `%s`" % state_csv.name,
        "- Source state binary: `%s`" % state_bin.name,
        "- UMAT with reader hooks: `%s`" % umat.name,
        "- PBS submit script: `%s`" % submit.name,
        "- Nodes: `%d`" % len(mesh["nodes"]),
        "- Elements: `%d`" % len(mesh["elements"]),
        "- Hole-ring elements: `%d`" % len(mesh["hole_ring"]),
        "- Production policy: `1 MPI rank x 16 OpenMP threads`",
        "",
        "This case intentionally measures a conservative zero-order fixed jump. It does not claim an exact restart or a high-order state extrapolation.",
    ]
    (case_dir / "STAGE16N_FIXED_JUMP_CASE_MANIFEST.md").write_text("\n".join(manifest) + "\n")
    print("Prepared %s" % case_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="all", help="all or comma-separated case names")
    args = parser.parse_args()
    selected = None
    if args.cases != "all":
        selected = set(part.strip() for part in args.cases.split(",") if part.strip())
    for spec in CASES:
        if selected is not None and spec["name"] not in selected:
            continue
        prepare_case(spec)


if __name__ == "__main__":
    main()
