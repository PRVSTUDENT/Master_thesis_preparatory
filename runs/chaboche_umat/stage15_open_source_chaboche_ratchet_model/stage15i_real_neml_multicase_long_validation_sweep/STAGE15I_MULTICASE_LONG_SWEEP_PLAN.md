# Stage 15I Real NEML Multi-Case Long Validation Sweep Plan

Stage 15I runs real NEML long-cycle baselines for B1-neighbouring stress paths and selected B2 diagnostic cases. The purpose is to test whether the adaptive cycle-jump strategy validated around the canonical Stage 15G B1 case transfers to nearby ratcheting regimes.

Stage 15I is not prediction-only. It uses the real NEML `P2_three_backstress_screen` material and the Stage 15G streaming/checkpoint-safe output pattern.

## Run Controls

| Setting | Value |
|---|---:|
| Queue | teachingq |
| Requested CPUs | 40 |
| PBS walltime | 20:00:00 |
| Stop guard | 19:40:00 |
| Default active workers | 24 |
| Hard maximum workers | 32 |
| Points per cycle | 40 |
| Primary target | 1,500,000 cycles |
| Extension target | 2,000,000 cycles |
| Minimum useful target | 500,000 cycles |

The runner writes compact cycle summaries only: every cycle through 10,000, every 100 cycles after 10,000, preserved target cycles exactly, and the final completed cycle. Selected loops store only the 40 stress-strain points for selected cycles.

## Case Groups

Primary B1-family cases test transferability near the successful Stage 15G baseline. Aggressive B1 cases stress-test stronger ratcheting. B2 cases are diagnostic because earlier simple predictors struggled there.

## Required Gate

Run `stage15i_preflight_check.py` and `run_stage15i_smoke_hpc.sh` before submitting `submit_stage15i_multicase_long_sweep.pbs`.
