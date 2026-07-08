#!/usr/bin/env python3
"""Prepare Stage 16N-B0 cycle-100 initialization-only audit case."""

from __future__ import print_function

import os
import shutil
from pathlib import Path

from prepare_stage16_plate_with_hole_model import chunks, make_mesh
from prepare_stage16n_neml_plate_with_hole_1000cycles import PARAMS
from stage16n_prepare_exact_reinjection_cases import strip_empty_hooks


STAGE_DIR = Path(__file__).resolve().parent
OUT_DIR = STAGE_DIR / "stage16n_exact_reinjection" / "cases" / "B0_AUDIT_100_INITIALIZATION_ONLY"
STATE_DIR = STAGE_DIR / "stage16n_exact_reinjection" / "state"
BASE_UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
READER = STAGE_DIR / "stage16n_sdvini_sigini_state_reader.for"
JOB = "stage16n_b0_audit_100_initialization_only"


def write_set(lines, keyword, values):
    lines.append(keyword)
    for chunk in chunks(values):
        lines.append(", ".join(str(v) for v in chunk))


def write_case_umat():
    base = strip_empty_hooks(BASE_UMAT.read_text())
    hooks = READER.read_text().replace("__STATE_FILE__", "state.csv")
    path = OUT_DIR / "stage16n_sdvini_sigini_state_reader.for"
    path.write_text(base + hooks + "\n")
    return path


def write_deck():
    mesh = make_mesh(20.0, 10.0, 1.0, 1.0, 0.25, 0.25)
    lines = [
        "** Stage 16N-B0 initialization-only audit",
        "** Exact cycle 100 stress/STATEV injection, no cyclic continuation",
        "*HEADING",
        "Stage 16N-B0 audit exact cycle 100 initialization only",
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
    ])
    lines.extend([
        "*INITIAL CONDITIONS, TYPE=SOLUTION, USER",
        "*INITIAL CONDITIONS, TYPE=STRESS, USER",
        "*STEP, NAME=CYCLE_0100, NLGEOM=NO, INC=80",
        "*STATIC",
        "1.0E-09, 1.0E-06, 1.0E-12, 1.0E-06",
        "*BOUNDARY",
        "LEFT_EDGE, 1, 1, 0.0",
        "ANCHOR_A, 2, 3, 0.0",
        "ANCHOR_B, 3, 3, 0.0",
        "RIGHT_EDGE, 1, 1, 0.0",
        "*OUTPUT, FIELD, NUMBER INTERVAL=1",
        "*NODE OUTPUT",
        "U, RF",
        "*ELEMENT OUTPUT",
        "S, SDV",
        "*OUTPUT, HISTORY, FREQUENCY=1",
        "*NODE OUTPUT, NSET=RIGHT_EDGE",
        "U1, RF1",
        "*END STEP",
    ])
    path = OUT_DIR / (JOB + ".inp")
    path.write_text("\n".join(lines) + "\n")
    return path, mesh


def write_submit_script():
    submit_dir = STAGE_DIR / "stage16n_exact_reinjection" / "submits"
    submit_dir.mkdir(parents=True, exist_ok=True)
    rel_case = os.path.relpath(str(OUT_DIR), str(STAGE_DIR)).replace(os.sep, "/")
    path = submit_dir / "submit_stage16n_b0_audit_100_initialization_only.pbs"
    lines = [
        "#!/bin/bash",
        "#PBS -N s16n_b0_audit100",
        "#PBS -l select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb",
        "#PBS -l walltime=03:00:00",
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
        "bash ../../../run_stage16n_b0_initialization_audit_hpc.sh %s" % JOB,
        "",
    ]
    path.write_text("\n".join(lines))
    return path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    state_csv = STATE_DIR / "stage16n_exact_state_cycle0100.csv"
    state_bin = STATE_DIR / "stage16n_exact_state_cycle0100.bin"
    if not state_csv.exists() or not state_bin.exists():
        raise RuntimeError("Missing cycle-100 extracted state files. Run exact-state extraction first.")
    shutil.copy2(state_csv, OUT_DIR / "state.csv")
    shutil.copy2(state_bin, OUT_DIR / "state.bin")
    umat = write_case_umat()
    deck, mesh = write_deck()
    submit = write_submit_script()
    manifest = [
        "# Stage 16N-B0 Initialization-Only Audit Manifest",
        "",
        "- Case: `B0_AUDIT_100_INITIALIZATION_ONLY`",
        "- Job: `%s`" % JOB,
        "- Injected state: exact reference cycle 100",
        "- Purpose: determine whether local SDV8 mismatch exists immediately after initialization/equilibration",
        "- Deck: `%s`" % deck.name,
        "- UMAT/reader: `%s`" % umat.name,
        "- Submit script: `%s`" % submit.name,
        "- Nodes: `%d`" % len(mesh["nodes"]),
        "- Elements: `%d`" % len(mesh["elements"]),
        "- Hole-ring elements: `%d`" % len(mesh["hole_ring"]),
        "- Mail policy: `#PBS -m abe`, `#PBS -M pr21vyci@mailserver.tu-freiberg.de`",
    ]
    (OUT_DIR / "STAGE16N_B0_AUDIT_100_MANIFEST.md").write_text("\n".join(manifest) + "\n")
    print("Prepared %s" % OUT_DIR)
    print("Submit script: %s" % submit)


if __name__ == "__main__":
    main()
