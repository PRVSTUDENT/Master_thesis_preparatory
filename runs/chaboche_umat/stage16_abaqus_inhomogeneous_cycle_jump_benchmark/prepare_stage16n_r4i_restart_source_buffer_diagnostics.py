#!/usr/bin/env python3
"""Prepare Stage 16N-R4I restart-source buffer diagnostics."""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
CONTROL_DIR = STAGE_DIR / "stage16n_restart_control"
R4I_DIR = CONTROL_DIR / "r4i_restart_source_buffer_diagnostics"
R1A_DIR = CONTROL_DIR / "R1A_restart_reference_500cycles"
UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
EXTRACTOR = STAGE_DIR / "stage16n_extract_hysteresis_and_local_states.py"
COMPARE = STAGE_DIR / "stage16n_compare_r3j_jump_against_reference.py"
REF500_METRICS = STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv"
REF500_LOCAL = STAGE_DIR / "stage16n_1000cycle_pilot" / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv"
REF750_METRICS = STAGE_DIR / "stage16n_parallel_max_reference" / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv"
REF750_LOCAL = STAGE_DIR / "stage16n_parallel_max_reference" / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv"


@dataclass(frozen=True)
class R4ICase:
    case_id: str
    job: str
    source_style: str
    checkpoint_cycle: int
    source_end_cycle: int
    restart_cycle: int
    final_cycle: int
    ref_metrics: Path
    ref_local_states: Path
    purpose: str

    @property
    def run_dir(self) -> Path:
        return R4I_DIR / self.case_id

    @property
    def source_job(self) -> str:
        return f"{self.job}_source_{self.checkpoint_cycle}_to_{self.source_end_cycle}"

    @property
    def first_solved_cycle(self) -> int:
        return self.restart_cycle + 1


