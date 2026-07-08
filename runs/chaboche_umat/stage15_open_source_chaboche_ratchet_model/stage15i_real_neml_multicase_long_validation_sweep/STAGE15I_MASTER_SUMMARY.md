# Stage 15I Real NEML Multi-Case Transferability Sweep Summary

Stage 15I showed that the real NEML workflow can run many stress-path variants safely under a 20-hour PBS allocation, without OOM failure, and can generate long-cycle reference data up to about 0.85-1.24 million cycles. However, because no case reached the planned 1.5 million-cycle target and because the chunked multicase runner shows segment-local strain-output behavior, Stage 15I should be used as a transferability and stress-path sensitivity dataset, not yet as the final global ratcheting-strain validation.

| Field | Value |
|---|---:|
| Case count | 14 |
| Completed cases | 0 |
| Stopped by time guard | 14 |
| Failed cases | 0 |
| Maximum final cycle | 1236000 |
| Target cycle | 1500000 |
| Active workers | 14 |
| Max cycles per worker launch | 10000 |

## Stage 15I: multicase real-NEML long-cycle validation sweep

Stage 15I was performed to test whether the real NEML Chaboche ratcheting workflow remains stable for several neighbouring stress paths around the accepted B1 case. The simulation campaign used the same `P2_three_backstress_screen` model and ran 14 stress-controlled cases, including primary B1-family cases, aggressive B1 stress paths, and diagnostic B2-type cases. The PBS job exited cleanly with `Exit_status=0`, used `19:40:08` walltime, and required only about `6.25 GB` memory, indicating that the streaming/checkpointed multicase workflow avoided the OOM problem observed earlier in Stage 15D.

The campaign stopped at the configured time guard before reaching the nominal target of 1,500,000 cycles. Therefore, the run should be described as a **time-guard-limited multicase baseline**, not as a failed run. No case failed numerically. The maximum reached cycle was 1,236,000 for `B2_10_to_310`, while the minimum reached cycle was 853,757 for the aggressive `B1_m200_to_300` case.

| Group | Case examples | Final-cycle range | Interpretation |
|---|---|---:|---|
| Primary B1-family | `B1_m140_to_250`, `B1_m150_to_240`, `B1_m150_to_250`, `B1_m150_to_260`, `B1_m160_to_250`, mean/amplitude variants | ~908k-971k | Stable long-cycle ratcheting-type baselines near the thesis-relevant B1 mechanism |
| Aggressive B1 | `B1_m180_to_280`, `B1_m200_to_300` | ~854k-901k | More demanding stress paths; slower progression and larger inelastic accumulation |
| Diagnostic B2 | `B2_0_to_320`, `B2_10_to_310`, `B2_m20_to_300`, `B2_stress_0_to_300` | ~1.086M-1.236M | Faster cases, but still not the preferred cycle-jump target because earlier Stage 15E gave no accepted B2 predictions |

The completion summary confirms all 14 cases were stopped by the time guard, with no failed case. It also shows the slower aggressive B1 cases and faster B2 diagnostic cases.

## Numerical observations

For the B1-family cases, the final recorded accumulated inelastic strain is high and increases strongly for more aggressive stress paths. For example, `B1_m150_to_250` reached cycle 936,000 with accumulated inelastic strain about 2373.40, while `B1_m200_to_300` reached cycle 853,700 with accumulated inelastic strain about 9067.93 and backstress norm about 82.72. This supports the interpretation that the stronger stress paths are materially more demanding and provide useful stress-test cases for adaptive cycle-jump methods.

The B2 diagnostic cases behaved differently. `B2_stress_0_to_300` and `B2_10_to_310` reached more than 1.2 million cycles but had very small final recorded mean strain values, while `B2_0_to_320` and `B2_m20_to_300` showed larger final recorded strain and accumulated inelastic strain. This confirms that B2-type loading is not a single uniform response class and should remain diagnostic rather than the primary thesis cycle-jump case.

## Data-quality caveat

A post-run consistency check showed that the Stage 15I target-cycle table should not yet be used as a continuous global ratcheting-strain history. The multicase runner used chunked worker launches, and the metadata records `max_cycles_per_launch = 10000`. In the target-cycle table, some strain-related quantities appear to reset or become segment-local after later chunks, even though accumulated inelastic strain and backstress continue to evolve. Therefore, Stage 15I is interpreted mainly through final-cycle coverage, accumulated inelastic strain, backstress norm, and selected-loop evidence. A follow-up postprocessing stage is required before using Stage 15I `strain_mean` or `ratcheting_strain` as a global continuous curve.

For the canonical `B1_m150_to_250` case, `strain_mean` is about 3.737 at 100,000 cycles but about 0.146 at 200,000 cycles, while accumulated inelastic strain continues increasing from about 253.7 to 507.3. That suggests the strain-like outputs are not globally continuous across chunks.

Therefore, Stage 15I should not be used to claim that it proves global ratcheting strain evolution for all cases. Instead, Stage 15I provides a stable, memory-safe, multicase real-NEML long-cycle dataset and identifies stress-path sensitivity. The global continuity of strain-like cycle metrics must be checked before using these data for quantitative adaptive-jump validation.

## Comparison with Stage 15G

Stage 15G remains the clean canonical long B1 reference because it reached 2,000,000 cycles in a single B1-focused run and reported final mean strain about 73.62 and final ratcheting strain about 73.60. Stage 15I, in contrast, is a parallel multicase sweep and should be used for transferability screening. The `B1_m150_to_250` case in Stage 15I reached 936,000 cycles, but its final recorded mean strain is only about 0.356, which is not directly comparable to the Stage 15G global B1 strain history without a continuity correction.

**Stage 15G is the validated long single-case reference. Stage 15I is the multicase transferability dataset.**

## Stage 15I case completion summary

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

## Recommended figures and tables

- Table: Stage 15I case completion summary, above.
- Bar plot: final cycle reached by each case: `figures/stage15i_final_cycle_by_case.svg`.
- Bar plot: final accumulated inelastic strain by case: `figures/stage15i_final_accumulated_inelastic_strain_by_case.svg`.
- Selected-loop plot for primary B1 case `B1_m150_to_250`: `figures/stage15i_selected_loops_B1_m150_to_250.svg`.
- Selected-loop plot for aggressive B1 case `B1_m200_to_300`: `figures/stage15i_selected_loops_B1_m200_to_300.svg`.
- Selected-loop plot for diagnostic B2 case `B2_stress_0_to_300`: `figures/stage15i_selected_loops_B2_stress_0_to_300.svg`.

## Stage 15J transition

The next required postprocessing step is Stage 15J. This stage will validate the continuity of Stage 15I chunked outputs, compare the Stage 15I canonical B1 case against the clean Stage 15G B1 reference at overlapping cycles, and reconstruct or correct global strain-like quantities if necessary. Only after this check should Stage 15I be used for quantitative adaptive cycle-jump transferability validation.

## Conclusion

Stage 15I successfully extended the real-NEML study from a single canonical B1 case to a 14-case multicase stress-path sweep. The PBS job completed cleanly with no failed cases and no memory failure. Although the cases stopped at the configured time guard before reaching the nominal 1,500,000-cycle target, they reached approximately 0.85-1.24 million cycles, which is sufficient for stress-path sensitivity assessment. The results show that B1-neighbouring cases remain stable, aggressive B1 cases produce stronger inelastic accumulation, and B2 cases behave differently from the accepted B1 cycle-jump target. However, because the chunked multicase runner may output segment-local strain-like quantities, Stage 15I should be treated as a transferability dataset until a continuity check is completed in Stage 15J.
