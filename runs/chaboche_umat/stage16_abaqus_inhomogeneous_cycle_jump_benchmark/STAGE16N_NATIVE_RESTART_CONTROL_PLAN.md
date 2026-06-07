# Stage 16N-R1 Native Abaqus Restart Control Plan

## Objective

Stage 16N-R repairs the failed later-cycle reinjection strategy. The new direction is to stop rebuilding the full finite-element state from scratch with `SDVINI`/`SIGINI` and instead preserve Abaqus' displacement, strain, equilibrium, and solver-history state through native restart.

The first control test is:

```text
native restart cycle 250 -> cycle 500
native restart cycle 500 -> cycle 1000
```

This separates two questions:

```text
Can Abaqus itself restart the inhomogeneous plate-with-hole model cleanly?
Is the failure specific to scratch SDVINI/SIGINI state injection?
```

## Current Restart-File Check

The local Stage 16N workspace currently has no visible `.res` restart files for the completed 1000-cycle reference. Therefore, the existing completed reference should be treated as a comparison target, not as a restart source.

## Required Setup

Create a restart-enabled reference or checkpoint run with native restart output at:

```text
cycle 100
cycle 250
cycle 500
```

The checkpoint run should preserve:

```text
nodal displacement field
compatible strain field
internal force equilibrium state
solver restart history
material STATEV history
```

## R1 Pass Criteria

The native restart control passes if:

```text
restart 250 -> 500 completes normally
restart 500 -> 1000 completes normally
comparison against the continuous 1000-cycle reference is within the normal no-jump/restart tolerance
```

If R1 passes, the FE restart mechanism is sound and the old failure is attributable to scratch manual reinjection. If R1 fails, repair the Abaqus restart/output setup before writing any restart-preserved jump UMAT.

## Follow-On Stage 16N-R2

Only after R1 passes, test a restart-preserved material-memory overwrite:

```text
restart from cycle 250
overwrite only independent material memory variables inside UMAT
continue to cycle 500
```

The first overwrite should be an exact no-op-style test using exact cycle-250 values, followed by a small repaired jump such as 250 -> 255 -> 500.

## Do Not Do

Do not submit more B2/B3/B3SAFE/B4SAFE jobs using the old scratch `SDVINI`/`SIGINI` route. The existing diagnostics already show that this path fails before valid physical continuation at cycle 250/500.
