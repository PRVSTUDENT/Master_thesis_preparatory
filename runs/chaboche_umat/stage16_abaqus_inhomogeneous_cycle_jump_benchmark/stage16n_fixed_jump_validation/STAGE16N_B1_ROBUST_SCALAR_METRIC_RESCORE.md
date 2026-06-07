# Stage 16N B1 Robust Scalar-Metric Re-score

This table re-scores the completed B1/B1_EQ family using robust statistics over the lightweight scalar metrics already stored in the repository. It is not a full pointwise field percentile study because full per-integration-point fields were not retained for every B1 case.

Loop errors are normalized by the full reference loop amplitude for `U1_avg` and `RF1_sum`, not by each individual reference point. This avoids artificial blow-ups at zero crossings.

## Interpretation Rule

- `pass_by_max`: maximum primary scalar-metric error is at or below 5%.
- `robust_pass_but_max_review`: p95 primary scalar-metric error is at or below 5%, but the maximum is above 5%.
- `review`: p95 and maximum primary scalar-metric errors are above 5%.

## Summary

| Case | Status | Primary mean % | Primary median % | Primary p95 % | Primary p99 % | Primary max % | Loop p95 % |
|---|---|---:|---:|---:|---:|---:|---:|
| B1D1_100_to_101_to_250 | review | 2.97163 | 1.77699 | 7.47991 | 8.46293 | 8.70868 | 21.6836 |
| B1D1_EQ_100_to_101_to_250 | review | 2.97163 | 1.77699 | 7.47991 | 8.46293 | 8.70868 | 21.6836 |
| B1D2_100_to_102_to_250 | review | 3.06906 | 1.92072 | 7.52586 | 8.54054 | 8.7942 | 21.7095 |
| B1D2_EQ_100_to_102_to_250 | review | 3.06906 | 1.92072 | 7.52586 | 8.54054 | 8.7942 | 21.7095 |
| B1D3_100_to_103_to_250 | review | 2.7881 | 1.49114 | 6.93576 | 7.33625 | 7.43637 | 5 |
| B1D3_EQ_100_to_103_to_250 | review | 2.7881 | 1.49114 | 6.93576 | 7.33625 | 7.43637 | 5 |
| B1D4_100_to_104_to_250 | review | 3.10576 | 1.52271 | 7.44854 | 7.52745 | 7.54718 | 32.4511 |
| B1D4_EQ_100_to_104_to_250 | review | 3.10576 | 1.52271 | 7.44854 | 7.52745 | 7.54718 | 32.4511 |
| B1D5_100_to_105_to_250 | pass_by_max | 0.392238 | 0.000246653 | 1.76313 | 2.23251 | 2.34986 | 4.88998e-05 |
| B1D5_EQ_100_to_105_to_250 | pass_by_max | 0.392238 | 0.000246653 | 1.76313 | 2.23251 | 2.34986 | 4.88998e-05 |
| B1Q_100_to_106_to_250 | robust_pass_but_max_review | 2.54352 | 2.34673 | 4.99948 | 5.60287 | 5.75372 | 22.0538 |
| B1Q_EQ_100_to_106_to_250 | robust_pass_but_max_review | 2.54352 | 2.34673 | 4.99948 | 5.60287 | 5.75372 | 22.0538 |
| B1S_100_to_112_to_250 | review | 3.65193 | 3.1224 | 7.50946 | 7.60616 | 7.63033 | 32.4509 |
| B1S_EQ_100_to_112_to_250 | review | 3.65193 | 3.1224 | 7.50946 | 7.60616 | 7.63033 | 32.4509 |
| B1_100_to_125_to_250 | review | 4.64409 | 2.3358 | 11.0312 | 11.2284 | 11.2777 | 21.9994 |
| B1_EQ_100_to_125_to_250 | review | 4.64409 | 2.3358 | 11.0312 | 11.2284 | 11.2777 | 21.9994 |

## Conclusion

The robust scalar re-score keeps the same conservative conclusion as the max-error gate. `B1D5` and `B1D5_EQ` are clean passes. Several neighboring cases have low global loop errors but remain review cases because their primary local scalar metrics exceed the 5% threshold. A future pointwise field-percentile study should use full ODB-extracted integration-point fields if a less brittle local acceptance rule is needed.
