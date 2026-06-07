#!/usr/bin/env python3
"""Prepare Stage 16N-R1 restart-enabled reference decks and PBS scripts.

The generated jobs are ordinary no-jump Abaqus references with native restart
output enabled at selected cycle steps. They are the control source for later
restart-preserved cycle-jump work; no UMAT memory overwrite is introduced here.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

from prepare_stage16_plate_with_hole_model import chunks, make_mesh


STAGE_DIR = Path(__file__).resolve().parent
OUT_DIR = STAGE_DIR / "stage16n_restart_control"
UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
EXTRACTOR = STAGE_DIR / "stage16n_extract_hysteresis_and_local_states.py"

PARAMS = {
    "E": 200000.0,
    "nu": 0.3,
    "yield": 100.0,
    "Q": 50.0,
    "b": 5.0,
    "C1": 80000.0,
    "g1": 900.0,
    "C2": 14000.0,
    "g2": 1500.0,
    "C3": 3333.0,
    "g3": 1.0,
}

BASE_SELECTED_FIELD_CYCLES = [1, 2, 10, 50, 100, 250, 500]


@dataclass(frozen=True)
class RestartReferenceCase:
    case_id: str
    job: str
    target_cycle: int
    checkpoint_cycles: tuple[int, ...]

    @property
    def run_dir(self) -> Path:
        return OUT_DIR / self.case_id


CASES = (
    RestartReferenceCase(
        case_id="R1B_restart_reference_250cycles",
        job="stage16n_r1b_restart_ref_250cycles",
        target_cycle=250,
        checkpoint_cycles=(100, 250),
    ),
    RestartReferenceCase(
        case_id="R1A_restart_reference_500cycles",
        job="stage16n_r1a_restart_ref_500cycles",
        target_cycle=500,
        checkpoint_cycles=(100, 250, 500),
    ),
)


def write_set(lines: list[str], keyword: str, values: list[int]) -> None:
    lines.append(keyword)
    for chunk in chunks(values):
        lines.append(", ".join(str(v) for v in chunk))


def selected_cycles(target_cycle: int, checkpoint_cycles: tuple[int, ...]) -> set[int]:
    return {cycle for cycle in BASE_SELECTED_FIELD_CYCLES + list(checkpoint_cycles) if cycle <= target_cycle}


def write_deck(path: Path, case: RestartReferenceCase) -> dict[str, object]:
    mesh = make_mesh(20.0, 10.0, 1.0, 1.0, 0.25, 0.25)
    lines = [
        f"** Stage 16N-R1 {case.target_cycle}-cycle restart-enabled reference",
        "** Structured C3D8 mesh with element-wise approximation of central circular hole",
        "*HEADING",
        f"Stage 16N-R1 {case.target_cycle}-cycle restart-enabled reference",
        "*PART, NAME=PLATE_HOLE",
        "*NODE",
    ]
    for nid, x, y, z in mesh["nodes"]:
        lines.append("%d, %.8g, %.8g, %.8g" % (nid, x, y, z))
    lines.append("*ELEMENT, TYPE=C3D8, ELSET=PLATE_ALL")
    for elem in mesh["elements"]:
        lines.append(", ".join(str(v) for v in elem))
    write_set(lines, "*ELSET, ELSET=HOLE_RING", mesh["hole_ring"])
    lines.extend(
        [
            "*SOLID SECTION, ELSET=PLATE_ALL, MATERIAL=NEML_EQUIV_CHABOCHE",
            "*END PART",
            "*ASSEMBLY, NAME=ASSEMBLY",
            "*INSTANCE, NAME=PLATE_INST, PART=PLATE_HOLE",
            "*END INSTANCE",
        ]
    )
    write_set(lines, "*NSET, NSET=LEFT_EDGE, INSTANCE=PLATE_INST", mesh["left_nodes"])
    write_set(lines, "*NSET, NSET=RIGHT_EDGE, INSTANCE=PLATE_INST", mesh["right_nodes"])
    lines.extend(
        [
            "*NSET, NSET=ANCHOR_A, INSTANCE=PLATE_INST",
            str(mesh["anchor_a"]),
            "*NSET, NSET=ANCHOR_B, INSTANCE=PLATE_INST",
            str(mesh["anchor_b"]),
            "*ELSET, ELSET=HOLE_RING, INSTANCE=PLATE_INST",
        ]
    )
    for chunk in chunks(mesh["hole_ring"]):
        lines.append(", ".join(str(v) for v in chunk))
    lines.extend(
        [
            "*END ASSEMBLY",
            "*MATERIAL, NAME=NEML_EQUIV_CHABOCHE",
            "*DEPVAR",
            "27",
            "*USER MATERIAL, CONSTANTS=11",
            "{E}, {nu}, {yield}, {Q}, {b}, {C1}, {g1}, {C2}, {g2}, {C3}, {g3}".format(**PARAMS),
            "*AMPLITUDE, NAME=AMP_ONE_CYCLE, DEFINITION=TABULAR",
            "0.00, 0.0",
            "0.25, 1.0",
            "0.50, 0.0",
            "0.75, -1.0",
            "1.00, 0.0",
        ]
    )

    selected = selected_cycles(case.target_cycle, case.checkpoint_cycles)
    checkpoint_set = set(case.checkpoint_cycles)
    for cycle in range(1, case.target_cycle + 1):
        lines.extend(
            [
                "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
                "*STATIC",
                "0.005, 1.0, 1.0E-08, 0.025",
            ]
        )
        if cycle in checkpoint_set:
            lines.append("*RESTART, WRITE, FREQUENCY=1")
        if cycle == 1:
            lines.extend(
                [
                    "*BOUNDARY",
                    "LEFT_EDGE, 1, 1, 0.0",
                    "ANCHOR_A, 2, 3, 0.0",
                    "ANCHOR_B, 3, 3, 0.0",
                ]
            )
        lines.extend(
            [
                "*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE",
                "RIGHT_EDGE, 1, 1, 0.10",
                "*OUTPUT, HISTORY, FREQUENCY=1",
                "*NODE OUTPUT, NSET=RIGHT_EDGE",
                "U1, RF1",
            ]
        )
        if cycle in selected:
            lines.extend(
                [
                    "*OUTPUT, FIELD, NUMBER INTERVAL=4",
                    "*NODE OUTPUT",
                    "U, RF",
                    "*ELEMENT OUTPUT",
                    "S, SDV",
                ]
            )
        lines.append("*END STEP")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return mesh


def write_runner(path: Path) -> None:
    text = (
        r"""#!/usr/bin/env bash
