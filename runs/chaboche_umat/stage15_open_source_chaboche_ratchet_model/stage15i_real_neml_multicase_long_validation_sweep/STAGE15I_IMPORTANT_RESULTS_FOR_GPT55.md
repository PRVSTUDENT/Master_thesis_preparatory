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

Stage 15I showed that the real NEML workflow can run many stress-path variants safely under a 20-hour PBS allocation, without OOM failure, and can generate long-cycle reference data up to about 0.85-1.24 million cycles. However, because no case reached the planned 1.5 million-cycle target and because the chunked multicase runner shows segment-local strain-output behavior, Stage 15I should be used as a transferability and stress-path sensitivity dataset, not yet as the final global ratcheting-strain validation.

The wrapper and PBS job completed successfully, but the simulation campaign stopped at the configured 19:40:00 guard before any case reached the 1,500,000-cycle target. This is a **time-guard-limited multicase baseline**, not a failed run.

- Case count: `14`
- Cases reaching 1,500,000 cycles: `0`
- Failed cases: `0`
- Maximum final cycle reached: `1,236,000` (`B2_10_to_310`)
- Minimum final cycle reached: `853,757` (`B1_m200_to_300`)
- Compact result files are committed for analysis.
- Full per-case `*_cycle_summary.csv` files were not committed because each is about 4.8-6.2 MB and the reduced target-cycle table plus selected-loop files are the preferred GPT analysis package.

## Report Interpretation

Stage 15I was performed to test whether the real NEML Chaboche ratcheting workflow remains stable for several neighbouring stress paths around the accepted B1 case. The simulation campaign used the same `P2_three_backstress_screen` model and ran 14 stress-controlled cases, including primary B1-family cases, aggressive B1 stress paths, and diagnostic B2-type cases. The PBS job exited cleanly with `Exit_status=0`, used `19:40:08` walltime, and required only about `6.25 GB` memory, indicating that the streaming/checkpointed multicase workflow avoided the OOM problem observed earlier in Stage 15D.

The completion summary confirms all 14 cases were stopped by the time guard, with no failed case. It also shows the slower aggressive B1 cases and faster B2 diagnostic cases.

| Group | Case examples | Final-cycle range | Interpretation |
|---|---|---:|---|
| Primary B1-family | `B1_m140_to_250`, `B1_m150_to_240`, `B1_m150_to_250`, `B1_m150_to_260`, `B1_m160_to_250`, mean/amplitude variants | ~908k-971k | Stable long-cycle ratcheting-type baselines near the thesis-relevant B1 mechanism |
| Aggressive B1 | `B1_m180_to_280`, `B1_m200_to_300` | ~854k-901k | More demanding stress paths; slower progression and larger inelastic accumulation |
| Diagnostic B2 | `B2_0_to_320`, `B2_10_to_310`, `B2_m20_to_300`, `B2_stress_0_to_300` | ~1.086M-1.236M | Faster cases, but still not the preferred cycle-jump target because earlier Stage 15E gave no accepted B2 predictions |

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

## Stage 15I Case Completion Summary

| Case name | Group | Stress range | Final cycle | Status | Accumulated inelastic strain | Backstress norm |
|---|---|---:|---:|---|---:|---:|
| `B1_m140_to_250` | primary_b1 | -140 to 250 | 938,000 | stopped_by_time_guard | 2081.15 | 54.59 |
| `B1_m150_to_240` | primary_b1 | -150 to 240 | 938,000 | stopped_by_time_guard | 2080.96 | 48.42 |
| `B1_m150_to_250` | primary_b1 | -150 to 250 | 936,000 | stopped_by_time_guard | 2373.40 | 53.35 |
| `B1_m150_to_260` | primary_b1 | -150 to 260 | 925,000 | stopped_by_time_guard | 2654.68 | 57.74 |
| `B1_m160_to_250` | primary_b1 | -160 to 250 | 920,000 | stopped_by_time_guard | 2640.10 | 52.45 |
| `B1_m180_to_280` | aggressive_b1 | -180 to 280 | 900,667 | stopped_by_time_guard | 4809.16 | 70.09 |
| `B1_m200_to_300` | aggressive_b1 | -200 to 300 | 853,757 | stopped_by_time_guard | 9067.93 | 82.72 |
| `B1_mean50_amp180` | primary_b1 | -130 to 230 | 971,000 | stopped_by_time_guard | 1352.99 | 45.10 |
| `B1_mean50_amp220` | primary_b1 | -170 to 270 | 908,241 | stopped_by_time_guard | 3750.56 | 63.40 |
| `B1_mean70_amp200` | primary_b1 | -130 to 270 | 936,000 | stopped_by_time_guard | 2373.92 | 65.73 |
| `B2_0_to_320` | diagnostic_b2 | 0 to 320 | 1,086,000 | stopped_by_time_guard | 481.38 | 122.12 |
| `B2_10_to_310` | diagnostic_b2 | 10 to 310 | 1,236,000 | stopped_by_time_guard | 1.89 | 126.82 |
| `B2_m20_to_300` | diagnostic_b2 | -20 to 300 | 1,087,000 | stopped_by_time_guard | 481.59 | 106.98 |
| `B2_stress_0_to_300` | diagnostic_b2 | 0 to 300 | 1,219,000 | stopped_by_time_guard | 1.89 | 118.89 |

