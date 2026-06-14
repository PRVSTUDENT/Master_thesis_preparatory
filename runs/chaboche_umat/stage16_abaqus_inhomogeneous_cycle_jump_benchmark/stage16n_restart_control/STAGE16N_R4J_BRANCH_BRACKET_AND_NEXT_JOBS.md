# Stage 16N-R4J Branch Bracket and Next Jobs

Date: 2026-06-14 Europe/Berlin

## Evidence Separation

The Stage 16N restart evidence must be separated into three distinct types.

1. R3J restart-preserved overwrite validation:
   - R3J +5, +10, and +20 passed with zero endpoint errors.
   - These cases validate stable restart-preserved UMAT material-memory overwrite.
   - They are not true cycle-skip acceleration evidence, because their continuation decks still solved all intermediate load cycles.

2. R4J +50 true-skip boundary test:
   - R4J1 and R4J2 used corrected continuation decks that start after the jumped material-state cycle.
   - Both jobs completed as Abaqus analyses, so the true-skip machinery works.
   - Both failed the local accuracy gate, so +50 is outside the safe range for both tested branches.

3. R4J +20 true-skip refinement:
   - R4J3, 250 -> 270 -> 500, passed.
   - R4J4, 500 -> 520 -> 750, failed due to local hole-ring error.
   - The safe true-skip range is therefore branch dependent.

## Branch-Specific Bracket

| Branch | Known pass | Known fail | Current bracket |
|---|---:|---:|---|
| Base cycle 250 | +20 | +50 | Safe Delta N is between 20 and 50 |
| Base cycle 500 | none yet for true skip | +20 and +50 | Safe Delta N is below 20 |

This is scientifically useful because it shows later cycles are not automatically safer in the inhomogeneous plate-with-hole benchmark. The local hole-ring variables still control the acceptable jump size.

## Thesis-Safe Conclusion

The first true cycle-skip refinement showed branch-dependent behavior. A +20 skip from cycle 250 to 270 passed the accuracy criterion, whereas the corresponding +20 skip from cycle 500 to 520 failed due to local hole-ring error. Therefore, the restart-preserved true-skip machinery is functional, but the safe jump size must be chosen adaptively and locally rather than assumed constant across the simulation.

## Prepared Next Jobs

The next two jobs refine the two branches separately rather than repeating the same jump size at both locations.

| Case | Restart checkpoint | Material-state jump | Solved continuation cycles | Endpoint | Purpose |
|---|---:|---:|---:|---:|---|
| R4J5 | 250 | 250 -> 285 | 286--500 | 500 | Refine the passing 250-branch between +20 and +50 |
| R4J6 | 500 | 500 -> 510 | 511--750 | 750 | Test whether the later 500-branch has a safe jump below +20 |

R4J5 uses +35 as the recommended midpoint refinement. A more conservative alternate early-branch probe would be 250 -> 280 -> 500, but it was not generated in this batch.

## Decision Rule After R4J5/R4J6

- If R4J5 +35 passes, test +42 or +45 for the 250 branch.
- If R4J5 +35 fails, test +27 or +30 for the 250 branch.
- If R4J6 +10 passes, the 500 branch safe range is between +10 and +20; next test +15.
- If R4J6 +10 fails, the 500 branch safe range is below +10; next test +5.

## Submission Command

Use the existing scratch watchdog with case overrides:

```bash
CASE1_NAME=R4J5_250_to_285_solve_286_to_500 \
CASE2_NAME=R4J6_500_to_510_solve_511_to_750 \
SCRATCH_ROOT=/scratch/$USER/stage16n_scratch_runs_r4j_branch_refine \
bash runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/watch_cleanup_and_submit_stage16n_r4j_plus20_scratch_jobs.sh
```

Before submission, rerun the storage gate and confirm the restart source files are still available from `/home` or linked into scratch.
