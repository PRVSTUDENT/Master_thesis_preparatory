# Chaboche-v1 Exact Phase Output Preparation Report

This report documents a copied Abaqus input deck prepared for exact cycle-end field output. It is a preparation step before repeating full STATEV extraction and vector-valued cycle-jump analysis.

## Files

- Source input deck: `chaboche_vp_v1_cyclic_eps005_20cycles.inp`
- Copied exact-output deck: `chaboche_vp_v1_cyclic_eps005_20cycles_exact_cycle_outputs.inp`

The original input deck was not modified.

## Why Exact Phase-Point Output Is Needed

The previous full STATEV extraction used the nearest available ODB frame to each integer cycle-end time. The maximum absolute time error was:

- `0.00974273681641`

This is acceptable for preliminary postprocessing, but it is not ideal for full internal-state cycle jumping. Backstress components `STATEV(2-4)` and viscoplastic strain components `STATEV(8-10)` are phase-sensitive, so a small offset from the intended cycle-end point can change the apparent cycle-to-cycle increments.

## Output-Control Change

The copied deck replaces increment-frequency output with time-marked output:

```text
*OUTPUT, FIELD, TIME INTERVAL=1.0, TIME MARKS=YES
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, SDV

*OUTPUT, HISTORY, TIME INTERVAL=1.0, TIME MARKS=YES
*NODE OUTPUT, NSET=RIGHT_FACE
U1, RF1
```

This requests output at integer step times `1, 2, ..., 20` for the 20-cycle step.

## Preserved Model Content

- Geometry: unchanged
- Material constants: unchanged
- UMAT expectation: unchanged
- Boundary conditions: unchanged
- Amplitude definition: unchanged
- Total step time: unchanged
- Number of cycles: unchanged

## Status

- Abaqus was not run automatically.
- The UMAT was not modified.
- The original input deck was not modified.
- No STATEV injection is attempted.

## Implication

This prepares a cleaner reference ODB with exact cycle-end field output. After running the copied deck, the full STATEV extraction and vector-valued STATEV cycle-jump analyzer should be repeated to remove phase-point ambiguity before any restart or injected-state Abaqus continuation is attempted.
