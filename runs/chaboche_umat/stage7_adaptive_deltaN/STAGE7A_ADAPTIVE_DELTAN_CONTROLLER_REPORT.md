# Stage 7A Adaptive DeltaN Controller Report

## Purpose

This report implements a paper-inspired adaptive jump-size estimate for the Chaboche cycle-jump workflow. No damage variable is used. The paper-style damage variable `D` is replaced by generalized control variables `Y_i` based on Chaboche STATEV and stress components.

No Abaqus run was performed. No UMAT or input deck was modified.

## Controller Definition

For each controlled variable `Y_i`, the admissible change is defined as:

`A_i = tau_i S_i`

where `S_i = max(|Y_i(N0)|, |mean(Y_i)|, small_floor)`. The paper-style jump estimate is then written as:

`DeltaN_i = floor(eta A_i / (|mean(Delta Y_i)| + eps))`

The global jump is controlled by the most restrictive variable:

`DeltaN = min_i(DeltaN_i)`

Settings:

- Base cycle `N0 = 10`
- Mean increment window: cycles `2-10`
- Safety factor `eta = 0.75`
- `eps = 1e-12`
- `JUMPMIN = 1`, `JUMPMAX = 60`

## Controlled Variables

| Variable | Meaning | tau | mean Delta Y_i | A_i | DeltaN_i |
|---|---|---:|---:|---:|---:|
| STATEV1 | accumulated viscoplastic strain p | 0.02 | 0.00718546519056 | 0.00140533566475 | 1 |
| STATEV2 | backstress X11 | 0.05 | 0.189079284668 | 4.29843576219 | 17 |
| STATEV3 | backstress X22 | 0.05 | -0.094539642334 | 2.1492178811 | 17 |
| STATEV4 | backstress X33 | 0.05 | -0.094539642334 | 2.1492178811 | 17 |
| STATEV8 | viscoplastic strain eps_vp_11 | 0.05 | -1.53241368632e-06 | 8.98255442734e-05 | 43 |
| STATEV9 | viscoplastic strain eps_vp_22 | 0.05 | 7.66206843158e-07 | 4.49127721367e-05 | 43 |
| STATEV10 | viscoplastic strain eps_vp_33 | 0.05 | 7.66206843158e-07 | 4.49127721367e-05 | 43 |
| S11 | axial residual stress | 0.03 | 0.321804470487 | 10.090502828 | 23 |

## Recommendation

- Global adaptive DeltaN: `1`
- Controlling variable: `STATEV1`
- Recommended target cycle: `11`
- Skipped intermediate FE cycles: `0`

## Comparison with Stage 6C Scan

| Target | DeltaN | Observed Stage 6C decision |
|---:|---:|---|
| 29 | 19 | acceptable exploratory candidate |
| 39 | 29 | not headline candidate |
| 49 | 39 | not headline candidate |

The adaptive controller should be interpreted as a conservative paper-inspired first estimate. If the recommended DeltaN is below 19, it is stricter than the manual Stage 6C scan. If it is near 19, it agrees with the largest acceptable scan target. If it exceeds 29, it would be less conservative than the observed stress/backstress drift in Stage 6C.

The computed recommendation is conservative relative to the Stage 6C scan and would not select the non-headline targets 39 or 49.

## Interpretation

This is a paper-inspired adaptive jump-size controller, not a damage model. It replaces `D` by Chaboche control variables `Y_i` and replaces `DeltaL` by the admissible state-change budget `A_i`. The result supports the thesis observation that scalar `STATEV1` alone permits larger jumps, while stress and backstress consistency restrict physically consistent FE continuation.

## Outputs

- Per-variable controller CSV: `stage7_adaptive_deltaN\stage7a_adaptive_deltaN_by_variable.csv`
- Summary CSV: `stage7_adaptive_deltaN\stage7a_adaptive_deltaN_summary.csv`
