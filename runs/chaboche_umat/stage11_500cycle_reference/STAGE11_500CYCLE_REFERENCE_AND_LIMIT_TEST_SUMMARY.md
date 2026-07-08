# Stage 11: 500-Cycle Reference and Extreme Long-Jump Limit Test

## Purpose

Stage 11 extends the Chaboche UMAT cycle-jump validation to a 500-cycle no-skip Abaqus reference and tests an extreme manually selected long-horizon predicted-state jump.

This is not an adaptive-controller-selected jump. It is a deliberate limit test to investigate stability and error accumulation far beyond the Stage 7B adaptive recommendation.

## Stage 11A: 500-Cycle No-Skip Reference

A new isolated 500-cycle Abaqus reference was generated.

Main settings:
- Step time: 500.0
- Cyclic amplitude: 500 cycles
- INC limit: 60000
- Maximum increment size: 0.02
- No TIME MARKS=YES introduced
- Same general Chaboche UMAT used

Abaqus status:
- Datacheck: completed
- Full analysis: completed
- Final `.sta`: THE ANALYSIS HAS COMPLETED SUCCESSFULLY

Cycle-500 reference values:
- STATEV1 = 3.463043212890625
- S11 = 351.0212707519531 MPa
- RIGHT_FACE RF1 = 1404.0850830078125

ODB size:
- 365,482,912 bytes

## Stage 11B: Predicted Cycle-499 to Cycle-500 Limit Test

Route:

cycle 10 -> predicted cycle 499 -> cycle 500

This corresponds to:
- DeltaN_test = 489
- Skipped intermediate FE cycles = 488

Before Abaqus continuation, the predicted cycle-499 state already showed large mismatch:
- STATEV1 relative error against exact cycle 499 = 3.6918279426%
- S11 relative error against exact cycle 499 = 59.109783072%

Therefore, Stage 11B is a severe over-jump / limit case.

## Injection Check

The injected values were imposed correctly:
- First-frame STATEV1 absolute error = 7.96278540882e-08
- First-frame S11 absolute error = 1.0172005716e-05 MPa

## Final Cycle-500 Comparison

Against the 500-cycle no-skip Abaqus reference:
- Final STATEV1 relative error = 3.69823703261%
- Final S11 relative error = 0.937215409313%
- Final RIGHT_FACE RF1 relative error = 0.937215409313%

Stage 11B outcome:
- not_accepted

## Interpretation

Stage 11B remained numerically stable and completed successfully. The stress and reaction force recovered surprisingly well from a very poor injected stress state, ending below 1% error.

However, the accumulated viscoplastic strain error remained above the 1% acceptance threshold. Therefore, the jump is not accepted as a valid accelerated cycle-jump result.

The practical accepted jump limit for the current first-order prediction method lies between:
- accepted Stage 10B: 88 skipped cycles
- rejected Stage 11B: 488 skipped cycles

## Recommended Next Step

Use the existing 500-cycle reference to bracket the acceptance limit:

1. Validate cycle 10 -> predicted cycle 199 -> cycle 200.
2. Validate cycle 10 -> predicted cycle 299 -> cycle 300.
3. Validate cycle 10 -> predicted cycle 399 -> cycle 400.

This is more informative than immediately jumping to 1000 cycles, because the 500-cycle extreme jump already exceeded the STATEV1 accuracy threshold.
