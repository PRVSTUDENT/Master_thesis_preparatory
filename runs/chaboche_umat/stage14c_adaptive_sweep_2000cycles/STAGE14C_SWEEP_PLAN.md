# Stage 14C Adaptive Sweep Plan

Stage 14C is a configurable sweep campaign derived from Stage 14B. The first submitted job is intentionally a short sanity run, not the 20-24 hour campaign.

## Safety Gate

The default PBS script runs with:

```text
SANITY_ONLY=1
walltime=00:30:00
```

This executes one complete Stage 14C block:

```text
case S00
DN_MIN=1
DN_MAX=25
RECOVERY_WINDOW=10
LOCAL_TOL=0.001
SAFETY_FACTOR=0.70
```

The sanity job must pass:

1. Python syntax compilation.
2. Block generation.
3. Abaqus datacheck.
4. One short Abaqus/Standard recovery analysis.
5. Postprocessing.
6. Summary/report update.

Only after that should the long sweep be submitted with `SANITY_ONLY=0` and a 24 hour walltime.

## Current Priority Cases

The first long sweep script currently prioritizes:

```text
B1, B2, B3
C1, C2, C5, C6
D2, D4
```

These cases test whether removing the hard `DN_MIN=25` failure mode, shortening `DN_MAX`, and increasing recovery windows stabilize the route before implementing the more expensive diagnostic variants.

## Baselines

```text
Stage 14 fixed best: jump25, STATEV1 error about 2.85226684954%
Stage 14B adaptive: STATEV1 error 124.209089872%
```

## Expected Output Files

```text
STAGE14C_SWEEP_MASTER_SUMMARY.csv
STAGE14C_SWEEP_CASE_SUMMARY.csv
STAGE14C_SWEEP_BLOCK_HISTORY.csv
STAGE14C_SWEEP_REPORT.md
```

Large Abaqus solver files must not be committed.
