#!/usr/bin/env python3
"""Prepare Stage 16N-R3J restart-preserved fixed cycle-jump controls."""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
CONTROL_DIR = STAGE_DIR / "stage16n_restart_control"
R3J_DIR = CONTROL_DIR / "restart_jump_cases"
SOURCE_R1A = CONTROL_DIR / "R1A_restart_reference_500cycles"
BASE_UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
EXTRACTOR = STAGE_DIR / "stage16n_extract_hysteresis_and_local_states.py"
EXACT_STATE_EXTRACTOR = STAGE_DIR / "stage16n_extract_exact_state_for_reinjection.py"
EXTRAPOLATOR = STAGE_DIR / "stage16n_make_extrapolated_state.py"


@dataclass(frozen=True)
class RestartJumpCase:
    case_id: str
    job: str
    oldjob: str
    source_dir: Path
    previous_cycle: int
    checkpoint_cycle: int
    jump_cycles: int
    target_cycle: int
    ref_metrics: Path
    ref_local_states: Path
    solve_start_cycle: int | None = None

    @property
    def run_dir(self) -> Path:
        return R3J_DIR / self.case_id

    @property
    def jump_cycle(self) -> int:
        return self.checkpoint_cycle + self.jump_cycles

    @property
    def target_step(self) -> int:
        return self.checkpoint_cycle + 1

    @property
    def continuation_start_cycle(self) -> int:
        if self.solve_start_cycle is not None:
            return self.solve_start_cycle
        return self.checkpoint_cycle + 1


PARALLEL_REF = STAGE_DIR / "stage16n_parallel_max_reference"

CASES = (
    RestartJumpCase(
        case_id="R3J1_250_to_255_to_500",
        job="stage16n_r3j1_jump_250_to_255_to_500_a4",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=5,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J2_500_to_505_to_750",
        job="stage16n_r3j2_jump_500_to_505_to_750_a4",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=5,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J3_250_to_260_to_500",
        job="stage16n_r3j3_jump_250_to_260_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=10,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J4_500_to_510_to_750",
        job="stage16n_r3j4_jump_500_to_510_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=10,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J5_250_to_270_to_500",
        job="stage16n_r3j5_jump_250_to_270_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=20,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J6_500_to_520_to_750",
        job="stage16n_r3j6_jump_500_to_520_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=20,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J7_250_to_300_to_500",
        job="stage16n_r3j7_jump_250_to_300_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=50,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R3J8_500_to_550_to_750",
        job="stage16n_r3j8_jump_500_to_550_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=50,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
    ),
    RestartJumpCase(
        case_id="R4J1_250_to_300_solve_301_to_500",
        job="stage16n_r4j1_jump_250_to_300_solve_301_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=50,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
        solve_start_cycle=301,
    ),
    RestartJumpCase(
        case_id="R4J2_500_to_550_solve_551_to_750",
        job="stage16n_r4j2_jump_500_to_550_solve_551_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=50,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
        solve_start_cycle=551,
    ),
    RestartJumpCase(
        case_id="R4J3_250_to_270_solve_271_to_500",
        job="stage16n_r4j3_jump_250_to_270_solve_271_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=20,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
        solve_start_cycle=271,
    ),
    RestartJumpCase(
        case_id="R4J4_500_to_520_solve_521_to_750",
        job="stage16n_r4j4_jump_500_to_520_solve_521_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=20,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
        solve_start_cycle=521,
    ),
    RestartJumpCase(
        case_id="R4J5_250_to_285_solve_286_to_500",
        job="stage16n_r4j5_jump_250_to_285_solve_286_to_500",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=100,
        checkpoint_cycle=250,
        jump_cycles=35,
        target_cycle=500,
        ref_metrics=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv",
        ref_local_states=STAGE_DIR
        / "stage16n_1000cycle_pilot"
        / "stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv",
        solve_start_cycle=286,
    ),
    RestartJumpCase(
        case_id="R4J6_500_to_510_solve_511_to_750",
        job="stage16n_r4j6_jump_500_to_510_solve_511_to_750",
        oldjob="stage16n_r1a_restart_ref_500cycles",
        source_dir=SOURCE_R1A,
        previous_cycle=250,
        checkpoint_cycle=500,
        jump_cycles=10,
        target_cycle=750,
        ref_metrics=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv",
        ref_local_states=PARALLEL_REF / "stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv",
        solve_start_cycle=511,
    ),
)


