# Stage 15F Adaptive Real NEML Cycle-Jump Summary

Reference-data-based adaptive refinement using Stage 15D B1 cycle summary.

No long NEML simulations were run.

## Route Summary

| Base | Requested target | Chosen target | Method | Max normalized error % | Accepted |
|---:|---:|---:|---|---:|---|
| 500 | 1000 | 1000 | local_linear | 0.456158 | True |
| 1000 | 5000 | 5000 | quadratic_curvature_limited | 0.111568 | True |
| 5000 | 10000 | 10000 | local_linear | 0.750589 | True |
| 10000 | 50000 | 15000 | local_linear | 0.313542 | True |
| 50000 | 100000 | 100000 | quadratic_curvature_limited | 0.757465 | True |
| 100000 | 200000 | 106250 | least_squares_local_linear | 0.0734935 | True |

## Totals

- Requested routes: 6
- Accepted adaptive routes: 6
- Output rows: 415
