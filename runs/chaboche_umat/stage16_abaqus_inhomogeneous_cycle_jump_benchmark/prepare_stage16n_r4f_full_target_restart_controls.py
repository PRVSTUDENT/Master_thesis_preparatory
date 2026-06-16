#!/usr/bin/env python3
"""Prepare Stage 16N-R4F full-target native restart controls.

R4F tests whether the R4E/R4J mismatch is caused by material-only overwrite.
Each case first solves a short native restart source to the target jump cycle,
then restarts Abaqus from that newly generated target restart state and solves
the remaining cycles with no SDVINI/SIGINI and no UMAT overwrite.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
CONTROL_DIR = STAGE_DIR / "stage16n_restart_control"
R4F_DIR = CONTROL_DIR / "full_target_restart_cases"
SOURCE_R1A = CONTROL_DIR / "R1A_restart_reference_500cycles"
UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
EXTRACTOR = STAGE_DIR / "stage16n_extract_hysteresis_and_local_states.py"
COMPARE = STAGE_DIR / "stage16n_compare_r3j_jump_against_reference.py"
PARALLEL_REF = STAGE_DIR / "stage16n_parallel_max_reference"


@dataclass(frozen=True)
class FullTargetRestartCase:
    case_id: str
    source_job: str
    continuation_job: str
    oldjob: str
    source_dir: Path
    checkpoint_cycle: int
    target_restart_cycle: int
    final_cycle: int
    ref_metrics: Path
    ref_local_states: Path

    @property
    def run_dir(self) -> Path:
        return R4F_DIR / self.case_id

    @property
    def first_continuation_cycle(self) -> int:
        return self.target_restart_cycle + 1


CASES = (
    FullTargetRestartCase(
        case_id="R4F1_250_to_280_fullrestart_solve_281_to_500",
        source_job="stage16n_r4f1_source_250_to_280",
        continuation_job="stage16n_r4f1_fullrestart_280_solve_281_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        checkpoint_cycle=250,
        target_restart_cycle=280,
        final_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
    ),
    FullTargetRestartCase(
        case_id="R4F2_500_to_505_fullrestart_solve_506_to_750",
        source_job="stage16n_r4f2_source_500_to_505",
        continuation_job="stage16n_r4f2_fullrestart_505_solve_506_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        checkpoint_cycle=500,
        target_restart_cycle=505,
        final_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
    ),
)


def parse_checkpoint_increment(sta_path: Path, checkpoint_cycle: int) -> int:
    if not sta_path.exists():
        raise FileNotFoundError(sta_path)
    last_inc: int | None = None
    for line in sta_path.read_text(errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            step = int(parts[0])
            inc = int(parts[1])
            if step == checkpoint_cycle:
                last_inc = inc
    if last_inc is None:
        raise RuntimeError(f"Could not find step {checkpoint_cycle} in {sta_path}")
    return last_inc


def write_source_deck(path: Path, case: FullTargetRestartCase, checkpoint_inc: int) -> None:
    lines = [
        f"** Stage 16N-R4F source restart solve: {case.case_id}",
        "** Generates the full mechanical/material Abaqus restart state at the target cycle.",
        "*HEADING",
        f"Stage 16N-R4F source {case.checkpoint_cycle} to {case.target_restart_cycle}",
        f"*RESTART, READ, STEP={case.checkpoint_cycle}, INC={checkpoint_inc}",
    ]
    for cycle in range(case.checkpoint_cycle + 1, case.target_restart_cycle + 1):
        lines.extend(
            [
                "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
                "*STATIC",
                "0.005, 1.0, 1.0E-08, 0.025",
            ]
        )
        if cycle == case.target_restart_cycle:
            lines.append("*RESTART, WRITE, FREQUENCY=1")
        lines.extend(
            [
                "*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE",
                "RIGHT_EDGE, 1, 1, 0.10",
                "*OUTPUT, HISTORY, FREQUENCY=1",
                "*NODE OUTPUT, NSET=RIGHT_EDGE",
                "U1, RF1",
            ]
        )
        if cycle == case.target_restart_cycle:
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
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_link_script(path: Path, case: FullTargetRestartCase) -> None:
    rel_source = Path("..") / ".." / case.source_dir.name
    text = f"""#!/usr/bin/env bash
