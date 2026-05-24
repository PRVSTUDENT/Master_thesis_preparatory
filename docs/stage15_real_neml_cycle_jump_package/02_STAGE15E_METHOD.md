# Stage 15E Method

Stage 15E is a prediction-only cycle-jump benchmark. It reads the Stage 15D cycle summaries, estimates slopes from early-cycle windows, predicts later target cycles, and compares predictions against the Stage 15D reference values.

## Variables

Primary:

- `strain_mean`
- `ratcheting_strain`

Secondary:

- `strain_max`
- `strain_min`
- `strain_range`
- `hysteresis_area`

## Base Cycles

`10, 20, 50, 100, 500, 1000, 5000, 10000`

## Prediction Methods

- `linear_last_2`
- `linear_last_5`
- `linear_last_10`
- `linear_last_20`
- `least_squares_last_20`
- `least_squares_last_50`
- `least_squares_last_100`

The predictor is:

```text
y_pred(target) = y(base) + slope * (target - base)
```

## Acceptance

A lane is accepted when the target is inside the Stage 15D baseline, reference values exist, no NaN or inf is present, drift direction is correct, and the normalized errors are within the selected tolerance.

Strict acceptance uses 1% normalized error. Relaxed summaries use 2% and 5%.