set -euo pipefail

JOB="${1:-}"
if [[ -z "$JOB" ]]; then
  echo "Usage: $0 <job-name>" >&2
  exit 2
fi

ABAQUS_CPUS="${ABAQUS_CPUS:-16}"
ABAQUS_MP_MODE="${ABAQUS_MP_MODE:-threads}"
LOG_DIR="${LOG_DIR:-_logs}"
mkdir -p "$LOG_DIR"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R1] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R1] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R1] Abaqus job: ${JOB}"
echo "[Stage16N-R1] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

if [[ ! -f "${JOB}.inp" ]]; then
  echo "Missing input deck: ${JOB}.inp" >&2
  exit 2
fi
if [[ ! -f "stage16n_neml_equivalent_chaboche_umat.for" ]]; then
  echo "Missing UMAT: stage16n_neml_equivalent_chaboche_umat.for" >&2
  exit 2
fi

abaqus job="${JOB}_datacheck" input="${JOB}.inp" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}_datacheck.log"

abaqus job="${JOB}" input="${JOB}.inp" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "${LOG_DIR}/${JOB}_parallelism_check.log" || true

if [[ -f "${JOB}.odb" && -f "stage16n_extract_hysteresis_and_local_states.py" ]]; then
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "${JOB}" \
    2>&1 | tee "${LOG_DIR}/${JOB}_extract.log" || true
fi

{
  echo "# Stage 16N-R1 Restart Reference Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`${JOB}\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  if [[ -f "${JOB}.sta" ]]; then
    if grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
      echo "- Solver status: \`completed\`"
    else
      echo "- Solver status: \`check ${JOB}.sta\`"
    fi
  fi
  echo "- Restart files:"
  find . -maxdepth 1 -type f \\( -name "${JOB}.res" -o -name "${JOB}.stt" -o -name "${JOB}.mdl" -o -name "${JOB}.sim" \\) -printf "  - \`%f\`\\n" | sort
} > "STAGE16N_R1_RESTART_REFERENCE_STATUS.md"

