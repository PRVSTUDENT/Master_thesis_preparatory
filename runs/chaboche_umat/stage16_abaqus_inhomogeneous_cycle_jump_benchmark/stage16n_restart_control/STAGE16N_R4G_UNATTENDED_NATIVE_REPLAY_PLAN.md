# Stage 16N R4G Unattended Native Replay Plan

Updated: 2026-06-17.

## Purpose

R4G is a two-day unattended diagnostic batch to resolve the mixed R4F result before any additional extrapolated refinement. R4J9/R4J10 remain on hold.

The batch separates:

- direct native restart behavior from the original restart reference,
- source-split replay behavior,
- 250-branch behavior at cycles 270 and 280,
- 500-branch direct restart behavior.

## Cases

| Case | Mode | Restart chain | First solved cycle | Final cycle | Purpose |
|---|---|---|---:|---:|---|
| R4G1 | direct original | 250 -> 500 | 251 | 500 | current-pipeline baseline; should pass |
| R4G2 | direct original | 270 -> 500 | 271 | 500 | check direct restart behavior from cycle 270 if available in original restart files |
| R4G3 | direct original | 280 -> 500 | 281 | 500 | isolate why the target-280 branch failed |
| R4G4 | source split | source 250 -> 270, restart 270 -> 500 | 271 | 500 | compare with the R4J3 +20 pass branch |
| R4G5 | source split | source 250 -> 280, restart 280 -> 500 | 281 | 500 | repeat the R4F1 branch with standalone audit outputs |
| R4G6 | direct original | 500 -> 750 | 501 | 750 | direct native restart baseline for the 500 branch |

The original R1A restart deck is known to have explicit restart writes at 100, 250, and 500. R4G2/R4G3 intentionally test whether direct reads from cycle 270/280 are usable from the retained restart files; if they fail at datacheck before solving, classify that as restart-record availability/setup evidence rather than a physical comparison failure.

## Submission order

1. R4G1 direct 250 -> 500.
2. R4G3 direct 280 -> 500.
3. R4G2 direct 270 -> 500.
4. R4G6 direct 500 -> 750.
5. R4G4 source split 250 -> 270 -> 500.
6. R4G5 source split 250 -> 280 -> 500.

Each PBS job uses:

```text
queue=teachingq
select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
walltime=24:00:00
```

## Interpretation

- If R4G1 passes but R4G3 fails, direct restart at cycle 280 or comparison at target 280 is problematic.
- If R4G3 passes but R4G5 fails, source-split generation 250 -> 280 is the issue.
- If R4G3 and R4G5 both fail, audit reference/comparison mapping or local-state extraction for cycle 500.
- If R4G1/R4G2/R4G3 all pass, native restart is fine; then R4F1 failure was caused by source/restart-file selection in that earlier case.
- If R4G6 passes, direct native restart 500 -> 750 is okay; R4F2 review is likely caused by the 500 -> 505 source split or target-505 restart source.
- If R4G6 fails, the 500-branch comparison or restart baseline itself is not clean.

## Evidence policy

Copy only lightweight evidence after completion:

- `STAGE16N_R4G_CASE_STATUS.md`
- `*_comparison_summary.csv`
- `*_comparison_details.csv`
- `*_cycle_metrics.csv`
- `*_selected_cycle_local_states.csv`
- `*_selected_cycle_loops.csv`
- `*.sta`
- PBS stdout `*.o<jobid>`
- `qstat_<jobid>_finished_full.txt`
- small `_logs/`

Do not copy heavy Abaqus artifacts:

- `.odb`
- `.stt`
- `.res`
- `.sim`
- `.mdl`
- `.prt`
- `state.bin`
- large `state.csv`
