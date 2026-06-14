# HPC-Only Workflow for Abaqus Trial

Date adopted: 2026-06-14

## Rule

All future repository work for this Abaqus workspace should be performed on the HPC clone by default. This includes file creation, code edits, Abaqus job preparation/submission, LaTeX report updates, commits, pushes, and routine Git inspection.

The Windows workstation should be treated as a low-frequency sync/viewer machine only, because local Codex/Git polling can spawn many small `git.exe` helpers and cause USB-display lag.

## Canonical HPC Clone

```bash
cd /scratch/$USER/git_work/Master_thesis_preparatory
git checkout copilot/curved-cephalopod
git pull --ff-only
```

Use this clone for normal work. Keep heavy Abaqus outputs in scratch/offload storage and do not commit `.odb`, `.stt`, `.sim`, `.res`, `.mdl`, `.prt`, `state.bin`, large `state.csv`, large `.msg`, or large `.dat` files.

## Windows Workstation Policy

Do not run broad Git commands in `D:\TUBAF\Master_Thesis\Abaqus_trial` during normal agent work. Avoid local `git status`, recursive searches over generated run folders, local LaTeX builds, and local staging/committing.

Use Windows only for occasional sync intervals, for example weekly or monthly, after HPC commits have been pushed to GitHub.

## Weekly or Monthly Local Sync

When the user explicitly requests a local sync, use a short targeted command window and avoid untracked enumeration:

```powershell
cd D:\TUBAF\Master_Thesis\Abaqus_trial
git fetch origin
git checkout copilot/curved-cephalopod
git pull --ff-only
git status --short --untracked-files=no
```

Close/reopen Codex after local sync if Git helper processes linger.

## HPC Submission Pattern

For R4J branch refinement jobs, prefer the scratch watchdog from the HPC clone. Example for R4J5/R4J6:

```bash
cd /scratch/$USER/git_work/Master_thesis_preparatory
CASE1_NAME=R4J5_250_to_285_solve_286_to_500 \
CASE2_NAME=R4J6_500_to_510_solve_511_to_750 \
SCRATCH_ROOT=/scratch/$USER/stage16n_scratch_runs_r4j_branch_refine \
bash runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/watch_cleanup_and_submit_stage16n_r4j_plus20_scratch_jobs.sh
```

Before submission, check `/home` and `/scratch` capacity and confirm required restart source files are available.
