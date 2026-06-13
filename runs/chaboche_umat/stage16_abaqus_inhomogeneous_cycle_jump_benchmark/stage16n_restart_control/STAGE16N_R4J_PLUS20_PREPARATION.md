# Stage 16N-R4J True-Skip +20 Preparation

Prepared on 2026-06-13 after the R4J +50 true-skip jobs completed successfully as Abaqus solves but failed the local accuracy criterion.

## Scientific status before this preparation

- R3J is overwrite validation, not acceleration validation.
- R4J is true cycle-skip acceleration validation.
- R4J +50 demonstrated that the true-skip machinery is computationally functional, but the jump size is too large for the current local error tolerance.
- The current true-skip safe jump size is not yet established.

## Prepared cases

| Case | Restart/base cycle | Material-state jump target | First solved cycle | Final cycle | True skipped cycles |
|---|---:|---:|---:|---:|---:|
| R4J3 | 250 | 270 | 271 | 500 | 20 |
| R4J4 | 500 | 520 | 521 | 750 | 20 |

Generated folders:

- `restart_jump_cases/R4J3_250_to_270_solve_271_to_500/`
- `restart_jump_cases/R4J4_500_to_520_solve_521_to_750/`

Deck verification:

- R4J3 starts with `*STEP, NAME=CYCLE_0271`.
- R4J4 starts with `*STEP, NAME=CYCLE_0521`.
- The skipped cycles `251--270` and `501--520` are not solved in these continuation decks.

## Scratch submission script

Dedicated scratch watchdog:

- `restart_jump_cases/watch_cleanup_and_submit_stage16n_r4j_plus20_scratch_jobs.sh`

This follows the same storage rule as the R4J +50 jobs: PBS wrappers are submitted from `/home`, while Abaqus runs in `/scratch/pr21vyci/stage16n_scratch_runs_r4j_plus20/Abaqus_trial`. Only lightweight evidence should be copied back after completion.

## Submission status

Not submitted from the local workstation at preparation time because SSH could not resolve the HPC login host:

```text
ssh: Could not resolve hostname mlogin01.hrz.tu-freiberg.de: No such host is known.
```

Before submission, rerun the storage gate:

```bash
qstat -u pr21vyci
df -h /home /scratch
du -sh /home/pr21vyci
find ~/master_thesis/Abaqus_trial -type f \( \
  -name "*.odb" -o -name "*.stt" -o -name "*.res" -o -name "*.sim" -o \
  -name "*.mdl" -o -name "*.prt" -o -name "state.bin" -o -name "state.csv" \
\) -size +10G -print
```

Then upload the new/changed files and run:

```bash
cd ~/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases
bash watch_cleanup_and_submit_stage16n_r4j_plus20_scratch_jobs.sh
```

## Decision rule after completion

- If true-skip +20 passes: test +30 or +35.
- If true-skip +20 fails: test +10.
- If true-skip +20 is review: refine between +10 and +20.