echo "[Stage16N-R1] end: $(date '+%Y-%m-%d %H:%M:%S')"
"""
    )
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_pbs(path: Path, case: RestartReferenceCase) -> None:
    path.write_text(
        f"""#!/bin/bash
#PBS -N {case.job}
#PBS -q entry_teachingq
#PBS -l select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
#PBS -l walltime=24:00:00
#PBS -j oe
#PBS -m abe
#PBS -M pr21vyci@mailserver.tu-freiberg.de

set -euo pipefail

cd "$PBS_O_WORKDIR"
export REPO_ROOT="$HOME/master_thesis/Abaqus_trial"
export ABAQUS_CPUS=16
export ABAQUS_MP_MODE=threads

RUN_DIR="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/{case.case_id}"
cd "$RUN_DIR"
bash run_stage16n_r1_restart_reference_hpc.sh {case.job}
""",
        encoding="utf-8",
        newline="\n",
    )


def write_manifest(cases: tuple[RestartReferenceCase, ...]) -> None:
    lines = [
        "# Stage 16N-R1 Restart-Control Manifest",
        "",
        "Generated restart-enabled no-jump references for native Abaqus restart testing.",
        "",
        "| Case | Job | Target cycle | Restart checkpoints |",
        "|---|---|---:|---|",
    ]
    for case in cases:
        checkpoints = ", ".join(str(c) for c in case.checkpoint_cycles)
        lines.append(f"| `{case.case_id}` | `{case.job}` | {case.target_cycle} | {checkpoints} |")
    lines.extend(
        [
            "",
            "Resource policy for each PBS job:",
            "",
            "- `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`",
            "- `walltime=24:00:00`",
            "- Abaqus `cpus=16 mp_mode=threads`",
            "",
            "These jobs do not perform UMAT overwrite or manual SDVINI/SIGINI reinjection.",
            "They only create FE-consistent native Abaqus restart sources.",
            "",
        ]
    )
    (OUT_DIR / "STAGE16N_R1_RESTART_CONTROL_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")


def prepare_cases(cases: tuple[RestartReferenceCase, ...]) -> None:
    if not UMAT.exists():
        raise FileNotFoundError(UMAT)
    if not EXTRACTOR.exists():
        raise FileNotFoundError(EXTRACTOR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for case in cases:
        case.run_dir.mkdir(parents=True, exist_ok=True)
        write_deck(case.run_dir / f"{case.job}.inp", case)
        shutil.copy2(UMAT, case.run_dir / "stage16n_neml_equivalent_chaboche_umat.for")
        shutil.copy2(EXTRACTOR, case.run_dir / "stage16n_extract_hysteresis_and_local_states.py")
        write_runner(case.run_dir / "run_stage16n_r1_restart_reference_hpc.sh")
        write_pbs(case.run_dir / f"submit_{case.job}.pbs", case)
        case_manifest = [
            f"# {case.case_id}",
            "",
            f"- Abaqus job: `{case.job}`",
            f"- Target cycle: `{case.target_cycle}`",
            f"- Restart checkpoints requested in cycle steps: `{', '.join(str(c) for c in case.checkpoint_cycles)}`",
            "- Restart keyword: `*RESTART, WRITE, FREQUENCY=1` inside checkpoint cycle steps",
            "- Purpose: generate native Abaqus restart files before any restart-preserved UMAT overwrite.",
            "",
        ]
        (case.run_dir / "STAGE16N_R1_CASE_MANIFEST.md").write_text("\n".join(case_manifest), encoding="utf-8")
        print(f"Wrote {case.run_dir / (case.job + '.inp')}")
        print(f"Wrote {case.run_dir / ('submit_' + case.job + '.pbs')}")
    write_manifest(cases)
    print(f"Wrote {OUT_DIR / 'STAGE16N_R1_RESTART_CONTROL_MANIFEST.md'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        choices=["all", "R1A", "R1B"],
        default="all",
        help="Case set to prepare. R1A is 500 cycles; R1B is 250 cycles.",
    )
    args = parser.parse_args()
    if args.case == "R1A":
        cases = (CASES[1],)
    elif args.case == "R1B":
        cases = (CASES[0],)
    else:
        cases = CASES
    prepare_cases(cases)


if __name__ == "__main__":
    main()