## Numerical Observations

For the B1-family cases, the final recorded accumulated inelastic strain is high and increases strongly for more aggressive stress paths. For example, `B1_m150_to_250` reached cycle 936,000 with accumulated inelastic strain about 2373.40, while `B1_m200_to_300` reached cycle 853,700 with accumulated inelastic strain about 9067.93 and backstress norm about 82.72. This supports the interpretation that the stronger stress paths are materially more demanding and provide useful stress-test cases for adaptive cycle-jump methods.

The B2 diagnostic cases behaved differently. `B2_stress_0_to_300` and `B2_10_to_310` reached more than 1.2 million cycles but had very small final recorded mean strain values, while `B2_0_to_320` and `B2_m20_to_300` showed larger final recorded strain and accumulated inelastic strain. This confirms that B2-type loading is not a single uniform response class and should remain diagnostic rather than the primary thesis cycle-jump case.

## Important Data-Quality Caveat

A post-run consistency check showed that the Stage 15I target-cycle table should not yet be used as a continuous global ratcheting-strain history. The multicase runner used chunked worker launches, and the metadata records `max_cycles_per_launch = 10000`. In the target-cycle table, some strain-related quantities appear to reset or become segment-local after later chunks, even though accumulated inelastic strain and backstress continue to evolve. Therefore, Stage 15I is interpreted mainly through final-cycle coverage, accumulated inelastic strain, backstress norm, and selected-loop evidence. A follow-up postprocessing stage is required before using Stage 15I `strain_mean` or `ratcheting_strain` as a global continuous curve.

For the canonical `B1_m150_to_250` case, `strain_mean` is about 3.737 at 100,000 cycles but about 0.146 at 200,000 cycles, while accumulated inelastic strain continues increasing from about 253.7 to 507.3. That suggests the strain-like outputs are not globally continuous across chunks.

Do not claim that Stage 15I proves global ratcheting strain evolution for all cases. Instead, claim that Stage 15I provides a stable, memory-safe, multicase real-NEML long-cycle dataset and identifies stress-path sensitivity. The global continuity of strain-like cycle metrics must be checked before using these data for quantitative adaptive-jump validation.

## Comparison with Stage 15G

Stage 15G remains the clean canonical long B1 reference because it reached 2,000,000 cycles in a single B1-focused run and reported final mean strain about 73.62 and final ratcheting strain about 73.60. Stage 15I, in contrast, is a parallel multicase sweep and should be used for transferability screening. The `B1_m150_to_250` case in Stage 15I reached 936,000 cycles, but its final recorded mean strain is only about 0.356, which is not directly comparable to the Stage 15G global B1 strain history without a continuity correction.

**Stage 15G is the validated long single-case reference. Stage 15I is the multicase transferability dataset.**

## Recommended Figures and Tables

- Table: Stage 15I case completion summary, above.
- Bar plot: final cycle reached by each case: `figures/stage15i_final_cycle_by_case.svg`.
- Bar plot: final accumulated inelastic strain by case: `figures/stage15i_final_accumulated_inelastic_strain_by_case.svg`.
- Selected-loop plot for primary B1 case `B1_m150_to_250`: `figures/stage15i_selected_loops_B1_m150_to_250.svg`.
- Selected-loop plot for aggressive B1 case `B1_m200_to_300`: `figures/stage15i_selected_loops_B1_m200_to_300.svg`.
- Selected-loop plot for diagnostic B2 case `B2_stress_0_to_300`: `figures/stage15i_selected_loops_B2_stress_0_to_300.svg`.

## Stage 15J Transition

The next required postprocessing step is Stage 15J. This stage will validate the continuity of Stage 15I chunked outputs, compare the Stage 15I canonical B1 case against the clean Stage 15G B1 reference at overlapping cycles, and reconstruct or correct global strain-like quantities if necessary. Only after this check should Stage 15I be used for quantitative adaptive cycle-jump transferability validation.

## Final Report Conclusion

Stage 15I successfully extended the real-NEML study from a single canonical B1 case to a 14-case multicase stress-path sweep. The PBS job completed cleanly with no failed cases and no memory failure. Although the cases stopped at the configured time guard before reaching the nominal 1,500,000-cycle target, they reached approximately 0.85-1.24 million cycles, which is sufficient for stress-path sensitivity assessment. The results show that B1-neighbouring cases remain stable, aggressive B1 cases produce stronger inelastic accumulation, and B2 cases behave differently from the accepted B1 cycle-jump target. However, because the chunked multicase runner may output segment-local strain-like quantities, Stage 15I should be treated as a transferability dataset until a continuity check is completed in Stage 15J.

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
- `figures/stage15i_final_cycle_by_case.svg`
- `figures/stage15i_final_accumulated_inelastic_strain_by_case.svg`
- `figures/stage15i_selected_loops_B1_m150_to_250.svg`
- `figures/stage15i_selected_loops_B1_m200_to_300.svg`
- `figures/stage15i_selected_loops_B2_stress_0_to_300.svg`
