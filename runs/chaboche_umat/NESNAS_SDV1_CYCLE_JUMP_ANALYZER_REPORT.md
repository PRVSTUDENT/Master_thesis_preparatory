# Nesnas-Saanouni-Inspired SDV1 Cycle-Jump Analyzer

This postprocessing script bridges the validated Chaboche-v1 milestone to the Nesnas-Saanouni two-time-scale idea. It does not rerun Abaqus, modify the UMAT, or inject jumped STATEV values.

## Input

- Explicit reference CSV: `chaboche_vp_v1_cyclic_eps005_20cycles_cycle_increments.csv`
- Scalar cycle-evolution marker: `SDV1 = accumulated viscoplastic strain p`
- Stabilized reference window: cycles `2-10`

## Reference Statistics

- Mean dSDV1/dN over cycles 2-10: `0.00718546519056`
- Std dSDV1/dN over cycles 2-10: `3.36821320212e-06`
- Relative range over cycles 2-10: `0.00142903719212` (`0.142903719212%`)
- Mean d2SDV1/dN2 over cycles 2-10: `3.1146925e-07`

## Adaptive Jump Settings

- eta: `1.0`
- JUMPMIN: `5`
- JUMPMAX: `60`
- Curvature check tolerance: `0.01`
- Recommended Delta N when cycle 10 is used as the jump base: `9`

## Cycle-20 Validation

- First-order predicted SDV1 at cycle 20: `0.142121435146`
- Second-order predicted SDV1 at cycle 20: `0.142137008608`
- Explicit SDV1 at cycle 20: `0.1420256943`
- First-order relative error: `0.0674109329494%`
- Second-order relative error: `0.0783761759477%`

## Adaptive Jump Validation

The adaptive estimator recommends a conservative jump from cycle 10 to cycle 19. The fixed cycle-20 target is kept separately because an explicit 20-cycle Abaqus reference is available for the original validation.

- Jump base cycle: `10`
- Recommended Delta N: `9`
- Adaptive target cycle: `19`
- First-order predicted SDV1: `0.134935969955`
- Second-order predicted SDV1: `0.13494858446`
- Explicit SDV1 reference: `0.1348549426`
- First-order relative error: `0.0600848240619%`
- Second-order relative error: `0.0694389525661%`

## Interpretation

The first-order SDV1 extrapolation reproduces the explicit 20-cycle result with the already validated error level. The second-order estimate is also reported, but for the nearly stabilized response the curvature term is small and mainly serves as a jump-size control diagnostic.

This is still a Level-1 postprocessing cycle-jump method. A Nesnas-Saanouni-style FE acceleration would require jumping the complete material state and resuming Abaqus from the extrapolated STATEV field.

## Generated Files

- `nesnas_sdv1_cycle_derivatives.csv`
- `nesnas_sdv1_first_second_order_predictions.csv`
- `nesnas_sdv1_adaptive_jump_recommendations.csv`
- `nesnas_sdv1_adaptive_jump_validation.csv`
- `nesnas_sdv1_cycle_derivatives.svg`
- `nesnas_sdv1_first_second_order_prediction.svg`
- `nesnas_sdv1_adaptive_jump_size.svg`