set -euo pipefail

DEFAULT_SOURCE_DIR="{rel_source.as_posix()}"
HPC_SOURCE_DIR="/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"
OLDJOB="{case.oldjob}"

SOURCE_DIR="${{RESTART_SOURCE_DIR:-$DEFAULT_SOURCE_DIR}}"
if [[ ! -e "${{SOURCE_DIR}}/${{OLDJOB}}.odb" && -e "${{HPC_SOURCE_DIR}}/${{OLDJOB}}.odb" ]]; then
  SOURCE_DIR="$HPC_SOURCE_DIR"
fi

echo "Linking base restart sources from: $SOURCE_DIR"
for ext in odb res stt mdl sim prt; do
  src="${{SOURCE_DIR}}/${{OLDJOB}}.${{ext}}"
  dst="${{OLDJOB}}.${{ext}}"
  if [[ ! -e "$src" ]]; then
    echo "Missing base restart source: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_runner(path: Path, case: FullTargetRestartCase) -> None:
    ref_metrics = case.ref_metrics.relative_to(STAGE_DIR).as_posix()
    ref_local_states = case.ref_local_states.relative_to(STAGE_DIR).as_posix()
    text = f"""#!/usr/bin/env bash
set -euo pipefail

SOURCE_JOB="{case.source_job}"
CONT_JOB="{case.continuation_job}"
OLDJOB="{case.oldjob}"
CHECKPOINT_CYCLE="{case.checkpoint_cycle}"
TARGET_RESTART_CYCLE="{case.target_restart_cycle}"
FIRST_CONT_CYCLE="{case.first_continuation_cycle}"
FINAL_CYCLE="{case.final_cycle}"

ABAQUS_CPUS="${{ABAQUS_CPUS:-16}}"
ABAQUS_MP_MODE="${{ABAQUS_MP_MODE:-threads}}"
LOG_DIR="${{LOG_DIR:-_logs}}"
ABAQUS_SCRATCH="${{PBS_JOBDIR:-$PWD/_abaqus_scratch}}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4F] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4F] PBS job: ${{PBS_JOBID:-manual}}"
echo "[Stage16N-R4F] source solve: $SOURCE_JOB ($CHECKPOINT_CYCLE -> $TARGET_RESTART_CYCLE)"
echo "[Stage16N-R4F] continuation: $CONT_JOB ($FIRST_CONT_CYCLE -> $FINAL_CYCLE)"
echo "[Stage16N-R4F] no UMAT overwrite; full Abaqus target restart is used"
echo "[Stage16N-R4F] scratch=$ABAQUS_SCRATCH"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${{OLDJOB}}.${{ext}}" ]]; then
    echo "Missing base native restart source: ${{OLDJOB}}.${{ext}}" >&2
    exit 2
  fi
done

if [[ ! -f "${{SOURCE_JOB}}.odb" ]]; then
  abaqus job="$SOURCE_JOB" input="${{SOURCE_JOB}}.inp" oldjob="$OLDJOB" \\
    user=stage16n_neml_equivalent_chaboche_umat.for \\
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
    2>&1 | tee "$LOG_DIR/${{SOURCE_JOB}}.log"
fi

if [[ ! -f "${{SOURCE_JOB}}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${{SOURCE_JOB}}.sta"; then
  echo "Source solve did not complete successfully; check $SOURCE_JOB.sta" >&2
  exit 2
fi

target_inc="$(awk -v step="$TARGET_RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {{inc=$2}} END {{if (inc == "") exit 3; print inc}}' "${{SOURCE_JOB}}.sta")"
echo "[Stage16N-R4F] restart read target: STEP=$TARGET_RESTART_CYCLE INC=$target_inc"

cat > "${{CONT_JOB}}.inp" <<EOF
** Stage 16N-R4F continuation: {case.case_id}
** Full native restart from target cycle; no SDVINI/SIGINI and no UMAT overwrite.
*HEADING
Stage 16N-R4F continuation {case.target_restart_cycle} to {case.final_cycle}
*RESTART, READ, STEP=${{TARGET_RESTART_CYCLE}}, INC=${{target_inc}}
EOF

for cycle in $(seq "$FIRST_CONT_CYCLE" "$FINAL_CYCLE"); do
  cat >> "${{CONT_JOB}}.inp" <<EOF
*STEP, NAME=CYCLE_$(printf '%04d' "$cycle"), NLGEOM=NO, INC=160
*STATIC
0.005, 1.0, 1.0E-08, 0.025
*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE
RIGHT_EDGE, 1, 1, 0.10
*OUTPUT, HISTORY, FREQUENCY=1
*NODE OUTPUT, NSET=RIGHT_EDGE
U1, RF1
EOF
  if [[ "$cycle" = "$FINAL_CYCLE" ]]; then
    cat >> "${{CONT_JOB}}.inp" <<EOF
*OUTPUT, FIELD, NUMBER INTERVAL=4
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, SDV
EOF
  fi
  echo "*END STEP" >> "${{CONT_JOB}}.inp"
done

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${{SOURCE_JOB}}.${{ext}}" ]]; then
    echo "Missing generated target restart source: ${{SOURCE_JOB}}.${{ext}}" >&2
    exit 2
  fi
done

abaqus job="${{CONT_JOB}}_datacheck" input="${{CONT_JOB}}.inp" oldjob="$SOURCE_JOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{CONT_JOB}}_datacheck.log"

abaqus job="$CONT_JOB" input="${{CONT_JOB}}.inp" oldjob="$SOURCE_JOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{CONT_JOB}}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${{CONT_JOB}}.msg" \\
  | tee "$LOG_DIR/${{CONT_JOB}}_parallelism_check.log" || true

abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py --job "$CONT_JOB" \\
  2>&1 | tee "$LOG_DIR/${{CONT_JOB}}_extract.log"

cd "${{REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}}"
CASE_DIR="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/full_target_restart_cases/{case.case_id}"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_r3j_jump_against_reference.py \\
  --jump-metrics "$CASE_DIR/${{CONT_JOB}}_cycle_metrics.csv" \\
  --jump-local-states "$CASE_DIR/${{CONT_JOB}}_selected_cycle_local_states.csv" \\
  --ref-metrics "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/{ref_metrics}" \\
  --ref-local-states "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/{ref_local_states}" \\
  --cycles "$FINAL_CYCLE" \\
  --out-dir "$CASE_DIR" \\
  --prefix "$CONT_JOB" \\
  2>&1 | tee "$CASE_DIR/$LOG_DIR/${{CONT_JOB}}_compare.log"

cd "$CASE_DIR"
{{
  echo "# Stage 16N-R4F Full-Target Restart Case Status"
  echo
  echo "- PBS job: \\`${{PBS_JOBID:-manual}}\\`"
  echo "- Base oldjob: \\`$OLDJOB\\`"
  echo "- Source solve: \\`$SOURCE_JOB\\`, cycles \\`$((CHECKPOINT_CYCLE + 1)) -> $TARGET_RESTART_CYCLE\\`"
  echo "- Continuation solve: \\`$CONT_JOB\\`, cycles \\`$FIRST_CONT_CYCLE -> $FINAL_CYCLE\\`"
  echo "- Restart read: \\`oldjob=$SOURCE_JOB, STEP=$TARGET_RESTART_CYCLE, INC=$target_inc\\`"
  echo "- UMAT overwrite: \\`none\\`"
  if [[ -f "${{SOURCE_JOB}}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${{SOURCE_JOB}}.sta"; then
    echo "- Source solver status: \\`completed_successfully\\`"
  else
    echo "- Source solver status: \\`check $SOURCE_JOB.sta\\`"
  fi
  if [[ -f "${{CONT_JOB}}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${{CONT_JOB}}.sta"; then
    echo "- Continuation solver status: \\`completed_successfully\\`"
  else
    echo "- Continuation solver status: \\`check $CONT_JOB.sta\\`"
  fi
  if [[ -f "${{CONT_JOB}}_comparison_summary.csv" ]]; then
    tail -n +2 "${{CONT_JOB}}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \\`$(date '+%Y-%m-%d %H:%M:%S')\\`"
}} > STAGE16N_R4F_CASE_STATUS.md

echo "[Stage16N-R4F] end: $(date '+%Y-%m-%d %H:%M:%S')"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_pbs(path: Path, case: FullTargetRestartCase) -> None:
    text = f"""#!/bin/bash
