# Stage 15I Important Results for GPT 5.5 Analysis

## PBS Job

- Job ID: `1330433.mmaster02`
- Job name: `stage15i_multi_long`
- Queue: `teachingq`
- Submit time: 2026-05-26 06:10:10 CEST
- Start time: 2026-05-26 06:10:14 CEST
- Finish/obit time: 2026-05-27 01:50:29 CEST
- Exit status: `0`
- Walltime used: `19:40:08`
- CPU time used: `129:48:54`
- CPU percent: `1393`
- Requested resources: `1:ncpus=40:mpiprocs=40:mem=160gb:ompthreads=1`, walltime `20:00:00`
- Used memory: `6245680kb`
- Used virtual memory: `13639656kb`
- Used CPUs: `40`

## Overall Outcome

The wrapper and PBS job completed successfully, but the simulation campaign stopped at the configured 19:40:00 guard before any case reached the 1,500,000-cycle target.

- Case count: `14`
- Cases reaching 1,500,000 cycles: `0`
- Failed cases: `0`
- Maximum final cycle reached: `1,236,000` (`B2_10_to_310`)
- Minimum final cycle reached: `853,757` (`B1_m200_to_300`)
- Compact result files are committed for analysis.
- Full per-case `*_cycle_summary.csv` files were not committed because each is about 4.8-6.2 MB and the reduced target-cycle table plus selected-loop files are the preferred GPT analysis package.

## Final Recorded Case Values

| Case | Final cycle | Stress min/max | Strain mean | Ratcheting strain | Accumulated inelastic strain | Backstress norm |
|---|---:|---:|---:|---:|---:|---:|
| `B1_m140_to_250` | 938,000 | -140.903 / 249.097 | 0.347792 | 0.333305 | 2081.15 | 54.5923 |
| `B1_m150_to_240` | 938,000 | -150.692 / 239.308 | 0.284682 | 0.273132 | 2080.96 | 48.4154 |
| `B1_m150_to_250` | 936,000 | -151.337 / 248.663 | 0.355940 | 0.341970 | 2373.40 | 53.3454 |
| `B1_m150_to_260` | 925,000 | -152.588 / 257.412 | 0.429931 | 0.413702 | 2654.68 | 57.7405 |
| `B1_m160_to_250` | 920,000 | -161.998 / 248.002 | 0.352886 | 0.339685 | 2640.10 | 52.4517 |
| `B1_m180_to_280` | 900,600 | -181.157 / 278.843 | 0.654999 | 0.638974 | 4809.16 | 70.0902 |
| `B1_m200_to_300` | 853,700 | -200.090 / 299.910 | 0.899515 | 0.882932 | 9067.93 | 82.7194 |
| `B1_mean50_amp180` | 971,000 | -130.920 / 229.080 | 0.197022 | 0.187427 | 1352.99 | 45.0993 |
| `B1_mean50_amp220` | 908,200 | -172.228 / 267.772 | 0.521870 | 0.506243 | 3750.56 | 63.3994 |
| `B1_mean70_amp200` | 936,000 | -131.967 / 268.033 | 0.498015 | 0.478069 | 2373.92 | 65.7305 |
| `B2_0_to_320` | 1,086,000 | -4.821 / 315.179 | 0.196726 | 0.160235 | 481.382 | 122.121 |
| `B2_10_to_310` | 1,236,000 | 9.888 / 309.888 | -0.000675 | -0.034319 | 1.89036 | 126.818 |
| `B2_m20_to_300` | 1,087,000 | -24.209 / 295.791 | 0.171959 | 0.141417 | 481.587 | 106.977 |
| `B2_stress_0_to_300` | 1,219,000 | -0.105 / 299.895 | -0.000678 | -0.031357 | 1.88753 | 118.893 |

## Recommended Files to Analyze

- `STAGE15I_MASTER_SUMMARY.md`
- `STAGE15I_IMPORTANT_RESULTS_FOR_GPT55.md`
- `STAGE15I_CASE_COMPLETION_SUMMARY.csv`
- `STAGE15I_TARGET_CYCLE_VALUES.csv`
- `STAGE15I_RUN_METADATA.json`
- `STAGE15I_GLOBAL_STATUS.txt`
- `case_outputs/*_status.txt`
- `case_outputs/*_checkpoint.json`
- `case_outputs/*_selected_loops.csv`
- `logs/STAGE15I_FULL_LOG.txt`
- `logs/STAGE15I_JOB_OUT_TAIL.txt`
- `logs/stage15i_multi_long.o1330433`
