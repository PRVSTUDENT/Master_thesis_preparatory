# Stage 7B Grouped Adaptive DeltaN Controller Report

## Purpose

This report refines the Stage 7A paper-inspired adaptive jump-size estimate by grouping Chaboche state quantities according to their role in restart continuation. The accumulated scalar `STATEV1 = p` is retained as an accuracy monitor, but it is not allowed to control the global restart jump size.

No Abaqus run was performed. No UMAT or input deck was modified.

## Notation

The damage variable `D` from the original cycle-jump formulation is not used here because the present UMAT is a Chaboche viscoplasticity implementation, not a damage model. It is replaced by a generic cycle-control quantity `Y_i`, where `Y_i` may be accumulated viscoplastic strain, backstress, viscoplastic strain tensor, or residual stress.

The paper-style load-cycle increment notation `DeltaL` is replaced by `A_i`, the admissible state change for each control variable:

`A_i = tau_i S_i`

with `S_i = max(|Y_i(N0)|, |mean(Y_i)|, small_floor)`. The per-variable estimate is:

`DeltaN_i = floor(eta A_i / (|mean(Delta Y_i)| + eps))`

The grouped restart recommendation is:

`DeltaN_restart = min(DeltaN_X, DeltaN_eps_vp, DeltaN_S)`

`STATEV1 = p` is evaluated afterward as a scalar cumulative accuracy monitor.

Settings:

- Base cycle `N0 = 10`
- Mean increment window: cycles `2-10`
- Safety factor `eta = 0.75`
- `eps = 1e-12`
- `JUMPMIN = 1`, `JUMPMAX = 60`

## Variable Groups

| Group | Role | Variables | Included in restart minimum? |
|---|---|---|---|
| A | Accuracy monitor | `STATEV1 = p` | no |
| B | Restart-state controller | `STATEV2-4`, `STATEV8-10` | yes |
| C | Stress consistency controller | `S11` | yes |

## Per-Variable Results

| Variable | Group | Meaning | tau | mean Delta Y_i | A_i | DeltaN_i | Restart minimum |
|---|---|---|---:|---:|---:|---:|---|
| STATEV1 | accuracy_monitor | accumulated viscoplastic strain p | 0.02 | 0.00718546519056 | 0.00140533566475 | 1 | no |
| STATEV2 | restart_state | backstress X11 | 0.05 | 0.189079284668 | 4.29843576219 | 17 | yes |
| STATEV3 | restart_state | backstress X22 | 0.05 | -0.094539642334 | 2.1492178811 | 17 | yes |
| STATEV4 | restart_state | backstress X33 | 0.05 | -0.094539642334 | 2.1492178811 | 17 | yes |
| STATEV8 | restart_state | viscoplastic strain eps_vp_11 | 0.05 | -1.53241368632e-06 | 8.98255442734e-05 | 43 | yes |
| STATEV9 | restart_state | viscoplastic strain eps_vp_22 | 0.05 | 7.66206843158e-07 | 4.49127721367e-05 | 43 | yes |
| STATEV10 | restart_state | viscoplastic strain eps_vp_33 | 0.05 | 7.66206843158e-07 | 4.49127721367e-05 | 43 | yes |
| S11 | stress_consistency | axial residual stress | 0.03 | 0.321804470487 | 10.090502828 | 23 | yes |

## Grouped Recommendation

- `STATEV1` monitor DeltaN: `1`
- Restart-state controller minimum (`STATEV2-4`, `STATEV8-10`): `17`
- Stress consistency controller (`S11`): `23`
- Grouped restart DeltaN: `17`
- Controlling restart variable: `STATEV2`
- Recommended target cycle: `27`
- Skipped intermediate FE cycles: `16`
- Nearest scanned Stage 6C target: `29` (DeltaN `19`)

With the Stage 7A values, excluding the cumulative monitor gives:

`min(STATEV2-4, STATEV8-10, S11) = min(17, 43, 23) = 17`

## Validation Context

| Reference | DeltaN | Outcome |
|---|---:|---|
| Stage 5B clean jump | 9 | clean success |
| Stage 6C target 29 scan | 19 | acceptable exploratory candidate |
| Stage 6D cycle-29 FE continuation | 19 | acceptable exploratory success |
| Stage 6C targets 39/49 | 29/39 | not headline candidates |

The grouped recommendation `DeltaN_restart = 17` is close to the validated Stage 6D exploratory jump `DeltaN = 19`, while remaining slightly more conservative. It also avoids the Stage 7A failure mode where cumulative `p` alone forced `DeltaN = 1` despite being one of the most accurately predicted quantities in the FE validation.

Stage 6D reported `STATEV1` final relative error `0.0458269043313%` and `S11` final relative error `2.34365652874%`, confirming that the scalar cumulative variable can remain accurate while stress consistency becomes the practical limiter.

## Thesis Wording

In the present Chaboche implementation, the damage variable D of the original cycle-jump formulation is replaced by a generalized state-control variable Y_i. The admissible jump is then governed by a prescribed admissible change A_i = tau_i S_i. Because accumulated viscoplastic strain p is cumulative and accurately predicted over large jumps, it is used as an accuracy monitor, while the global jump size is controlled by backstress, viscoplastic strain tensor, and residual stress consistency.

## Outputs

- Per-variable controller CSV: `stage7_adaptive_deltaN\stage7b_grouped_adaptive_deltaN_by_variable.csv`
- Summary CSV: `stage7_adaptive_deltaN\stage7b_grouped_adaptive_deltaN_summary.csv`
