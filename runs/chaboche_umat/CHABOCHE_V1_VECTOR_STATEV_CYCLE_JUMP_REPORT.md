# Chaboche-v1 Vector STATEV Cycle-Jump Report

This analyzer extends the validated scalar SDV1 cycle-jump postprocessor to a vector-valued STATEV diagnostic. It remains Level-2 preparation only: no Abaqus rerun, no UMAT edit, no input-file edit, and no STATEV injection.

## Inputs

- `chaboche_v1_full_statev_cycle_history.csv`
- `chaboche_v1_full_statev_cycle_stability.csv`

## Method

- Reference window: cycles `2-10`
- Jump base: cycle `10`
- Active vector components used for jump control: `STATEV(1), STATEV(2-4), STATEV(8-10)`
- Near-zero shear components reported only: `STATEV(5-7), STATEV(11-13)`
- Recomputable/diagnostic components reported only: `STATEV(14-15)`
- Adaptive settings: `eta=1.0`, `JUMPMIN=1`, `JUMPMAX=60`, curvature tolerance `0.01`

## Phase Consistency

- Maximum absolute cycle-end time error: `0.00974273681641`
- Warning: cycle-end frames are nearest available ODB frames, not exactly integer cycle times. This matters especially for backstress and viscoplastic strain components.

## Adaptive Vector Jump Control

- Conservative global DeltaN: `2`
- Adaptive target cycle: `12`
- Controlling component: `STATEV(2)` `X11`
- Controlling component prior stability class: `needs caution`

The global vector jump is the minimum candidate jump over the active components. This is more conservative than the scalar SDV1-only adaptive jump because the normal backstress and viscoplastic strain components are included in the control set.

## SDV1 Comparison

- Vector-global adaptive target cycle: `12`
- Scalar SDV1-only adaptive target cycle retained for comparison: `19`
- First-order SDV1 relative error at vector-global adaptive target: `0.0118027922862%`
- First-order SDV1 relative error at scalar SDV1-only adaptive target: `0.0600848519171%`
- First-order SDV1 relative error at fixed cycle 20 target: `0.0674109657445%`

## Active Component Error Summary at Adaptive Target

| STATEV | Symbol | First-order rel. error [%] | Second-order rel. error [%] | Role |
| ---: | --- | ---: | ---: | --- |
| 1 | `p` | `0.0118027922862` | `0.0125388848447` | active_vector_component |
| 2 | `X11` | `0.427408706426` | `0.0419307118442` | active_vector_component |
| 3 | `X22` | `0.427408706426` | `0.0419307118441` | active_vector_component |
| 4 | `X33` | `0.427408706426` | `0.0419307118441` | active_vector_component |
| 8 | `Evp11` | `0.202728724628` | `0.0200038057079` | active_vector_component |
| 9 | `Evp22` | `0.202728724739` | `0.0200038055965` | active_vector_component |
| 10 | `Evp33` | `0.202728724739` | `0.0200038055965` | active_vector_component |

## Worst Active Component at Adaptive Target

- `STATEV(2)` `X11`
- First-order relative error: `0.427408706426%`

## Interpretation

`STATEV(1)` remains the cleanest cycle-jump control variable. The normal backstress components `STATEV(2-4)` and normal viscoplastic strain components `STATEV(8-10)` are physically important for a future restart/injected-state continuation, but their cycle-end increments are less stable and must be handled cautiously.

For this uniaxial test, the shear components are near zero and should not control the jump. `STATEV(14)` is recomputable from `STATEV(1)` and the material constants in this UMAT, while `STATEV(15)` is diagnostic.

This result suggests that any Level-2 injection experiment should start conservatively. A scalar-only injected SDV1 test may be useful as a controlled experiment, but a physically consistent restart state will eventually require coordinated treatment of `STATEV(1-4,8-10)` at a consistent cycle phase point.

## Output Files

- `chaboche_v1_vector_statev_cycle_jump_predictions.csv`
- `chaboche_v1_vector_statev_cycle_jump_errors.csv`
- `chaboche_v1_vector_statev_adaptive_jump_control.csv`
