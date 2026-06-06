# Stage 16N-C Fixed State-Initialized Cycle-Jump Validation Plan

Last updated: 2026-06-06

## Purpose

Stage 16N-C begins practical fixed cycle-jump validation after the Stage 16N-B0 reinjection audit. The method is now framed as:

```text
fixed state-initialized cycle-jump validation
```

not:

```text
exact restart cycle-jump validation
```

The distinction matters because the B0 initialization audit showed a local reinjection error floor for strain-like state variables, especially `HOLE_RING_SDV8_MAX`.

## First gate

Run only one conservative fixed-jump case first:

```text
B1_100_to_125_to_250
base state:        cycle 100
jump target:       cycle 125
comparison target: cycle 250
skipped cycles:    101-125
normal cycles:     126-250
```

This case uses the same final comparison cycle as B0-1, so the B0-1 result can be used as the reinjection baseline.

## Initial jump approximation

The first scaffold uses a conservative zero-order state approximation:

```text
state at cycle 125 is initialized from the exact cycle-100 state
```

This intentionally does not claim a sophisticated extrapolation. Its purpose is to measure the additional error caused by skipping 25 cycles on top of the already measured `SDVINI/SIGINI` reinjection floor.

## Primary pass/fail metrics

Use these as primary metrics:

```text
RF1 max/min error
loop area error
global hysteresis loop shape
HOLE_RING_SDV1_MAX
HOLE_RING_MISES_MAX
HOLE_RING_S11_MAX_ABS
```

Use these as diagnostic-only metrics:

```text
HOLE_RING_SDV8_MAX
other strain-like STATEV components affected immediately by initialization
```

## Error interpretation

For the B1 case, report:

```text
total fixed-jump error against the 1000-cycle reference
B0-1 state-initialized baseline error
additional fixed-jump error relative to the B0-1 baseline
```

Do not overclaim exact subtraction if the error signs or local controlling locations differ.

## Execution sequence

From the repository root on HPC:

```bash
cd ~/master_thesis/Abaqus_trial
python runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_prepare_fixed_jump_cases.py --cases B1_100_to_125_to_250
bash runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/run_stage16n_fixed_jump_cases_hpc.sh B1_100_to_125_to_250
abaqus python runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_compare_fixed_jumps_against_1000ref.py --cases B1_100_to_125_to_250
```

If B1 gives acceptable global errors and controlled primary local-state errors, then prepare the next fixed cases:

```text
250 -> 300, continue to 500
500 -> 575, continue to 750 or 1000
750 -> 850, continue to 1000
```
