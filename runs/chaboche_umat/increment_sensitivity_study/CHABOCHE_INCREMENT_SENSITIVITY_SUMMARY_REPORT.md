# Chaboche-v1 Increment-Schedule Sensitivity Summary

This report summarizes the completed DMAX sensitivity cases for cycle 20 and freezes the Stage 3 evidence for thesis use.

Reference STATEV1 at cycle 20: 0.142025694251

## Final Cycle-20 Table

| case_name | dmax | inc_limit | completed | STATEV1_cycle20 | abs diff | rel diff % | Avg_S11_cycle20 |
|---|---:|---:|---|---:|---:|---:|---:|
| chaboche_eps005_20cycles_dt_original_output | 0.020 | 4000 | true | 0.142025694251 | 0 | 0 | 376.434143066 |
| chaboche_eps005_20cycles_dtmax_0p01 | 0.010 | 4000 | true | 0.143569096923 | 0.001543402672 | 1.08670665554 | 380.566436768 |
| chaboche_eps005_20cycles_dtmax_0p005_inc6000 | 0.005 | 6000 | true | 0.145257070661 | 0.00323137641 | 2.2752055021 | 385.053924561 |

## Interpretation

The three completed cases show a monotonic increase in STATEV1 as DMAX decreases:

- DMAX = 0.020 -> STATEV1 = 0.142025694251
- DMAX = 0.010 -> STATEV1 = 0.143569096923
- DMAX = 0.005 -> STATEV1 = 0.145257070661

This confirms that the Chaboche-v1 UMAT is increment-size sensitive under the controlled DMAX refinement study.

## Stage 3 Context

The earlier DMAX = 0.005 deck with INC = 2500 failed with too many increments and was not used as a cycle-20 result.
It was corrected by copying the deck to INC = 6000, which completed successfully and provided the final DMAX = 0.005 data point.

## Implication

Level-3 STATEV injection remains deferred.
The results are stronger evidence that UMAT integration robustness should be improved before attempting a full Nesnas-Saanouni restart-level cycle jump.

## Recommendations

1. Improve UMAT integration robustness.
2. Revisit convergence after the implementation is stabilized.
3. Only then resume the Level-3 STATEV injection path.
