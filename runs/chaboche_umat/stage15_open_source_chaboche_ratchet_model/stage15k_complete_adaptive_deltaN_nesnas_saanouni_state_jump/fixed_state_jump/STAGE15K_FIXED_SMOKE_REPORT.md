# Stage 15K Fixed State-Jump Smoke Report

- Real NEML backend: `true`
- NEML path: `/home/pr21vyci/.local/lib/python3.11/site-packages/neml/__init__.py`
- Rows: `3`
- Strict accepted rows: `3`
- Relaxed 2 pct accepted rows: `3`
- Relaxed 5 pct accepted rows: `3`
- Gate pass: `true`

## Route
- Route: `500 -> 1000`
- Method: `least_squares_last_20`
- Full state extrapolated and reinjected: `true`
- Post-jump continuation cycles checked: `0, 50, 100`
- `fixed_smoke_pass`: `true`

## Error Table
| base_cycle | requested_target_cycle | jump_target_cycle | derivative_method | comparison_cycle | mean_strain_norm_error | accumulated_inelastic_norm_error | backstress_norm_error | relaxed_5pct_accepted |
|---|---|---|---|---|---|---|---|---|
| 500 | 1000 | 1000 | least_squares_last_20 | 1000 | 0.00027241320667371546 | 0.0003777677896209299 | 0.0018761779378214626 | true |
| 500 | 1000 | 1000 | least_squares_last_20 | 1050 | 0.00027544782865353165 | 0.0003603677581632091 | 6.0356177102746135e-06 | true |
| 500 | 1000 | 1000 | least_squares_last_20 | 1100 | 0.0002679633699159051 | 0.00034502575761902876 | 7.0600770575002565e-06 | true |
