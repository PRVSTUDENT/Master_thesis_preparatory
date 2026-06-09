#!/usr/bin/env python3
"""Prepare Stage 16N-R2 native Abaqus restart continuation controls.

R2 is native restart only: no SDVINI/SIGINI and no UMAT memory overwrite.
The generated continuation decks read Abaqus' own restart files and continue
the cyclic loading to a later checkpoint.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
CONTROL_DIR = STAGE_DIR / "stage16n_restart_control"
NATIVE_DIR = CONTROL_DIR / "native_restart_cases"
EXTRACTOR = STAGE_DIR / "stage16n_extract_hysteresis_and_local_states.py"
COMPARE = STAGE_DIR / "stage16n_compare_native_restart_against_1000ref.py"
UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"


@dataclass(frozen=True)
class NativeRestartCase:
    case_id: str
    job: str
    source_case_dir: Path
    oldjob: str
    checkpoint_cycle: int
    target_cycle: int
    selected_field_cycles: tuple[int, ...]

    @property
    def run_dir(self) -> Path:
        return NATIVE_DIR / self.case_id


CASES = (
    NativeRestartCase(
        case_id="R2C1_100_to_250",
        job="stage16n_r2c1_native_restart_100_to_250",
        source_case_dir=CONTROL_DIR / "R1B_restart_reference_250cycles",
        oldjob="stage16n_r1b_restart_ref_250cycles",
        checkpoint_cycle=100,
        target_cycle=250,
        selected_field_cycles=(250,),
    ),
    NativeRestartCase(
        case_id="R2C2_250_to_500",
        job="stage16n_r2c2_native_restart_250_to_500",
        source_case_dir=CONTROL_DIR / "R1A_restart_reference_500cycles",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        checkpoint_cycle=250,
        target_cycle=500,
        selected_field_cycles=(500,),
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
        raise RuntimeError(f"Could not find cycle/step {checkpoint_cycle} in {sta_path}")
    return last_inc


def write_restart_deck(path: Path, case: NativeRestartCase, checkpoint_inc: int) -> None:
    lines = [
        f"** Stage 16N-R2 native restart continuation: {case.case_id}",
        "** No SDVINI/SIGINI and no UMAT overwrite.",
        "*HEADING",
        f"Stage 16N-R2 {case.checkpoint_cycle} to {case.target_cycle} native restart continuation",
        f"*RESTART, READ, STEP={case.checkpoint_cycle}, INC={checkpoint_inc}",
    ]
    selected = set(case.selected_field_cycles)
    for cycle in range(case.checkpoint_cycle + 1, case.target_cycle + 1):
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
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_runner(path: Path) -> None:
    text = r"""#!/usr/bin/env bash
set -euo pipefail

JOB="${1:-}"
OLDJOB="${2:-}"
TARGET_CYCLE="${3:-}"
if [[ -z "$JOB" || -z "$OLDJOB" || -z "$TARGET_CYCLE" ]]; then
  echo "Usage: $0 <job-name> <oldjob-name> <target-cycle>" >&2
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

echo "[Stage16N-R2] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R2] PBS job: ${PBS_JOBID:-manual}"
echo "[Stage16N-R2] Abaqus job: ${JOB}"
echo "[Stage16N-R2] oldjob: ${OLDJOB}"
echo "[Stage16N-R2] target cycle: ${TARGET_CYCLE}"
echo "[Stage16N-R2] cpus=${ABAQUS_CPUS} mp_mode=${ABAQUS_MP_MODE}"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${OLDJOB}.${ext}" ]]; then
    echo "Missing native restart source: ${OLDJOB}.${ext}" >&2
    exit 2
  fi
done

if [[ ! -f "${JOB}.inp" ]]; then
  echo "Missing continuation input deck: ${JOB}.inp" >&2
  exit 2