CASES = (
    R4ICase(
        case_id="R4I1_deck_clone_250_to_281_restart_280_to_500",
        job="stage16n_r4i1_deck_clone_250_to_281_restart_280_to_500",
        source_style="deck_clone",
        checkpoint_cycle=250,
        source_end_cycle=281,
        restart_cycle=280,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="clone/truncate the clean direct replay deck shape, solve 250--281, restart interior 280, continue 281--500",
    ),
    R4ICase(
        case_id="R4I2_buffer_250_to_300_restart_280_to_500",
        job="stage16n_r4i2_buffer_250_to_300_restart_280_to_500",
        source_style="buffered_generated",
        checkpoint_cycle=250,
        source_end_cycle=300,
        restart_cycle=280,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="generated source solve 250--300, restart interior 280, continue 281--500",
    ),
    R4ICase(
        case_id="R4I3_buffer_250_to_300_restart_270_to_500",
        job="stage16n_r4i3_buffer_250_to_300_restart_270_to_500",
        source_style="buffered_generated",
        checkpoint_cycle=250,
        source_end_cycle=300,
        restart_cycle=270,
        final_cycle=500,
        ref_metrics=REF500_METRICS,
        ref_local_states=REF500_LOCAL,
        purpose="generated source solve 250--300, restart interior 270, continue 271--500",
    ),
    R4ICase(
        case_id="R4I4_buffer_500_to_525_restart_505_to_750",
        job="stage16n_r4i4_buffer_500_to_525_restart_505_to_750",
        source_style="buffered_generated",
        checkpoint_cycle=500,
        source_end_cycle=525,
        restart_cycle=505,
        final_cycle=750,
        ref_metrics=REF750_METRICS,
        ref_local_states=REF750_LOCAL,
        purpose="generated source solve 500--525, restart interior 505, continue 506--750",
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


def add_cycle_step(lines: list[str], cycle: int, *, write_restart: bool, write_field: bool) -> None:
    lines.extend(
        [
            "*STEP, NAME=CYCLE_%04d, NLGEOM=NO, INC=160" % cycle,
            "*STATIC",
            "0.005, 1.0, 1.0E-08, 0.025",
        ]
    )
    if write_restart:
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
    if write_field:
        add_field_output(lines)
    lines.append("*END STEP")


def write_source_deck(path: Path, case: R4ICase, checkpoint_inc: int) -> None:
    lines = [
        f"** Stage 16N-R4I source solve: {case.case_id}",
        f"** Source style: {case.source_style}",
        f"** Purpose: {case.purpose}",
        "*HEADING",
        f"Stage 16N-R4I source {case.checkpoint_cycle} to {case.source_end_cycle}",
        f"*RESTART, READ, STEP={case.checkpoint_cycle}, INC={checkpoint_inc}",
    ]
    for cycle in range(case.checkpoint_cycle + 1, case.source_end_cycle + 1):
        if case.source_style == "deck_clone":
            write_field = cycle == case.source_end_cycle
        else:
            write_field = cycle in {case.restart_cycle, case.source_end_cycle}
        add_cycle_step(lines, cycle, write_restart=True, write_field=write_field)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_continuation_deck(path: Path, case: R4ICase) -> None:
    lines = [
        f"** Stage 16N-R4I continuation: {case.case_id}",
        f"** Purpose: {case.purpose}",
        "*HEADING",
        f"Stage 16N-R4I {case.restart_cycle} to {case.final_cycle}",
        f"*RESTART, READ, STEP={case.restart_cycle}, INC=__R4I_RESTART_INC__",
    ]
    for cycle in range(case.first_solved_cycle, case.final_cycle + 1):
        add_cycle_step(lines, cycle, write_restart=False, write_field=(cycle == case.final_cycle))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_link_script(path: Path) -> None:
    text = """#!/usr/bin/env bash
set -euo pipefail

OLDJOB="stage16n_r1a_restart_ref_500cycles"
HOME_SOURCE="$HOME/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles"

echo "Linking R1A restart sources from: $HOME_SOURCE"
for ext in odb res stt mdl sim prt; do
  src="$HOME_SOURCE/${OLDJOB}.${ext}"
  dst="${OLDJOB}.${ext}"
  if [[ ! -e "$src" ]]; then
    echo "Missing base restart source: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_runner(path: Path, case: R4ICase) -> None:
    ref_metrics = case.ref_metrics.relative_to(STAGE_DIR).as_posix()
    ref_local = case.ref_local_states.relative_to(STAGE_DIR).as_posix()
    text = f"""#!/usr/bin/env bash
set -euo pipefail

JOB="{case.job}"
SOURCE_JOB="{case.source_job}"
BASE_OLDJOB="stage16n_r1a_restart_ref_500cycles"
CHECKPOINT_CYCLE="{case.checkpoint_cycle}"
SOURCE_END_CYCLE="{case.source_end_cycle}"
RESTART_CYCLE="{case.restart_cycle}"
FIRST_SOLVED_CYCLE="{case.first_solved_cycle}"
FINAL_CYCLE="{case.final_cycle}"
SOURCE_STYLE="{case.source_style}"
PURPOSE="{case.purpose}"

ABAQUS_CPUS="${{ABAQUS_CPUS:-16}}"
ABAQUS_MP_MODE="${{ABAQUS_MP_MODE:-threads}}"
LOG_DIR="${{LOG_DIR:-_logs}}"
ABAQUS_SCRATCH="${{TMPDIR:-$PWD/tmp}}"
mkdir -p "$LOG_DIR" "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R4I] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R4I] PBS job: ${{PBS_JOBID:-manual}}"
echo "[Stage16N-R4I] job: $JOB"
echo "[Stage16N-R4I] source style: $SOURCE_STYLE"
echo "[Stage16N-R4I] first solved cycle: $FIRST_SOLVED_CYCLE"
echo "[Stage16N-R4I] purpose: $PURPOSE"

bash link_restart_sources.sh

abaqus job="$SOURCE_JOB" input="${{SOURCE_JOB}}.inp" oldjob="$BASE_OLDJOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{SOURCE_JOB}}.log"

if [[ ! -f "${{SOURCE_JOB}}.sta" ]] || ! grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${{SOURCE_JOB}}.sta"; then
  echo "Source solve did not complete successfully; check $SOURCE_JOB.sta" >&2
  exit 2
fi

RESTART_INC="$(awk -v step="$RESTART_CYCLE" '$1 == step && $2 ~ /^[0-9]+$/ {{inc=$2}} END {{if (inc == "") exit 3; print inc}}' "${{SOURCE_JOB}}.sta")"
python3 - <<PY
from pathlib import Path
path = Path("{case.job}.inp")
path.write_text(path.read_text().replace("INC=__R4I_RESTART_INC__", "INC=" + "$RESTART_INC"))
PY

abaqus python stage16n_extract_hysteresis_and_local_states.py --job "$SOURCE_JOB" \\
  2>&1 | tee "$LOG_DIR/${{SOURCE_JOB}}_extract.log" || true

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${{SOURCE_JOB}}.${{ext}}" ]]; then
    echo "Missing generated source restart file: $SOURCE_JOB.$ext" >&2
    exit 2
  fi
done

echo "[Stage16N-R4I] restart read: oldjob=$SOURCE_JOB step=$RESTART_CYCLE inc=$RESTART_INC"

abaqus job="${{JOB}}_datacheck" input="${{JOB}}.inp" oldjob="$SOURCE_JOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}_datacheck.log"

abaqus job="$JOB" input="${{JOB}}.inp" oldjob="$SOURCE_JOB" \\
  user=stage16n_neml_equivalent_chaboche_umat.for \\
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="$ABAQUS_CPUS" mp_mode="$ABAQUS_MP_MODE" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}.log"

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
  echo "# Stage 16N-R4I Case Status"
  echo
  echo "- PBS job: \\`${{PBS_JOBID:-manual}}\\`"
  echo "- Job: \\`$JOB\\`"
  echo "- Source job: \\`$SOURCE_JOB\\`"
  echo "- Source style: \\`$SOURCE_STYLE\\`"
  echo "- Purpose: \\`$PURPOSE\\`"
  echo "- Restart read: \\`STEP=$RESTART_CYCLE, INC=$RESTART_INC\\`"
  echo "- First solved cycle: \\`$FIRST_SOLVED_CYCLE\\`"
  echo "- Final cycle: \\`$FINAL_CYCLE\\`"
  if [[ -f "${{JOB}}_comparison_summary.csv" ]]; then
    tail -n +2 "${{JOB}}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \\`$(date '+%Y-%m-%d %H:%M:%S')\\`"
}} > STAGE16N_R4I_CASE_STATUS.md

