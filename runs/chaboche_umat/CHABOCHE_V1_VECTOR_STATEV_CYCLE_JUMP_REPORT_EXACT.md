# Chaboche-v1 Vector STATEV Cycle-Jump Report (Exact)

This analyzer extends the validated scalar SDV1 cycle-jump postprocessor to a vector-valued STATEV diagnostic. It remains Level-2 preparation only: no Abaqus rerun, no UMAT edit, no input-file edit, and no STATEV injection.

## Inputs

- `chaboche_v1_full_statev_cycle_history_exact.csv`
- `chaboche_v1_full_statev_cycle_stability_exact.csv`

## Method

- Reference window: cycles `2-10`
- Jump base: cycle `10`
- Active vector components used for jump control: `STATEV(1), STATEV(2-4), STATEV(8-10)`
- Near-zero shear components reported only: `STATEV(5-7), STATEV(11-13)`
- Recomputable/diagnostic components reported only: `STATEV(14-15)`
- Adaptive settings: `eta=1.0`, `JUMPMIN=1`, `JUMPMAX=60`, curvature tolerance `0.01`

## Phase Consistency

- Maximum absolute cycle-end time error: `0`
- Cycle-end frames are effectively exact integer cycle times.

## Adaptive Vector Jump Control

- Conservative global DeltaN: `1`
- Adaptive target cycle: `11`
- Controlling component: `STATEV(2)` `X11`
- Controlling component prior stability class: `needs caution`

The global vector jump is the minimum candidate jump over the active components. This is more conservative than the scalar SDV1-only adaptive jump because the normal backstress and viscoplastic strain components are included in the control set.

## SDV1 Comparison

- Vector-global adaptive target cycle: `11`
- Scalar SDV1-only adaptive target cycle retained for comparison: `19`
- First-order SDV1 relative error at vector-global adaptive target: `0.0185763296123%`
- First-order SDV1 relative error at scalar SDV1-only adaptive target: `0.127282460804%`
- First-order SDV1 relative error at fixed cycle 20 target: `0.138393722167%`

## Active Component Error Summary at Adaptive Target

| STATEV | Symbol | First-order rel. error [%] | Second-order rel. error [%] | Role |
| ---: | --- | ---: | ---: | --- |
| 1 | `p` | `0.0185763296123` | `0.0116490467411` | active_vector_component |
| 2 | `X11` | `0.458188029595` | `0.194351048692` | active_vector_component |
| 3 | `X22` | `0.458188029475` | `0.194351048573` | active_vector_component |
| 4 | `X33` | `0.458188029475` | `0.194351048573` | active_vector_component |
| 8 | `Evp11` | `0.527137487888` | `0.233108838642` | active_vector_component |
| 9 | `Evp22` | `0.527137487888` | `0.233108838642` | active_vector_component |
| 10 | `Evp33` | `0.527137487888` | `0.233108838642` | active_vector_component |

## Worst Active Component at Adaptive Target

- `STATEV(9)` `Evp22`
- First-order relative error: `0.527137487888%`

## Interpretation

`STATEV(1)` remains the cleanest cycle-jump control variable. The normal backstress components `STATEV(2-4)` and normal viscoplastic strain components `STATEV(8-10)` are physically important for a future restart/injected-state continuation, but their cycle-end increments are less stable and must be handled cautiously.

For this uniaxial test, the shear components are near zero and should not control the jump. `STATEV(14)` is recomputable from `STATEV(1)` and the material constants in this UMAT, while `STATEV(15)` is diagnostic.

This result suggests that any Level-2 injection experiment should start conservatively. A scalar-only injected SDV1 test may be useful as a controlled experiment, but a physically consistent restart state will eventually require coordinated treatment of `STATEV(1-4,8-10)` at a consistent cycle phase point.

## Output Files

- `chaboche_v1_vector_statev_cycle_jump_predictions_exact.csv`
- `chaboche_v1_vector_statev_cycle_jump_errors_exact.csv`
- `chaboche_v1_vector_statev_adaptive_jump_control_exact.csv`