fi
if [[ ! -f "stage16n_neml_equivalent_chaboche_umat.for" ]]; then
  echo "Missing UMAT: stage16n_neml_equivalent_chaboche_umat.for" >&2
  exit 2
fi

abaqus job="${JOB}_datacheck" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  datacheck interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}_datacheck.log"

abaqus job="${JOB}" input="${JOB}.inp" oldjob="${OLDJOB}" \
  user=stage16n_neml_equivalent_chaboche_umat.for \
  interactive ask_delete=OFF scratch=. \
  cpus="${ABAQUS_CPUS}" mp_mode="${ABAQUS_MP_MODE}" \
  2>&1 | tee "${LOG_DIR}/${JOB}.log"

grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${JOB}.msg" \
  | tee "${LOG_DIR}/${JOB}_parallelism_check.log" || true

if [[ -f "${JOB}.odb" && -f "stage16n_extract_hysteresis_and_local_states.py" ]]; then
  abaqus python stage16n_extract_hysteresis_and_local_states.py --job "${JOB}" \
    2>&1 | tee "${LOG_DIR}/${JOB}_extract.log"
fi

python3 stage16n_compare_native_restart_against_1000ref.py \
  --restart-metrics "${JOB}_cycle_metrics.csv" \
  --restart-local-states "${JOB}_selected_cycle_local_states.csv" \
  --cycles "${TARGET_CYCLE}" \
  --out-dir "." \
  2>&1 | tee "${LOG_DIR}/${JOB}_compare.log"