echo "[Stage16N-R4I] end: $(date '+%Y-%m-%d %H:%M:%S')"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_pbs(path: Path, case: R4ICase) -> None:
    pbs_out = f"/scratch/pr21vyci/stage16n_r4i_pbs/{case.job}.pbs.out"
    text = f"""#!/bin/bash
#PBS -N {case.job}
#PBS -q teachingq
#PBS -l select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
#PBS -l walltime=24:00:00
#PBS -j oe
#PBS -o {pbs_out}
#PBS -m abe
#PBS -M pr21vyci@mailserver.tu-freiberg.de

set -euo pipefail

export REPO_ROOT="$HOME/master_thesis/Abaqus_trial"
export HOME_CASE_DIR="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4i_restart_source_buffer_diagnostics/{case.case_id}"
export SCRATCH_CASE_DIR="/scratch/$USER/stage16n_r4i/{case.case_id}/${{PBS_JOBID:-manual}}"
export TMPDIR="$SCRATCH_CASE_DIR/tmp"
export ABAQUS_CPUS=16
export ABAQUS_MP_MODE=threads

mkdir -p "$SCRATCH_CASE_DIR" "$TMPDIR" /scratch/pr21vyci/stage16n_r4i_pbs
rsync -a --delete \\
  --exclude='*.odb' --exclude='*.stt' --exclude='*.res' --exclude='*.sim' \\
  --exclude='*.mdl' --exclude='*.prt' --exclude='*.dat' --exclude='*.msg' \\
  --exclude='*.023' --exclude='*.cax' --exclude='*.abq' --exclude='*.pac' \\
  --exclude='*.sel' --exclude='*.lck' --exclude='state.bin' --exclude='state.csv' \\
  "$HOME_CASE_DIR/" "$SCRATCH_CASE_DIR/"

cd "$SCRATCH_CASE_DIR"
bash run_stage16n_r4i_restart_source_buffer_hpc.sh

rsync -a \\
  --include='*/' --include='*.md' --include='*.csv' --include='*.txt' --include='*.log' \\
  --include='*.sta' --include='*.pbs.out' --exclude='*' \\
  "$SCRATCH_CASE_DIR/" "$HOME_CASE_DIR/"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_dispatcher(path: Path) -> None:
    text = """#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R4I case id>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="${SCRIPT_DIR}/stage16n_restart_control/r4i_restart_source_buffer_diagnostics/${CASE_ID}"
