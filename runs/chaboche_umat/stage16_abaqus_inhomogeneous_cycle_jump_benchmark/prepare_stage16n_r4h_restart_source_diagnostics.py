#!/usr/bin/env python3
"""Prepare Stage 16N-R4H restart-source diagnostic controls."""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
CONTROL_DIR = STAGE_DIR / "stage16n_restart_control"
R4H_DIR = CONTROL_DIR / "r4h_restart_source_diagnostics"
R1A_DIR = CONTROL_DIR / "R1A_restart_reference_500cycles"
R4G_DIR = CONTROL_DIR / "r4g_native_replay_cases"
UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
EXTRACTOR = STAGE_DIR / "stage16n_extract_hysteresis_and_local_states.py"
COMPARE = STAGE_DIR / "stage16n_compare_r3j_jump_against_reference.py"
REF500_METRICS = STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv"
REF500_LOCAL = STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv"
REF750_METRICS = STAGE_DIR / "stage16n_parallel_max_reference" / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
REF750_LOCAL = STAGE_DIR / "stage16n_parallel_max_reference" / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"


@dataclass(frozen=True)
class R4HCase:
    case_id: str
    job: str
    mode: str
    base_oldjob: str
    base_source_dir: Path
    checkpoint_cycle: int
    source_end_cycle: int
    restart_cycle: int
    final_cycle: int
    ref_metrics: Path
    ref_local_states: Path
    purpose: str

    @property
    def run_dir(self) -> Path:
        return R4H_DIR / self.case_id

    @property
    def first_solved_cycle(self) -> int:
        return self.restart_cycle + 1

    @property
    def source_job(self) -> str:
        return f"{self.job}_source_{self.checkpoint_cycle}_to_{self.source_end_cycle}"

    @property
    def continuation_oldjob(self) -> str:
        return self.source_job if self.mode == "interior_source_split" else self.base_oldjob


CASES = (
    R4HCase(
        case_id="R4H1_long_replay_280_to_500",
        job="stage16n_r4h1_long_replay_280_to_500",
        mode="long_replay_restart",
        base_oldjob="stage16n_r4g1_direct_250_to_500",
        base_source_dir=R4G_DIR / "R4G1_direct_250_to_500",
        checkpoint_cycle=280,
        source_end_cycle=280,
        restart_cycle=280,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="restart at cycle 280 from long direct replay R4G1, then solve 281--500",
    ),
    R4HCase(
        case_id="R4H2_source_250_to_281_restart_280_to_500",
        job="stage16n_r4h2_source_250_to_281_restart_280_to_500",
        mode="interior_source_split",
        base_oldjob="stage16n_r1a_restart_ref_500cycles",
        base_source_dir=R1A_DIR,
        checkpoint_cycle=250,
        source_end_cycle=281,
        restart_cycle=280,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="source solve 250--281, restart from interior cycle 280, then solve 281--500",
    ),
    R4HCase(
        case_id="R4H3_long_replay_270_to_500",
        job="stage16n_r4h3_long_replay_270_to_500",
        mode="long_replay_restart",
        base_oldjob="stage16n_r4g1_direct_250_to_500",
        base_source_dir=R4G_DIR / "R4G1_direct_250_to_500",
        checkpoint_cycle=270,
        source_end_cycle=270,
        restart_cycle=270,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="restart at cycle 270 from long direct replay R4G1, then solve 271--500",
    ),
    R4HCase(
        case_id="R4H4_source_250_to_271_restart_270_to_500",
        job="stage16n_r4h4_source_250_to_271_restart_270_to_500",
        mode="interior_source_split",
        base_oldjob="stage16n_r1a_restart_ref_500cycles",
        base_source_dir=R1A_DIR,
        checkpoint_cycle=250,
        source_end_cycle=271,
        restart_cycle=270,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="source solve 250--271, restart from interior cycle 270, then solve 271--500",
    ),
    R4HCase(
        case_id="R4H5_long_replay_505_to_750",
        job="stage16n_r4h5_long_replay_505_to_750",
        mode="long_replay_restart",
        base_oldjob="stage16n_r4g6_direct_500_to_750",
        base_source_dir=R4G_DIR / "R4G6_direct_500_to_750",
        checkpoint_cycle=505,
        source_end_cycle=505,
        restart_cycle=505,
        final_cycle=750,
        ref_metrics=REF750_METRICS,
        ref_local_states=REF750_LOCAL,
        purpose="restart at cycle 505 from long direct replay R4G6, then solve 506--750",
    ),
    R4HCase(
        case_id="R4H6_source_500_to_506_restart_505_to_750",
        job="stage16n_r4h6_source_500_to_506_restart_505_to_750",
        mode="interior_source_split",
        base_oldjob="stage16n_r1a_restart_ref_500cycles",
        base_source_dir=R1A_DIR,
        checkpoint_cycle=500,
        source_end_cycle=506,
        restart_cycle=505,
        final_cycle=750,
        ref_metrics=REF750_METRICS,
        ref_local_states=REF750_LOCAL,
        purpose="source solve 500--506, restart from interior cycle 505, then solve 506--750",
    ),
)