def parse_checkpoint_increment(sta_path: Path, checkpoint_cycle: int) -> int:
    last_inc: int | None = None
    for line in sta_path.read_text(errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            if int(parts[0]) == checkpoint_cycle:
                last_inc = int(parts[1])
    if last_inc is None:
        raise RuntimeError(f"Could not find cycle/step {checkpoint_cycle} in {sta_path}")
    return last_inc


def strip_empty_hooks(text: str) -> str:
    marker = "C Empty initialization hooks."
    index = text.find(marker)
    if index < 0:
        raise RuntimeError(f"Could not locate empty initialization hooks in {BASE_UMAT}")
    return text[:index].rstrip() + "\n\n"


def write_jump_umat(path: Path) -> None:
    hooks = r"""C ======================================================================
C Stage 16N-R3J restart-preserved extrapolated material-memory overwrite.
C Reads direct-access binary state records generated from a cycle-space
C slope pair and overwrites only independent material memory STATEV(1:25).
C STATEV(26) and STATEV(27) are diagnostic/derived and are not overwritten.
C ======================================================================

      SUBROUTINE STAGE16N_READ_JUMP_STATE(NOEL,NPT,VALS,FOUND)
      INCLUDE 'ABA_PARAM.INC'
      INTEGER NOEL,NPT,FOUND,RECNO,UNITNO,IOS,I
      DOUBLE PRECISION VALS(33)
      CHARACTER*512 STATEBIN

      FOUND=0
      DO I=1,33
        VALS(I)=0.D0
      END DO

      CALL GETENV('STAGE16N_JUMP_STATE_BIN',STATEBIN)
      IF (STATEBIN.EQ.' ') STATEBIN='state.bin'

      RECNO=(NOEL-1)*8+NPT
      UNITNO=11000+NOEL*10+NPT
      OPEN(UNIT=UNITNO,FILE=STATEBIN,STATUS='OLD',
     1 ACCESS='DIRECT',FORM='UNFORMATTED',RECL=66,IOSTAT=IOS)
      IF (IOS.NE.0) THEN
        WRITE(6,*) 'STAGE16N_R3J ERROR: cannot open state binary'
        WRITE(6,*) STATEBIN
        CALL XIT
      END IF

      READ(UNITNO,REC=RECNO,IOSTAT=IOS) (VALS(I),I=1,33)
      CLOSE(UNITNO)
      IF (IOS.NE.0) THEN
        WRITE(6,*) 'STAGE16N_R3J ERROR: cannot read state record',
     1             NOEL,NPT,RECNO,IOS
        CALL XIT
      END IF

      FOUND=1
      RETURN
      END

      SUBROUTINE STAGE16N_R3J_JUMP_OVERWRITE(STATEV,NSTATV,
     1 NOEL,NPT,JSTEP,KINC,TIME,PROPS,NPROPS)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV),JSTEP(4),TIME(2),PROPS(NPROPS)
      INTEGER NSTATV,NOEL,NPT,KINC,NPROPS
      INTEGER TARGET_STEP,FOUND,I
      DOUBLE PRECISION VALS(33),CHECK_TIME,TOL
      CHARACTER*80 TARGET_TEXT,CHECK_TEXT

      TARGET_STEP=-1
      CHECK_TIME=-1.D0
      CALL GETENV('STAGE16N_JUMP_TARGET_STEP',TARGET_TEXT)
      CALL GETENV('STAGE16N_JUMP_CHECK_TIME',CHECK_TEXT)
      IF (TARGET_TEXT.NE.' ') READ(TARGET_TEXT,*,ERR=90) TARGET_STEP
      IF (CHECK_TEXT.NE.' ') READ(CHECK_TEXT,*,ERR=90) CHECK_TIME
90    CONTINUE

      TOL=1.D-6
      IF (TARGET_STEP.LT.0) RETURN
      IF (JSTEP(1).NE.TARGET_STEP) RETURN
      IF (KINC.NE.0) RETURN
      IF (DABS(TIME(1)).GT.TOL) RETURN
      IF (CHECK_TIME.GE.0.D0 .AND. DABS(TIME(2)-CHECK_TIME).GT.TOL)
     1 RETURN

      CALL STAGE16N_READ_JUMP_STATE(NOEL,NPT,VALS,FOUND)
      IF (FOUND.EQ.0) THEN
        WRITE(6,*) 'STAGE16N_R3J missing jump state',NOEL,NPT
        CALL XIT
      END IF

      DO I=1,NSTATV
        IF (I.LE.25) STATEV(I)=VALS(I+6)
      END DO

      IF ((NOEL.LE.4 .AND. NPT.LE.2) .OR.
     1    (NOEL.EQ.278 .AND. NPT.EQ.1)) THEN
        WRITE(6,*) 'STAGE16N_R3J_OVERWRITE',
     1      ' NOEL=',NOEL,' NPT=',NPT,' KSTEP=',JSTEP(1),
     2      ' KINC=',KINC,' TIME1=',TIME(1),' TIME2=',TIME(2),
     3      ' STATEV1=',STATEV(1),' STATEV8=',STATEV(8),
     4      ' STATEV11=',STATEV(11)
      END IF

      RETURN
      END

      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,
     1 LAYER,KSPT,LREBAR,NAMES)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 NAMES(2)
      RETURN
      END

      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV),COORDS(NCRDS)
      RETURN
      END
"""
    base = strip_empty_hooks(BASE_UMAT.read_text())
    needle = "      TINY = 1.D-12"
    call = (
        "      CALL STAGE16N_R3J_JUMP_OVERWRITE(STATEV,NSTATV,\n"
        "     1 NOEL,NPT,JSTEP,KINC,TIME,PROPS,NPROPS)\n\n"
        "      TINY = 1.D-12"
    )
    if needle not in base:
        raise RuntimeError("Could not locate UMAT insertion point")
    path.write_text((base.replace(needle, call, 1) + hooks).rstrip() + "\n", encoding="utf-8", newline="\n")


def write_restart_deck(path: Path, case: RestartJumpCase, checkpoint_inc: int) -> None:
    lines = [
        f"** Stage 16N-R3J restart-preserved +{case.jump_cycles} cycle jump: {case.case_id}",
        "** Native Abaqus restart, extrapolated overwrite of independent STATEV(1:25) at KINC=0.",
        f"** Slope pair: {case.previous_cycle} -> {case.checkpoint_cycle}.",
        "*HEADING",
        f"Stage 16N-R3J {case.checkpoint_cycle} to {case.jump_cycle} to {case.target_cycle}",
        f"*RESTART, READ, STEP={case.checkpoint_cycle}, INC={checkpoint_inc}",
    ]
    for cycle in range(case.continuation_start_cycle, case.target_cycle + 1):
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
        if cycle == case.target_cycle:
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


def write_link_script(path: Path, case: RestartJumpCase) -> None:
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

echo "Linking restart sources from: $SOURCE_DIR"
for ext in odb res stt mdl sim prt; do
  src="${{SOURCE_DIR}}/${{OLDJOB}}.${{ext}}"
  dst="${{OLDJOB}}.${{ext}}"
  if [[ ! -e "$src" ]]; then
    echo "Missing restart source: $src" >&2
    exit 2
  fi
  ln -sfn "$src" "$dst"
done
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_runner(path: Path, case: RestartJumpCase) -> None:
    ref_metrics = case.ref_metrics.relative_to(STAGE_DIR).as_posix()
    ref_local_states = case.ref_local_states.relative_to(STAGE_DIR).as_posix()
    text = f"""#!/usr/bin/env bash
set -euo pipefail

JOB="{case.job}"
OLDJOB="{case.oldjob}"
PREVIOUS_CYCLE="{case.previous_cycle}"
CHECKPOINT_CYCLE="{case.checkpoint_cycle}"
JUMP_CYCLES="{case.jump_cycles}"
JUMP_CYCLE="{case.jump_cycle}"
TARGET_CYCLE="{case.target_cycle}"
TARGET_STEP="{case.target_step}"

ABAQUS_CPUS="${{ABAQUS_CPUS:-16}}"
ABAQUS_MP_MODE="${{ABAQUS_MP_MODE:-threads}}"
LOG_DIR="${{LOG_DIR:-_logs}}"
ABAQUS_SCRATCH="${{PBS_JOBDIR:-$PWD/_abaqus_scratch}}"
mkdir -p "$LOG_DIR"
mkdir -p "$ABAQUS_SCRATCH"

module purge
module load gcc/11.4.0
module load intel/2024.2.0
module load abaqus/2023

echo "[Stage16N-R3J] start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[Stage16N-R3J] PBS job: ${{PBS_JOBID:-manual}}"
echo "[Stage16N-R3J] Abaqus job: $JOB"
echo "[Stage16N-R3J] oldjob: $OLDJOB"
echo "[Stage16N-R3J] restart checkpoint: $CHECKPOINT_CYCLE"
echo "[Stage16N-R3J] slope pair: $PREVIOUS_CYCLE -> $CHECKPOINT_CYCLE"
echo "[Stage16N-R3J] material jump: $CHECKPOINT_CYCLE -> $JUMP_CYCLE"
echo "[Stage16N-R3J] solved continuation cycles: {case.continuation_start_cycle} -> $TARGET_CYCLE"
echo "[Stage16N-R3J] target cycle: $TARGET_CYCLE"
echo "[Stage16N-R3J] cpus=${{ABAQUS_CPUS}} mp_mode=${{ABAQUS_MP_MODE}}"
echo "[Stage16N-R3J] scratch=$ABAQUS_SCRATCH"

for ext in odb res stt mdl sim prt; do
  if [[ ! -e "${{OLDJOB}}.${{ext}}" ]]; then
    echo "Missing native restart source: ${{OLDJOB}}.${{ext}}" >&2
    exit 2
  fi
done

if [[ ! -f state.bin || ! -f STAGE16N_R3J_EXTRAPOLATED_STATE.md ]]; then
  rm -f state.bin state.csv STAGE16N_R3J_EXTRAPOLATED_STATE.md
  mkdir -p _jump_state
  abaqus python ../../../stage16n_extract_exact_state_for_reinjection.py \\
    --odb "${{OLDJOB}}.odb" \\
    --cycles "$PREVIOUS_CYCLE,$CHECKPOINT_CYCLE" \\
    --outdir _jump_state \\
    2>&1 | tee "$LOG_DIR/${{JOB}}_extract_slope_states.log"
  python3 ../../../stage16n_make_extrapolated_state.py \\
    --previous-csv "_jump_state/stage16n_exact_state_cycle$(printf '%04d' "$PREVIOUS_CYCLE").csv" \\
    --base-csv "_jump_state/stage16n_exact_state_cycle$(printf '%04d' "$CHECKPOINT_CYCLE").csv" \\
    --previous-cycle "$PREVIOUS_CYCLE" \\
    --base-cycle "$CHECKPOINT_CYCLE" \\
    --jump-cycles "$JUMP_CYCLES" \\
    --output-cycle "$JUMP_CYCLE" \\
    --output-csv state.csv \\
    --output-bin state.bin \\
    --output-summary STAGE16N_R3J_EXTRAPOLATED_STATE.md \\
    2>&1 | tee "$LOG_DIR/${{JOB}}_make_extrapolated_state.log"
fi

export STAGE16N_JUMP_STATE_BIN="$PWD/state.bin"
export STAGE16N_JUMP_TARGET_STEP="$TARGET_STEP"
export STAGE16N_JUMP_CHECK_TIME="$CHECKPOINT_CYCLE"

abaqus job="${{JOB}}_datacheck" input="${{JOB}}.inp" oldjob="${{OLDJOB}}" \\
  user=stage16n_r3_jump_umat.for \\
  datacheck interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="${{ABAQUS_CPUS}}" mp_mode="${{ABAQUS_MP_MODE}}" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}_datacheck.log"

abaqus job="$JOB" input="${{JOB}}.inp" oldjob="${{OLDJOB}}" \\
  user=stage16n_r3_jump_umat.for \\
  interactive ask_delete=OFF scratch="$ABAQUS_SCRATCH" \\
  cpus="${{ABAQUS_CPUS}}" mp_mode="${{ABAQUS_MP_MODE}}" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}.log"

grep "STAGE16N_R3J_OVERWRITE" "${{JOB}}.dat" \\
  > "$LOG_DIR/${{JOB}}_overwrite_trace.txt" || true
grep -m 5 -A3 "SPARSE SOLVER RUNNING ON" "${{JOB}}.msg" \\
  | tee "$LOG_DIR/${{JOB}}_parallelism_check.log" || true

abaqus python ../../../stage16n_extract_hysteresis_and_local_states.py --job "$JOB" \\
  2>&1 | tee "$LOG_DIR/${{JOB}}_extract.log"

cd "${{REPO_ROOT:-$HOME/master_thesis/Abaqus_trial}}"
CASE_DIR="runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/{case.case_id}"
python3 runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_r3j_jump_against_reference.py \\
  --jump-metrics "$CASE_DIR/${{JOB}}_cycle_metrics.csv" \\
  --jump-local-states "$CASE_DIR/${{JOB}}_selected_cycle_local_states.csv" \\
  --ref-metrics "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/{ref_metrics}" \\
  --ref-local-states "runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/{ref_local_states}" \\
  --cycles "$TARGET_CYCLE" \\
  --out-dir "$CASE_DIR" \\
  --prefix "$JOB" \\
  2>&1 | tee "$CASE_DIR/$LOG_DIR/${{JOB}}_compare.log"

cd "$CASE_DIR"
{{
  echo "# Stage 16N-R3J Jump Case Status"
  echo
  echo "- PBS job: \\`${{PBS_JOBID:-manual}}\\`"
  echo "- Abaqus job: \\`$JOB\\`"
  echo "- Oldjob: \\`$OLDJOB\\`"
  echo "- Restart checkpoint: \\`$CHECKPOINT_CYCLE\\`"
  echo "- Slope pair: \\`$PREVIOUS_CYCLE -> $CHECKPOINT_CYCLE\\`"
  echo "- Material-state jump: \\`$CHECKPOINT_CYCLE -> $JUMP_CYCLE\\`"
  echo "- Continuation target: \\`$TARGET_CYCLE\\`"
  echo "- Overwrite trigger: \\`JSTEP(1)=$TARGET_STEP, KINC=0, TIME(2)~=$CHECKPOINT_CYCLE\\`"
  echo "- Overwritten variables: \\`STATEV(1:25)\\`"
  echo "- Diagnostic/derived variables not table-overwritten: \\`STATEV(26:27)\\`"
  if [[ -f "${{JOB}}.sta" ]] && grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "${{JOB}}.sta"; then
    echo "- Solver status: \\`completed_successfully\\`"
  else
    echo "- Solver status: \\`check $JOB.sta\\`"
  fi
  if [[ -f "${{JOB}}_comparison_summary.csv" ]]; then
    tail -n +2 "${{JOB}}_comparison_summary.csv" | sed 's/^/- Comparison summary: /'
  fi
  echo "- Finished: \\`$(date '+%Y-%m-%d %H:%M:%S')\\`"
}} > STAGE16N_R3J_CASE_STATUS.md

echo "[Stage16N-R3J] end: $(date '+%Y-%m-%d %H:%M:%S')"
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_pbs(path: Path, case: RestartJumpCase) -> None:
    text = f"""#!/bin/bash
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

RUN_DIR="$REPO_ROOT/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/{case.case_id}"
cd "$RUN_DIR"
bash link_restart_sources.sh
bash run_stage16n_r3j_jump_hpc.sh
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_manifest(path: Path, case: RestartJumpCase, checkpoint_inc: int) -> None:
    text = f"""# Stage 16N-R3J Restart-Preserved Jump Case

- Case: `{case.case_id}`
- Job: `{case.job}`
- Oldjob: `{case.oldjob}`
- Restart read: `STEP={case.checkpoint_cycle}, INC={checkpoint_inc}`
- Native restart checkpoint: `{case.checkpoint_cycle}`
- Slope pair: `{case.previous_cycle} -> {case.checkpoint_cycle}`
- Jump formula: `STATEV_jump = STATEV_base + {case.jump_cycles} * dSTATEV/dN`
- Material-state jump: `{case.checkpoint_cycle} -> {case.jump_cycle}`
- Solved continuation cycles: `{case.continuation_start_cycle} -> {case.target_cycle}`
- Continuation target: `{case.target_cycle}`
- Overwrite trigger: `JSTEP(1)={case.target_step}`, `KINC=0`, `TIME(1)=0`, `TIME(2)~={case.checkpoint_cycle}`
- Overwritten variables: `STATEV(1:25)`
- Not table-overwritten: `STATEV(26:27)`
- Pass criterion: `max_primary_local_error_pct <= 5`
- Review criterion: `5 < max_primary_local_error_pct <= 10`
- Fail criterion: `max_primary_local_error_pct > 10` or solver instability
- Diagnostic-only metric: `HOLE_RING_S11_MAX_ABS`
- Production resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_compare_script(path: Path) -> None:
    text = r'''#!/usr/bin/env python3
"""Compare Stage 16N-R3J restart-preserved jumps against references."""

import argparse
import csv
from pathlib import Path


GLOBAL_FIELDS = ["U1_max", "U1_min", "RF1_max", "RF1_min", "loop_area_abs"]
PRIMARY_LOCAL_FIELDS = [
    "HOLE_RING_MISES_MAX",
    "HOLE_RING_SDV1_MAX",
    "HOLE_RING_SDV8_MAX",
    "HOLE_RING_SDV11_MAX",
]
DIAGNOSTIC_LOCAL_FIELDS = ["HOLE_RING_S11_MAX_ABS"]


def read_by_cycle(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = {int(float(row["cycle"])): row for row in reader}
    return fields, rows


def rel_pct(value, ref):
    return 100.0 * abs(value - ref) / max(abs(ref), 1.0e-12)


def compare_table(kind, fields, cycles, ref_rows, test_rows):
    rows = []
    for cycle in cycles:
        if cycle not in ref_rows:
            raise KeyError(f"Cycle {cycle} missing from reference {kind} table")
        if cycle not in test_rows:
            raise KeyError(f"Cycle {cycle} missing from jump {kind} table")
        for field in fields:
            ref_value = float(ref_rows[cycle][field])
            test_value = float(test_rows[cycle][field])
            rows.append(
                {
                    "kind": kind,
                    "cycle": str(cycle),
                    "metric": field,
                    "jump_value": "%.12g" % test_value,
                    "reference_value": "%.12g" % ref_value,
                    "error_pct": "%.8g" % rel_pct(test_value, ref_value),
                }
            )
    return rows


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def classify(max_primary_local):
    if max_primary_local <= 5.0:
        return "pass"
    if max_primary_local <= 10.0:
        return "review"
    return "fail"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jump-metrics", type=Path, required=True)
    parser.add_argument("--jump-local-states", type=Path, required=True)
    parser.add_argument("--ref-metrics", type=Path, required=True)
    parser.add_argument("--ref-local-states", type=Path, required=True)
    parser.add_argument("--cycles", required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("."))
    parser.add_argument("--prefix", default="stage16n_r3j_jump")
    args = parser.parse_args()

    cycles = [int(part.strip()) for part in args.cycles.split(",") if part.strip()]
    ref_metric_fields, ref_metrics = read_by_cycle(args.ref_metrics)
    jump_metric_fields, jump_metrics = read_by_cycle(args.jump_metrics)
    ref_local_fields, ref_local = read_by_cycle(args.ref_local_states)
    jump_local_fields, jump_local = read_by_cycle(args.jump_local_states)

    details = []
    details.extend(
        compare_table(
            kind="global_cycle_metric",
            fields=[f for f in GLOBAL_FIELDS if f in ref_metric_fields and f in jump_metric_fields],
            cycles=cycles,
            ref_rows=ref_metrics,
            test_rows=jump_metrics,
        )
    )
    details.extend(
        compare_table(
            kind="primary_local_scalar",
            fields=[f for f in PRIMARY_LOCAL_FIELDS if f in ref_local_fields and f in jump_local_fields],
            cycles=cycles,
            ref_rows=ref_local,
            test_rows=jump_local,
        )
    )
    details.extend(
        compare_table(
            kind="diagnostic_local_scalar",
            fields=[f for f in DIAGNOSTIC_LOCAL_FIELDS if f in ref_local_fields and f in jump_local_fields],
            cycles=cycles,
            ref_rows=ref_local,
            test_rows=jump_local,
        )
    )

    detail_path = args.out_dir / f"{args.prefix}_comparison_details.csv"
    write_csv(
        detail_path,
        details,
        ["kind", "cycle", "metric", "jump_value", "reference_value", "error_pct"],
    )

    max_global = max((float(r["error_pct"]) for r in details if r["kind"] == "global_cycle_metric"), default=0.0)
    max_primary_local = max(
        (float(r["error_pct"]) for r in details if r["kind"] == "primary_local_scalar"),
        default=0.0,
    )
    max_diagnostic_s11 = max(
        (
            float(r["error_pct"])
            for r in details
            if r["kind"] == "diagnostic_local_scalar" and r["metric"] == "HOLE_RING_S11_MAX_ABS"
        ),
        default=0.0,
    )
    summary_rows = [
        {
            "cycles": ",".join(str(c) for c in cycles),
            "status": classify(max_primary_local),
            "max_global_error_pct": "%.8g" % max_global,
            "max_primary_local_error_pct": "%.8g" % max_primary_local,
            "diagnostic_s11_error_pct": "%.8g" % max_diagnostic_s11,
            "details_file": detail_path.name,
        }
    ]
    summary_path = args.out_dir / f"{args.prefix}_comparison_summary.csv"
    write_csv(
        summary_path,
        summary_rows,
        [
            "cycles",
            "status",
            "max_global_error_pct",
            "max_primary_local_error_pct",
            "diagnostic_s11_error_pct",
            "details_file",
        ],
    )
    print("Wrote %s" % summary_path)
    print("Wrote %s" % detail_path)


if __name__ == "__main__":
    main()
'''
    path.write_text(text, encoding="utf-8", newline="\n")


def case_index_row(case: RestartJumpCase) -> dict[str, object]:
    checkpoint_inc = parse_checkpoint_increment(case.source_dir / f"{case.oldjob}.sta", case.checkpoint_cycle)
    return {
        "case_id": case.case_id,
        "job": case.job,
        "oldjob": case.oldjob,
        "previous_cycle": case.previous_cycle,
        "checkpoint_cycle": case.checkpoint_cycle,
        "checkpoint_inc": checkpoint_inc,
        "jump_cycles": case.jump_cycles,
        "jump_cycle": case.jump_cycle,
        "continuation_start_cycle": case.continuation_start_cycle,
        "target_cycle": case.target_cycle,
        "target_step": case.target_step,
    }


def prepare_cases(cases: tuple[RestartJumpCase, ...]) -> None:
    for required in (BASE_UMAT, EXTRACTOR, EXACT_STATE_EXTRACTOR, EXTRAPOLATOR):
        if not required.exists():
            raise FileNotFoundError(required)
    R3J_DIR.mkdir(parents=True, exist_ok=True)
    write_compare_script(STAGE_DIR / "stage16n_compare_r3j_jump_against_reference.py")
    for case in cases:
        run_dir = case.run_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_inc = parse_checkpoint_increment(case.source_dir / f"{case.oldjob}.sta", case.checkpoint_cycle)
        write_restart_deck(run_dir / f"{case.job}.inp", case, checkpoint_inc)
        write_jump_umat(run_dir / "stage16n_r3_jump_umat.for")
        write_link_script(run_dir / "link_restart_sources.sh", case)
        write_runner(run_dir / "run_stage16n_r3j_jump_hpc.sh", case)
        write_pbs(run_dir / f"submit_{case.job}.pbs", case)
        write_manifest(run_dir / "STAGE16N_R3J_CASE_MANIFEST.md", case, checkpoint_inc)
        shutil.copy2(EXTRACTOR, run_dir / EXTRACTOR.name)
        print(f"Prepared {run_dir}")
    rows = [case_index_row(case) for case in CASES]
    with (R3J_DIR / "stage16n_r3j_jump_cases.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "job",
                "oldjob",
                "previous_cycle",
                "checkpoint_cycle",
                "checkpoint_inc",
                "jump_cycles",
                "jump_cycle",
                "continuation_start_cycle",
                "target_cycle",
                "target_step",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        choices=[
            "all",
            "R3J1",
            "R3J2",
            "R3J3",
            "R3J4",
            "R3J5",
            "R3J6",
            "R3J7",
            "R3J8",
            "R4J1",
            "R4J2",
            "R4J3",
            "R4J4",
            "R4J5",
            "R4J6",
        ],
        default="all",
    )
    args = parser.parse_args()
    if args.case == "R3J1":
        selected = (CASES[0],)
    elif args.case == "R3J2":
        selected = (CASES[1],)
    elif args.case == "R3J3":
        selected = (CASES[2],)
    elif args.case == "R3J4":
        selected = (CASES[3],)
    elif args.case == "R3J5":
        selected = (CASES[4],)
    elif args.case == "R3J6":
        selected = (CASES[5],)
    elif args.case == "R3J7":
        selected = (CASES[6],)
    elif args.case == "R3J8":
        selected = (CASES[7],)
    elif args.case == "R4J1":
        selected = (CASES[8],)
    elif args.case == "R4J2":
        selected = (CASES[9],)
    elif args.case == "R4J3":
        selected = (CASES[10],)
    elif args.case == "R4J4":
        selected = (CASES[11],)
    elif args.case == "R4J5":
        selected = (CASES[12],)
    elif args.case == "R4J6":
        selected = (CASES[13],)
    else:
        selected = CASES
    prepare_cases(selected)


if __name__ == "__main__":
    main()
