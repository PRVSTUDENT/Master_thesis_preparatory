# Stage 16N R4E2 / 505 Candidate Provenance Review

Reviewed: 2026-06-22

No solver job was submitted for this review.

## Candidate

Base path:

`/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source`

Observed heavy restart files:

- `.stt`: 4.9G
- `.res`: 1.2M
- `.mdl`: 13M
- `.prt`: 2.0K

Supporting evidence:

- `.inp`: 1.4K
- `.sta`: 23K
- `.dat`: 1.7M
- `.msg`: 2.7M
- `.log`: available in the R4E2 `_logs` folder

## Provenance Questions

### Did it really finish through cycle 505?

Yes.

The `.sta` tail reaches `CYCLE_0505` and ends with:

```text
THE ANALYSIS HAS COMPLETED SUCCESSFULLY
```

The `.msg`/Abaqus summary reports:

```text
RESTART INFORMATION WRITTEN IN STEP 505 AFTER INCREMENT 54
THE ANALYSIS HAS BEEN COMPLETED
0 ERROR MESSAGES
Abaqus JOB stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source COMPLETED
```

### Was it native/exact, not generated-buffer/source-split?

Yes, with an important classification nuance.

The input deck identifies itself as:

```text
Stage 16N-R4E exact-target source continuation
Native restart solve to the exact target cycle used only to extract STATEV payload.
```

The deck starts from an existing long-reference restart record:

```text
*RESTART, READ, STEP=500, INC=65
```

It then solves native continuation steps:

```text
CYCLE_0501
CYCLE_0502
CYCLE_0503
CYCLE_0504
CYCLE_0505
```

It is therefore not a generated-buffer/source-split R4I/R4I-R branch. It is also not the same as the 250-branch deck-clone/truncate method: it is an older R4E exact-target native source solve from cycle 500 to 505.

### Does the `.sta` show clean source completion?

Yes. The `.sta` shows completion through cycle 505 and successful analysis completion. The `.msg` summary reports zero error messages and restart information written at step 505 increment 54.

### Is it suitable as a restart source for `505 -> 750`?

Provisionally yes for a validation controller, but not as proof that the 505 branch is solved.

Accepted use:

- Use as the existing source for `R4K2B_505candidate_validation_controller`.
- Do not generate a new source `.stt`.
- Run a `505 -> 750` continuation with `*RESTART, READ` only and no continuation restart writes.
- Extract and compare immediately.
- Copy only lightweight evidence.
- Delete heavy continuation outputs after classification.

Not accepted as:

- A validated deck-clone/truncate source.
- Evidence that the 505 branch passes.
- Permission to run R4J9/R4J10 or a broad true-jump batch.

## Classification

The R4E2 505 candidate is classified as:

```text
provisionally valid native/exact cycle-505 restart source candidate
```

It is suitable for the storage-light `R4K2B_505candidate_validation_controller`, subject to a fresh `/scratch9/pr21vyci` audit before submission. The validation controller itself is still required to determine whether the 505--750 branch can pass.

## Next Gate

Before any solver submission:

1. Confirm `/scratch9/pr21vyci` remains below the storage-light warning level.
2. Confirm `STAGE16N_HEAVY_RETENTION_MANIFEST.md` is current.
3. Prepare the R4K2B controller so the continuation does not write restart files and cleans heavy output after lightweight evidence is copied.
4. Keep R4J9/R4J10 blocked.

