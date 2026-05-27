# Stage 15J Final Continuous Real-NEML Multicase Validation Plan

Stage 15J is the final continuous real-NEML multicase transferability validation. It closes the Stage 15 workflow by replacing Stage 15I's chunked multicase execution with one continuous worker process per case.

## Purpose

Run a 20-hour, 40-CPU, continuous-state real-NEML multicase validation campaign. The goal is to prove whether the accepted B1 adaptive cycle-jump strategy is transferable to neighbouring B1-type stress paths and to clearly separate B1-type useful ratcheting cases from B2 diagnostic cases.

## Critical Difference from Stage 15I

- No chunked relaunch resetting strain-like quantities.
- Each case runs as one continuous process from cycle 1 until target, extension target, stop guard, or failure.
- Checkpointing is allowed for recovery, but the normal full run does not relaunch every 10,000 cycles.

## HPC Request

| Setting | Value |
|---|---:|
| Queue | teachingq |
| CPUs | 40 |
| Walltime | 20:00:00 |
| Stop guard | 19:40:00 |
| Active workers | 40 |
| Memory | 160 GB |
| Points per cycle | 40 |
| Primary target | 1,500,000 cycles |
| Extension target | 2,000,000 cycles |
| Minimum useful target | 500,000 cycles |

Threading variables are set to one thread per worker: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `NUMEXPR_NUM_THREADS=1`.

## OOM Fix

The first full PBS attempt, job `1332149.mmaster02`, failed after `01:01:27` because the cgroup memory limit was exceeded. PBS reported `resources_used.mem = 167774208kb` against the 160 GB allocation, and the wrapper log showed `BrokenProcessPool` after one worker was killed. A first fix trimmed `stress_int`, `strain_int`, and `stored_int`, but the resumed retry `1332165.mmaster02` still reached the cgroup limit after `02:31:46`. A driver inspection showed that `Driver_sd` also retains `mechanical_strain_int`, `thermal_strain_int`, `T_int`, `t_int`, `u_int`, and `p_int`. The final fix keeps the intended 40 active real-NEML workers but trims every retained `Driver_sd` integration-history list to its latest value after every material increment. This preserves continuous material state while preventing retained per-step arrays from growing throughout the run. Retries use `STAGE15J_RESUME=1` to continue from per-case checkpoints.

## Case Groups

Group A is a 25-case B1 transferability grid over mean stress `[30, 40, 50, 60, 70]` MPa and stress amplitude `[180, 190, 200, 210, 220]` MPa. The canonical B1 repeat is `B1_grid_mean50_amp200`.

Group B contains 10 aggressive B1 stress-test cases.

Group C contains 5 B2 diagnostic cases.

## Required Gate

Run preflight and smoke test before PBS submission:

```bash
python3 stage15j_preflight_check.py
bash run_stage15j_smoke_hpc.sh
qsub submit_stage15j_final_multicase.pbs
```