#PBS -N {case.continuation_job}
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

RUN_DIR="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/full_target_restart_cases/{case.case_id}"
cd "$RUN_DIR"
bash link_restart_sources.sh
bash run_stage16n_r4f_full_target_restart_hpc.sh
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_dispatcher(path: Path) -> None:
    text = r"""#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R4F1_250_to_280_fullrestart_solve_281_to_500|R4F2_500_to_505_fullrestart_solve_506_to_750>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="${SCRIPT_DIR}/stage16n_restart_control/full_target_restart_cases/${CASE_ID}"
MANIFEST="${SCRIPT_DIR}/stage16n_restart_control/full_target_restart_cases/stage16n_r4f_full_target_restart_cases.csv"

if [[ ! -d "$CASE_DIR" ]]; then
  echo "Unknown case directory: $CASE_DIR" >&2
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing manifest: $MANIFEST" >&2
  exit 2
fi

pbs_script="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $11}' "$MANIFEST")"
if [[ -z "$pbs_script" ]]; then
  echo "Case not found in manifest: $CASE_ID" >&2
  exit 2
fi

cd "$CASE_DIR"
qsub "$pbs_script"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def prepare_cases(cases: tuple[FullTargetRestartCase, ...]) -> None:
    R4F_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    dispatcher = STAGE_DIR / "submit_stage16n_r4f_full_target_restart_case.sh"
    write_dispatcher(dispatcher)
    dispatcher.chmod(0o755)

    for case in cases:
        case.run_dir.mkdir(parents=True, exist_ok=True)
        source_sta = case.source_dir / f"{case.oldjob}.sta"
        checkpoint_inc = parse_checkpoint_increment(source_sta, case.checkpoint_cycle)

        source_inp = case.run_dir / f"{case.source_job}.inp"
        runner = case.run_dir / "run_stage16n_r4f_full_target_restart_hpc.sh"
        pbs = case.run_dir / f"submit_{case.continuation_job}.pbs"
        link_script = case.run_dir / "link_restart_sources.sh"

        write_source_deck(source_inp, case, checkpoint_inc)
        write_runner(runner, case)
        write_pbs(pbs, case)
        write_link_script(link_script, case)
        runner.chmod(0o755)
        pbs.chmod(0o755)
        link_script.chmod(0o755)

        for src in (UMAT, EXTRACTOR, COMPARE):
            shutil.copy2(src, case.run_dir / src.name)

        rows.append(
            {
                "case_id": case.case_id,
                "source_job": case.source_job,
                "continuation_job": case.continuation_job,
                "oldjob": case.oldjob,
                "checkpoint_cycle": str(case.checkpoint_cycle),
                "target_restart_cycle": str(case.target_restart_cycle),
                "first_continuation_cycle": str(case.first_continuation_cycle),
                "final_cycle": str(case.final_cycle),
                "checkpoint_inc": str(checkpoint_inc),
                "runner": runner.name,
                "pbs": pbs.name,
            }
        )

    manifest = R4F_DIR / "stage16n_r4f_full_target_restart_cases.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "case_id",
            "source_job",
            "continuation_job",
            "oldjob",
            "checkpoint_cycle",
            "target_restart_cycle",
            "first_continuation_cycle",
            "final_cycle",
            "checkpoint_inc",
            "runner",
            "pbs",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=["all", "R4F1", "R4F2"], default="all")
    args = parser.parse_args()
    if args.case == "R4F1":
        selected = (CASES[0],)
    elif args.case == "R4F2":
        selected = (CASES[1],)
    else:
        selected = CASES
    prepare_cases(selected)


if __name__ == "__main__":
    main()