MANIFEST="${SCRIPT_DIR}/stage16n_restart_control/r4i_restart_source_buffer_diagnostics/stage16n_r4i_restart_source_buffer_diagnostics.csv"
pbs_script="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $12}' "$MANIFEST")"

if [[ -z "$pbs_script" || ! -d "$CASE_DIR" ]]; then
  echo "Unknown R4I case: $CASE_ID" >&2
  exit 2
fi

mkdir -p /scratch/$USER/stage16n_r4i_pbs
cd "$CASE_DIR"
if command -v qsub_abq >/dev/null 2>&1; then
  qsub_abq "$pbs_script"
else
  echo "qsub_abq not found; refusing raw qsub for Abaqus job" >&2
  exit 2
fi
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def prepare_cases(cases: tuple[R4ICase, ...]) -> None:
    R4I_DIR.mkdir(parents=True, exist_ok=True)
    dispatcher = STAGE_DIR / "submit_stage16n_r4i_restart_source_buffer_case.sh"
    write_dispatcher(dispatcher)
    dispatcher.chmod(0o755)
    rows: list[dict[str, str]] = []
    for case in cases:
        case.run_dir.mkdir(parents=True, exist_ok=True)
        base_inc = parse_checkpoint_increment(R1A_DIR / "stage16n_r1a_restart_ref_500cycles.sta", case.checkpoint_cycle)
        write_source_deck(case.run_dir / f"{case.source_job}.inp", case, base_inc)
        write_continuation_deck(case.run_dir / f"{case.job}.inp", case)
        write_link_script(case.run_dir / "link_restart_sources.sh")
        write_runner(case.run_dir / "run_stage16n_r4i_restart_source_buffer_hpc.sh", case)
        write_pbs(case.run_dir / f"submit_{case.job}.pbs", case)
        for script in (
            case.run_dir / "link_restart_sources.sh",
            case.run_dir / "run_stage16n_r4i_restart_source_buffer_hpc.sh",
            case.run_dir / f"submit_{case.job}.pbs",
        ):
            script.chmod(0o755)
        for src in (UMAT, EXTRACTOR, COMPARE):
            shutil.copy2(src, case.run_dir / src.name)
        rows.append(
            {
                "case_id": case.case_id,
                "job": case.job,
                "source_style": case.source_style,
                "checkpoint_cycle": str(case.checkpoint_cycle),
                "source_end_cycle": str(case.source_end_cycle),
                "restart_cycle": str(case.restart_cycle),
                "first_solved_cycle": str(case.first_solved_cycle),
                "final_cycle": str(case.final_cycle),
                "base_inc": str(base_inc),
                "source_inp": f"{case.source_job}.inp",
                "continuation_inp": f"{case.job}.inp",
                "pbs": f"submit_{case.job}.pbs",
                "purpose": case.purpose,
            }
        )
    fields = [
        "case_id",
        "job",
        "source_style",
        "checkpoint_cycle",
        "source_end_cycle",
        "restart_cycle",
        "first_solved_cycle",
        "final_cycle",
        "base_inc",
        "source_inp",
        "continuation_inp",
        "pbs",
        "purpose",
    ]
    with (R4I_DIR / "stage16n_r4i_restart_source_buffer_diagnostics.csv").open("w", newline="", encoding="utf-8") as handle:
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
