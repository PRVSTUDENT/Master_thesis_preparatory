# Stage 6C Multi-Target Prediction Scan Report

## Purpose

This scan evaluates predicted injection-state quality for larger FE cycle jumps before running another Abaqus continuation. It uses the existing no-skip 50-cycle reference history and performs no Abaqus rerun.

No UMAT or Abaqus input deck was modified.

## Method

- Base cycle: `10`
- Targets: `29, 39, 49`
- Mean increment window: cycles `2-10`
- Prediction rule: `predicted_target = value_cycle10 + DeltaN * mean_increment_per_cycle`
- STATEV14 policy: recomputed from predicted STATEV1 using `Q*(1-exp(-b*STATEV1))`
- STATEV15 policy: reset to `0` for injection
- Compared exact target states from `chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv` only for validation.

## Decision Rules

- Strong candidate: `STATEV1 < 1%`, `S11 < 1%`, and vector components preferably `< 3%`.
- Acceptable exploratory candidate: `STATEV1 < 1%`, `S11 < 3%`, and vector components preferably `< 6%`.
- Not headline candidate: `S11 > 3%` or `STATEV2-4 > 6%`.

## Summary

| Target | Continue to | DeltaN | Skipped cycles | Computed route | Full route | Reduction | STATEV1 err | STATEV2-4 max err | STATEV8-10 max err | S11 err | Recommendation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 29 | 30 | 19 | 18 | 11 | 30 | 63.3333333333% | 0.135335066339% | 4.06462912747% | 1.92948361911% | 2.16514971786% | `acceptable_exploratory_candidate` |
| 39 | 40 | 29 | 28 | 11 | 40 | 72.5% | 0.212701182838% | 6.20776169223% | 2.94821440017% | 3.30894356786% | `not_headline_candidate` |
| 49 | 50 | 39 | 38 | 11 | 50 | 78% | 0.290736770316% | 8.35356376404% | 3.96914287256% | 4.45565123814% | `not_headline_candidate` |

## Interpretation

- Cycle 49 gives the largest skip but has noticeable stress/backstress drift.
- The best next FE validation target should be the largest target satisfying the decision rules.
- Largest candidate satisfying the rules: target cycle `29` with recommendation `acceptable_exploratory_candidate`.
- The scan confirms that scalar `STATEV1` extrapolation is less restrictive than full vector/stress extrapolation.

## Cycle-50 Reference Context

- Full explicit cycle-50 STATEV1: `0.356620669365`
- Full explicit cycle-50 S11: `374.653869629 MPa`
- Full explicit cycle-50 RIGHT_FACE RF1: `1498.61547852`

## Outputs

- Detailed errors: `stage6_multitarget_jump_scan\stage6c_multitarget_prediction_errors.csv`
- Target summary: `stage6_multitarget_jump_scan\stage6c_multitarget_prediction_summary.csv`
