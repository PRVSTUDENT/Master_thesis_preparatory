# Stage 14C Adaptive Sweep Report

Generated: 2026-05-21 19:33:51

## Method

Configurable adaptive blockwise cycle jumping with Abaqus/Standard recovery windows. This report is updated after each finished case or sanity block.

## Ranked Case Summary

| Rank | Case | Outcome | Final Cycle | STATEV1 Error % | S11 Error % | RF1 Error % | Speed-up |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | S00 | in_progress | 33 | 0.00627372495218 | 12.223564919 | 12.223564919 | 100 |

## Latest Block History

| Case | Block | Base | Target | Recovery End | DeltaN | Recovered STATEV1 | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| S00 | 1 | 10 | 23 | 33 | 13 | 0.235127046704 | accepted_exploratory_success |

## Baselines

- Stage 14 fixed best: jump25, STATEV1 error about 2.85226684954%.
- Stage 14B adaptive: STATEV1 error 124.209089872%.