def parse_checkpoint_increment(sta_path: Path, cycle: int) -> int:
    last_inc: int | None = None
    for line in sta_path.read_text(errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit() and int(parts[0]) == cycle:
            last_inc = int(parts[1])
    if last_inc is None:
        raise RuntimeError(f"Could not find step {cycle} in {sta_path}")
    return last_inc


def add_field_output(lines: list[str]) -> None:
    lines.extend(
        [
            "*OUTPUT, FIELD, NUMBER INTERVAL=4",
            "*NODE OUTPUT",
            "U, RF",
            "*ELEMENT OUTPUT",
            "S, SDV",
        ]
    )


def write_continuation_deck(path: Path, case: R4HCase, restart_inc_expr: str) -> None:
    lines = [
        f"** Stage 16N-R4H continuation: {case.case_id}",
        f"** Mode: {case.mode}.",
        f"** Purpose: {case.purpose}.",
        "*HEADING",
        f"Stage 16N-R4H {case.restart_cycle} to {case.final_cycle}",
        f"*RESTART, READ, STEP={case.restart_cycle}, INC={restart_inc_expr}",
    ]
    for cycle in range(case.first_solved_cycle, case.final_cycle + 1):
        lines.extend(
            [
                "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
                "*STATIC",
                "0.005, 1.0, 1.0E-08, 0.025",
                "*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE",
                "RIGHT_EDGE, 1, 1, 0.10",
                "*OUTPUT, HISTORY, FREQUENCY=1",
                "*NODE OUTPUT, NSET=RIGHT_EDGE",
                "U1, RF1",
            ]
        )
        if cycle == case.final_cycle:
            add_field_output(lines)
        lines.append("*END STEP")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_source_deck(path: Path, case: R4HCase, checkpoint_inc: int) -> None:
    lines = [
        f"** Stage 16N-R4H source split solve: {case.case_id}",
        "** Writes restart records through the interior target cycle.",
        "*HEADING",
        f"Stage 16N-R4H source {case.checkpoint_cycle} to {case.source_end_cycle}",
        f"*RESTART, READ, STEP={case.checkpoint_cycle}, INC={checkpoint_inc}",
    ]
    for cycle in range(case.checkpoint_cycle + 1, case.source_end_cycle + 1):
        lines.extend(
            [
                "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
                "*STATIC",
                "0.005, 1.0, 1.0E-08, 0.025",
                "*RESTART, WRITE, FREQUENCY=1",
                "*BOUNDARY, AMPLITUDE=AMP_ONE_CYCLE",
                "RIGHT_EDGE, 1, 1, 0.10",
                "*OUTPUT, HISTORY, FREQUENCY=1",
                "*NODE OUTPUT, NSET=RIGHT_EDGE",
                "U1, RF1",
            ]
        )
        if cycle in {case.restart_cycle, case.source_end_cycle}:
            add_field_output(lines)
        lines.append("*END STEP")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_link_script(path: Path, case: R4HCase) -> None:
    rel_source = Path("..") / ".." / case.base_source_dir.name
    if "R4G" in str(case.base_source_dir):
        rel_source = Path("..") / ".." / "r4g_native_replay_cases" / case.base_source_dir.name
    hpc_source = (
        "/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/"
        "stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/"
        + (
            f"r4g_native_replay_cases/{case.base_source_dir.name}"
            if "R4G" in str(case.base_source_dir)
            else "R1A_restart_reference_500cycles"
        )
    )
    text = f"""#!/usr/bin/env bash
set -euo pipefail

DEFAULT_SOURCE_DIR="{rel_source.as_posix()}"
HPC_SOURCE_DIR="{hpc_source}"
OLDJOB="{case.base_oldjob}"

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


def write_runner(path: Path, case: R4HCase) -> None:
    ref_metrics = case.ref_metrics.relative_to(STAGE_DIR).as_posix()
    ref_local = case.ref_local_states.relative_to(STAGE_DIR).as_posix()
    if case.mode == "interior_source_split":
        source_block = f"""
if [[ ! -f "{case.source_job}.odb" ]]; then
  abaqus job="{case.source_job}" input="{case.source_job}.inp" oldjob="$BASE_OLDJOB" \\
    user=stage16n_neml_equivalent_chaboche_umat.for \\
    interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
    cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
    2>&1 | tee "$LOG_DIR/{case.source_job}.log"
fi

if [[ ! -f "{case.source_job}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "{case.source_job}.sta"; then
  echo "Source split solve did not complete successfully; check {case.source_job}.sta" >&2
  exit 2
fi

RESTART_INC="$(awk -v step="$RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {{inc=$2}} END {{if (inc == "") exit 3; print inc}}' "{case.source_job}.sta")"
python3 - <<PY
from pathlib import Path
text = Path("{case.job}.inp").read_text()
Path("{case.job}.inp").write_text(text.replace("INC=__R4H_RESTART_INC__", "INC=" + "$RESTART_INC"))
PY

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "{case.source_job}" \\
  2>&1 | tee "$LOG_DIR/{case.source_job}_extract.log" || true
"""
    else:
        source_block = f'RESTART_INC="{parse_checkpoint_increment(case.base_source_dir / (case.base_oldjob + ".sta"), case.restart_cycle)}"\n'
    text = f"""#!/usr/bin/env bash
set -euo pipefail

JOB="{case.job}"
BASE_OLDJOB="{case.base_oldjob}"
OLDJOB="{case.continuation_oldjob}"
MODE="{case.mode}"
CHECKPOINT_CYCLE="{case.checkpoint_cycle}"
SOURCE_END_CYCLE="{case.source_end_cycle}"
RESTART_CYCLE="{case.restart_cycle}"
FIRST_SOLVED_CYCLE="{case.first_solved_cycle}"
FINAL_CYCLE="{case.final_cycle}"
PURPOSE="{case.purpose}"

ABAQUS_CPUS="${{ABAQUS_CPUS:-16}}"
ABAQUS_MP_MODE="${{ABAQUS_MP_MODE:-threads}}"
LOG_DIR="${{LOG_DIR:-_logs}}"
ABAQUS_SCRATCH="${{PBS_JOBDIR:-$PWD/_abaqus_scratch}}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4H] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4H] PBS job: ${{PBS_JOBID:-manual}}"
echo "[Stage16N-R4H] case: {case.case_id}"
echo "[Stage16N-R4H] mode: $MODE"
echo "[Stage16N-R4H] first solved cycle: $FIRST_SOLVED_CYCLE"
echo "[Stage16N-R4H] final cycle: $FINAL_CYCLE"
echo "[Stage16N-R4H] purpose: $PURPOSE"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${{BASE_OLDJOB}}.${{ext}}" ]]; then
    echo "Missing base native restart source: ${{BASE_OLDJOB}}.${{ext}}" >&2
    exit 2
  fi
done

{source_block}

if [[ "$MODE" = "interior_source_split" ]]; then
  for ext in odb res stt mdl sim prt; do
    if [[ ! -e "${{OLDJOB}}.${{ext}}" ]]; then
      echo "Missing generated split restart source: ${{OLDJOB}}.${{ext}}" >&2
      exit 2
    fi
  done
fi

echo "[Stage16N-R4H] restart read: oldjob=$OLDJOB step=$RESTART_CYCLE inc=$RESTART_INC"

abaqus job="${{JOB}}_datacheck" input="${{JOB}}.inp" oldjob="$OLDJOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}_datacheck.log"

abaqus job="$JOB" input="${{JOB}}.inp" oldjob="$OLDJOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${{JOB}}.msg" \\
  | tee "$LOG_DIR/${{JOB}}_parallelism_check.log" || true

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}_extract.log"

python3 stage16n_compare_r3j_jump_against_reference.py \\
  --jump-metrics "${{JOB}}_cycle_metrics.csv" \\
  --jump-local-states "${{JOB}}_selected_cycle_local_states.csv" \\
  --ref-metrics "../../../{ref_metrics}" \\
  --ref-local-states "../../../{ref_local}" \\
  --cycles "$FINAL_CYCLE" \\
  --out-dir "." \\
  --prefix "$JOB" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}_compare.log"

{{
  echo "# Stage 16N-R4H Case Status"
  echo
  echo "- PBS job: \\`${{PBS_JOBID:-manual}}\\`"
  echo "- Case: \\`{case.case_id}\\`"
  echo "- Mode: \\`$MODE\\`"
  echo "- Purpose: \\`$PURPOSE\\`"
  echo "- Base oldjob: \\`$BASE_OLDJOB\\`"
  echo "- Continuation oldjob: \\`$OLDJOB\\`"
  echo "- Restart read: \\`STEP=$RESTART_CYCLE, INC=$RESTART_INC\\`"
  echo "- First solved cycle: \\`$FIRST_SOLVED_CYCLE\\`"
  echo "- Final cycle: \\`$FINAL_CYCLE\\`"
  echo "- UMAT overwrite: \\`none\\`"
  if [[ -f "${{JOB}}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${{JOB}}.sta"; then
    echo "- Continuation solver status: \\`completed_successfully\\`"
  else
    echo "- Continuation solver status: \\`check $JOB.sta\\`"
  fi
  if [[ -f "${{JOB}}_comparison_summary.csv" ]]; then
    tail -n +2 "${{JOB}}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \\`$(date '+%Y-%m-%d %H:%M:%S')\\`"
}} > STAGE16N_R4H_CASE_STATUS.md

echo "[Stage16N-R4H] end: $(date '+%Y-%m-%d %H:%M:%S')"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_pbs(path: Path, case: R4HCase) -> None:
    text = f"""#!/bin/bash
#PBS -N {case.job}
#PBS -q teachingq
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

RUN_DIR="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4h_restart_source_diagnostics/{case.case_id}"
cd "$RUN_DIR"
bash link_restart_sources.sh
bash run_stage16n_r4h_restart_source_diagnostic_hpc.sh
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_dispatcher(path: Path) -> None:
    text = r"""#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R4H case id>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="${SCRIPT_DIR}/stage16n_restart_control/r4h_restart_source_diagnostics/${CASE_ID}"
MANIFEST="${SCRIPT_DIR}/stage16n_restart_control/r4h_restart_source_diagnostics/stage16n_r4h_restart_source_diagnostics.csv"
pbs_script="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $11}' "$MANIFEST")"

if [[ -z "$pbs_script" || ! -d "$CASE_DIR" ]]; then
  echo "Unknown R4H case: $CASE_ID" >&2
  exit 2
fi

cd "$CASE_DIR"
qsub "$pbs_script"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def prepare_cases(cases: tuple[R4HCase, ...]) -> None:
    R4H_DIR.mkdir(parents=True, exist_ok=True)
    dispatcher = STAGE_DIR / "submit_stage16n_r4h_restart_source_diagnostic_case.sh"
    write_dispatcher(dispatcher)
    dispatcher.chmod(0o755)
    rows: list[dict[str, str]] = []
    for case in cases:
        case.run_dir.mkdir(parents=True, exist_ok=True)
        base_inc = parse_checkpoint_increment(case.base_source_dir / f"{case.base_oldjob}.sta", case.checkpoint_cycle)
        if case.mode == "interior_source_split":
            write_source_deck(case.run_dir / f"{case.source_job}.inp", case, base_inc)
            write_continuation_deck(case.run_dir / f"{case.job}.inp", case, "__R4H_RESTART_INC__")
            restart_inc = ""
        else:
            restart_inc = str(parse_checkpoint_increment(case.base_source_dir / f"{case.base_oldjob}.sta", case.restart_cycle))
            write_continuation_deck(case.run_dir / f"{case.job}.inp", case, restart_inc)
        runner = case.run_dir / "run_stage16n_r4h_restart_source_diagnostic_hpc.sh"
        pbs = case.run_dir / f"submit_{case.job}.pbs"
        link_script = case.run_dir / "link_restart_sources.sh"
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
                "job": case.job,
                "mode": case.mode,
                "base_oldjob": case.base_oldjob,
                "checkpoint_cycle": str(case.checkpoint_cycle),
                "source_end_cycle": str(case.source_end_cycle),
                "restart_cycle": str(case.restart_cycle),
                "first_solved_cycle": str(case.first_solved_cycle),
                "final_cycle": str(case.final_cycle),
                "base_inc": str(base_inc),
                "pbs": pbs.name,
                "restart_inc_from_base_sta": restart_inc,
                "purpose": case.purpose,
            }
        )
    fields = [
        "case_id",
        "job",
        "mode",
        "base_oldjob",
        "checkpoint_cycle",
        "source_end_cycle",
        "restart_cycle",
        "first_solved_cycle",
        "final_cycle",
        "base_inc",
        "pbs",
        "restart_inc_from_base_sta",
        "purpose",
    ]
    with (R4H_DIR / "stage16n_r4h_restart_source_diagnostics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=["all"] + [case.case_id for case in CASES], default="all")
    args = parser.parse_args()
    selected = CASES if args.case == "all" else tuple(case for case in CASES if case.case_id == args.case)
    prepare_cases(selected)


if __name__ == "__main__":
    main()
