# Stage 16N-R4J Scratch-Based Submission Setup

Date: 2026-06-12

## Purpose

R4J1/R4J2 are the corrected +50 restart-preserved state-jump cases intended to test actual cycle skipping. Unlike the earlier R3J7/R3J8 prepared decks, these decks restart from the native checkpoint, overwrite the material memory at the first continuation increment, and then solve only the post-jump cycle labels.

## Corrected Cases

| Case | Restart checkpoint | Material-state jump | Solved continuation cycles | Endpoint |
|---|---:|---:|---:|---:|
| R4J1 | 250 | 250 -> 300 | 301 -> 500 | 500 |
| R4J2 | 500 | 500 -> 550 | 551 -> 750 | 750 |

The generated decks start with:

- R4J1: `*STEP, NAME=CYCLE_0301`
- R4J2: `*STEP, NAME=CYCLE_0551`

The UMAT overwrite trigger remains the first restart-continuation step:

- R4J1: `JSTEP(1)=251`, `KINC=0`
- R4J2: `JSTEP(1)=501`, `KINC=0`

## Scratch Watchdog

The scratch watchdog was installed and started on the HPC:

- Script: `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/watch_cleanup_and_submit_stage16n_scratch_jobs.sh`
- HPC background PID: `2444124`
- Start time: Fri Jun 12 12:24:22 CEST 2026
- Log: `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/scratch_auto_submit_R4J1_250_to_300_solve_301_to_500_R4J2_500_to_550_solve_551_to_750.log`
- Nohup log: `~/watch_cleanup_and_submit_stage16n_scratch_jobs.nohup.log`

At startup, the watchdog correctly detected that the R3J5/R3J6 `.stt` offload was still running:

```text
Cleanup/offload still running. Waiting...
2397333 python3 /tmp/offload_r3j5_r3j6_stt.py
```

## Scratch Execution Design

The watchdog stages a lightweight repo-shaped tree to:

```text
/scratch/pr21vyci/stage16n_scratch_runs/Abaqus_trial
```

Each PBS job then runs from the scratch case directory, links native restart sources there, sets `REPO_ROOT` to the scratch repo path, and stages only lightweight evidence back to `/home`.

Heavy Abaqus outputs are excluded from `/home` stage-back:

```text
*.odb, *.stt, *.res, *.sim, *.mdl, *.prt, state.bin, state.csv
```

## Current Status

The first scratch-submission attempt failed because PBS rejected a script submitted directly from `/scratch`:

```text
qsub: Unauthorized Request
```

The watchdog was corrected so that PBS wrapper files are written and submitted from the `/home` case folders while the job itself changes directory to the scratch case folder before running Abaqus. A second staging correction narrowed scratch staging to only the required case folders, helper scripts, reference CSV files, and restart-source symlinks. The active scratch root is now:

```text
/scratch/pr21vyci/stage16n_scratch_runs_r4j_v2/Abaqus_trial
```

The final submission issue was a missing queue directive. Adding `#PBS -q entry_teachingq` matched the accepted Stage 16N PBS pattern and allowed submission.

The corrected watchdog submitted both jobs on Sat Jun 13 06:01 CEST 2026:

| Case | PBS job | State at check | Queue | Host | Start time |
|---|---|---|---|---|---|
| R4J1 | `1344946.mmaster02` | R | teachingq | mnode100 | Sat Jun 13 06:01:25 2026 |
| R4J2 | `1344947.mmaster02` | R | teachingq | mnode101 | Sat Jun 13 06:01:26 2026 |

Requested resources for each job are `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, with `walltime=24:00:00`.
