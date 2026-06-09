# Stage 16N-R2 Native Restart Control Result

## Objective

Stage 16N-R2 tests native Abaqus restart continuation with no UMAT overwrite and no `SDVINI`/`SIGINI` scratch reinjection.

The two control cases are:

```text
R2C1: restart from cycle 100, continue to cycle 250
R2C2: restart from cycle 250, continue to cycle 500
```

## Scientific Gate

This stage answers whether Abaqus can restart the inhomogeneous plate-with-hole model from its own restart files while preserving the finite-element displacement, strain, equilibrium, solver-history, and material state.

If R2 passes, the earlier cycle-250 failure is attributable to scratch `SDVINI`/`SIGINI` reinjection rather than to the material model or geometry.

## Preparation Status

Prepared cases:

```text
stage16n_restart_control/native_restart_cases/R2C1_100_to_250
stage16n_restart_control/native_restart_cases/R2C2_250_to_500
```

Checkpoint increments are parsed from the completed R1 `.sta` files:

```text
cycle 100 -> step 100, inc 53
cycle 250 -> step 250, inc 58
```

## Submission Status

The corrected native restart jobs were submitted and ran on the TU Freiberg PBS cluster:

```text
R2C1: 1341284.mmaster02, restart 100 -> 250
R2C2: 1341285.mmaster02, restart 250 -> 500
```

Both PBS jobs ended with `Exit_status = 1`, but both Abaqus `.sta` files ended with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`. The nonzero PBS status is therefore classified as a wrapper/postprocessing failure, not as a native restart solver failure.

## Results

Follow-up extraction and comparison completed successfully.

| Case | Cycle checked | Solver status | Postprocess status | Scientific status | Max global error | Max primary local error |
|---|---:|---|---|---|---:|---:|
| `R2C1` | 250 | `completed_successfully` | `completed_successfully` | `pass` | 0% | 0% |
| `R2C2` | 500 | `completed_successfully` | `completed_successfully` | `pass` | 0% | 0% |

The native restart control gate passes scientifically: Abaqus can restart the inhomogeneous plate-with-hole model from its own restart files and reproduce the 1000-cycle reference at the checked continuation endpoints.

This confirms that the earlier later-cycle failures are attributable to scratch `SDVINI`/`SIGINI` reinjection rather than to the material model, geometry, or Abaqus native restart mechanics.
