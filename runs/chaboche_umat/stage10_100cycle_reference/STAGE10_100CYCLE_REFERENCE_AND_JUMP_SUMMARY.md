# Stage 10: 100-Cycle Reference and Long-Jump Validation Summary

## Purpose

Stage 10 extends the Chaboche UMAT cycle-jump validation from the 50-cycle reference range to a 100-cycle no-skip Abaqus reference. The goal is to test whether a much larger predicted-state FE jump remains valid.

## Stage 10A: 100-Cycle No-Skip Reference

A new isolated 100-cycle Abaqus reference was generated from the existing 50-cycle deck.

Main settings:
- Step time extended from 50.0 to 100.0
- Cyclic amplitude extended to 100 cycles
- Increment limit increased from INC=6000 to INC=12000
- Maximum increment size kept at 0.02
- No TIME MARKS=YES was introduced
- Same general Chaboche UMAT was used

The Abaqus datacheck and full analysis both completed successfully.

Final reference values at cycle 100:
- STATEV1 = 0.712048649788
- S11 = 371.760040283 MPa
- RIGHT_FACE RF1 = 1487.04016113

## Stage 10B: Predicted Cycle-99 to Cycle-100 Jump

The predicted-state continuation route was:

cycle 10 -> predicted cycle 99 -> cycle 100

This corresponds to:
- DeltaN = 89
- Skipped intermediate FE cycles = 88

Before the Abaqus continuation, the predicted cycle-99 state showed:
- STATEV1 relative error against exact cycle 99 = 0.681765687914%
- S11 relative error against exact cycle 99 = 10.2322851886%

The high predicted S11 error indicated that this was an aggressive long-jump test.

## Injection Check

The injected state was reproduced accurately in the first output frame:
- First-frame STATEV1 absolute error = 2.32838248682e-09
- First-frame S11 absolute error = 3.3911667856e-06 MPa

## Final Cycle-100 Validation

Against the 100-cycle no-skip Abaqus reference:
- Final STATEV1 relative error = 0.667869616047%
- Final S11 relative error = 0.0713767788476%
- Final RIGHT_FACE RF1 relative error = 0.0713767788476%

Stage 10B outcome:
- accepted_clean_success

## Interpretation

Stage 10B shows that the direct prediction error at the injected target state does not necessarily equal the final continuation error after one computed Abaqus cycle. Although the predicted cycle-99 S11 differed from the exact cycle-99 reference by about 10.23%, the continuation from cycle 99 to cycle 100 recovered the final stress and reaction force response very accurately.

The accumulated viscoplastic strain error remained below 1%, while the final S11 and RF1 errors were below 0.1%. This makes Stage 10B the largest validated cycle jump so far in this workflow.

## Current Largest Validated Jump

- Route: cycle 10 -> predicted cycle 99 -> cycle 100
- Skipped intermediate FE cycles: 88
- Final STATEV1 error: 0.667869616047%
- Final S11 error: 0.0713767788476%
- Outcome: accepted_clean_success