{
  echo "# Stage 16N-R2 Native Restart Case Status"
  echo
  echo "- PBS job: \`${PBS_JOBID:-manual}\`"
  echo "- Abaqus job: \`${JOB}\`"
  echo "- Oldjob: \`${OLDJOB}\`"
  echo "- Target cycle: \`${TARGET_CYCLE}\`"
  echo "- Finished: \`$(date '+%Y-%m-%d %H:%M:%S')\`"
  if [[ -f "${JOB}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${JOB}.sta"; then
    echo "- Solver status: \`completed\`"
  else
    echo "- Solver status: \`check ${JOB}.sta\`"
  fi
} > "STAGE16N_R2_CASE_STATUS.md"

echo "[Stage16N-R2] end: $(date '+%Y-%m-%d %H:%M:%S')"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_pbs(path: Path, case: NativeRestartCase) -> None:
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

RUN_DIR="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/native_restart_cases/{case.case_id}"
cd "$RUN_DIR"
bash link_restart_sources.sh
bash run_stage16n_native_restart_continuation_hpc.sh {case.job} {case.oldjob} {case.target_cycle}
""",
        encoding="utf-8",
        newline="\n",
    )


def write_dispatcher(path: Path) -> None:
    text = r"""#!/usr/bin/env bash
set -euo pipefail

CASE_ID="${1:-}"
if [[ -z "$CASE_ID" ]]; then
  echo "Usage: $0 <R2C1_100_to_250|R2C2_250_to_500>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/stage16n_restart_control/native_restart_cases"
CASE_DIR="${ROOT_DIR}/${CASE_ID}"
MANIFEST="${ROOT_DIR}/stage16n_r2_native_restart_cases.csv"

if [[ ! -d "$CASE_DIR" ]]; then
  echo "Unknown case directory: $CASE_DIR" >&2
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing manifest: $MANIFEST" >&2
  exit 2
fi

row="$(awk -F, -v id="$CASE_ID" 'NR > 1 && $1 == id {print $0}' "$MANIFEST")"
if [[ -z "$row" ]]; then
  echo "Case not found in manifest: $CASE_ID" >&2
  exit 2
fi

IFS=, read -r case_id job oldjob checkpoint_cycle checkpoint_inc target_cycle <<< "$row"
cd "$CASE_DIR"
bash link_restart_sources.sh
bash run_stage16n_native_restart_continuation_hpc.sh "$job" "$oldjob" "$target_cycle"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_link_script(path: Path, case: NativeRestartCase) -> None:
    rel_source = Path("..") / ".." / case.source_case_dir.name
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f'SOURCE_DIR="{rel_source.as_posix()}"',
        f'OLDJOB="{case.oldjob}"',
        "for ext in odb res stt mdl sim prt; do",
        '  src="${SOURCE_DIR}/${OLDJOB}.${ext}"',
        '  dst="${OLDJOB}.${ext}"',
        '  if [[ ! -e "$src" ]]; then',
        '    echo "Missing restart source: $src" >&2',
        "    exit 2",
        "  fi",
        '  ln -sfn "$src" "$dst"',
        "done",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_manifest(path: Path, case: NativeRestartCase, checkpoint_inc: int) -> None:
    lines = [
        f"# Stage 16N-R2 Native Restart Case: {case.case_id}",
        "",
        f"- Job: `{case.job}`",
        f"- Source R1 case: `{case.source_case_dir.relative_to(CONTROL_DIR)}`",
        f"- Oldjob: `{case.oldjob}`",
        f"- Restart read: `STEP={case.checkpoint_cycle}, INC={checkpoint_inc}`",
        f"- Continue cycles: `{case.checkpoint_cycle + 1}` to `{case.target_cycle}`",
        "- UMAT overwrite: none",
        "- SDVINI/SIGINI: none",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def prepare_cases(cases: tuple[NativeRestartCase, ...]) -> None:
    if not EXTRACTOR.exists():
        raise FileNotFoundError(EXTRACTOR)
    if not COMPARE.exists():
        raise FileNotFoundError(COMPARE)
    if not UMAT.exists():
        raise FileNotFoundError(UMAT)
    NATIVE_DIR.mkdir(parents=True, exist_ok=True)
    write_dispatcher(STAGE_DIR / "run_stage16n_native_restart_continuation_hpc.sh")
    summary_rows = []
    for case in cases:
        run_dir = case.run_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        sta = case.source_case_dir / f"{case.oldjob}.sta"
        checkpoint_inc = parse_checkpoint_increment(sta, case.checkpoint_cycle)
        write_restart_deck(run_dir / f"{case.job}.inp", case, checkpoint_inc)
        write_runner(run_dir / "run_stage16n_native_restart_continuation_hpc.sh")
        write_pbs(run_dir / f"submit_{case.job}.pbs", case)
        write_link_script(run_dir / "link_restart_sources.sh", case)
        write_manifest(run_dir / "STAGE16N_R2_CASE_MANIFEST.md", case, checkpoint_inc)
        shutil.copy2(UMAT, run_dir / "stage16n_neml_equivalent_chaboche_umat.for")
        shutil.copy2(EXTRACTOR, run_dir / "stage16n_extract_hysteresis_and_local_states.py")
        shutil.copy2(COMPARE, run_dir / "stage16n_compare_native_restart_against_1000ref.py")
        summary_rows.append(
            {
                "case_id": case.case_id,
                "job": case.job,
                "oldjob": case.oldjob,
                "checkpoint_cycle": case.checkpoint_cycle,
                "checkpoint_inc": checkpoint_inc,
                "target_cycle": case.target_cycle,
            }
        )
        print(f"Wrote {run_dir / (case.job + '.inp')}")
        print(f"Wrote {run_dir / ('submit_' + case.job + '.pbs')}")
    summary = NATIVE_DIR / "stage16n_r2_native_restart_cases.csv"
    with summary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["case_id", "job", "oldjob", "checkpoint_cycle", "checkpoint_inc", "target_cycle"],
        )
        writer.writeheader()
        writer.writerows(summary_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=["all", "R2C1", "R2C2"], default="all")
    args = parser.parse_args()
    if args.case == "R2C1":
        cases = (CASES[0],)
    elif args.case == "R2C2":
        cases = (CASES[1],)
    else:
        cases = CASES
    prepare_cases(cases)


if __name__ == "__main__":
    main()
