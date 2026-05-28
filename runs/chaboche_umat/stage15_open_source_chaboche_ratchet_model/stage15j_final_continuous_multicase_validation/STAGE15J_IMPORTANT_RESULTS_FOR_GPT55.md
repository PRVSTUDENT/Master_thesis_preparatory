# Stage 15J Important Results For GPT-5.5 Analysis

## Run Outcome

PBS job `1333807.mmaster02` (`stage15j_final_multi`) completed with scheduler exit status `0` on 2026-05-28. The wrapper log reports:

- Host: `mfatnode004.cluster`
- Active workers: `40`
- Stop guard: `70800` seconds
- Resume mode: `1`
- Final runner message: `Stage 15J finished: 40 cases`
- Postprocessing message: `wrote Stage 15J transferability postprocessing outputs`

The run used continuous real-NEML workers per case. It did not use the older 10,000-cycle chunk relaunch strategy.

## Headline Results

From `STAGE15J_MASTER_SUMMARY.md`:

| Metric | Value |
|---|---:|
| Case count | 40 |
| Failed cases | 0 |
| Minimum final cycle | 557136 |
| Maximum final cycle | 2000000 |
| Clean transferability cases | 25 |
| Aggressive but stable cases | 7 |
| Diagnostic B2 cases | 5 |
| Incomplete below 500k | 0 |

Completion status counts from `STAGE15J_CASE_COMPLETION_SUMMARY.csv`:

| Status | Count |
|---|---:|
| `completed_extension` | 8 |
| `completed_primary` | 9 |
| `stopped_by_time_guard` | 23 |

Classification counts from `STAGE15J_TRANSFERABILITY_CLASSIFICATION.csv`:

| Classification | Count |
|---|---:|
| `clean_transferability_case` | 25 |
| `aggressive_but_stable` | 7 |
| `borderline_or_time_limited` | 3 |
| `diagnostic_b2_case` | 5 |

## Borderline Cases

The only borderline/time-limited cases were aggressive B1 stress paths with high amplitudes:

| Case | Stress min | Stress max | Final cycle |
|---|---:|---:|---:|
| `B1_aggr_m100_amp260` | -160 | 360 | 557136 |
| `B1_aggr_m70_amp260` | -190 | 330 | 582485 |
| `B1_aggr_m80_amp260` | -180 | 340 | 682736 |

These are not failures. They are stable but too expensive/severe to reach the primary target within the 19h40m job window.

## Canonical B1 Repeat Check

The canonical `B1_grid_mean50_amp200` repeat was compared with the Stage 15G long B1 reference at preserved overlapping cycles. The last overlap cycle was `1500000`.

At cycle `1500000`:

| Quantity | Stage 15J | Stage 15G | Absolute difference |
|---|---:|---:|---:|
| `strain_mean` | 45.70391764596161 | 55.45267197534096 | 9.748754329379352 |
| `ratcheting_strain` | 45.689947687551395 | 55.43870201693075 | 9.748754329379352 |

The comparison data are in `STAGE15J_CANONICAL_B1_REPEAT_CHECK.csv`.

## Thesis Interpretation

Stage 15J confirms that the real-NEML Chaboche ratcheting model remains numerically stable across a B1-type asymmetric stress neighbourhood. The clean B1 grid cases support transferability of the accepted adaptive cycle-jump strategy. Aggressive B1 cases remain stable but show stronger inelastic accumulation and need stricter jump-size control. B2 cases remain diagnostic and are not the primary thesis cycle-jump target.

The strongest thesis-ready conclusion is: use a robust B1-type adaptive ratcheting benchmark, not a universal fixed-jump extrapolation rule.

## Artifact Map

Use these files for deeper analysis:

- `STAGE15J_MASTER_SUMMARY.md`: final narrative summary and thesis conclusion.
- `STAGE15J_CASE_COMPLETION_SUMMARY.csv`: one row per case with final cycle, status, and output paths.
- `STAGE15J_TRANSFERABILITY_CLASSIFICATION.csv`: classification of clean, aggressive, borderline, and diagnostic cases.
- `STAGE15J_TARGET_CYCLE_VALUES.csv`: compact preserved target-cycle values for all cases.
- `STAGE15J_CANONICAL_B1_REPEAT_CHECK.csv`: Stage 15J vs Stage 15G canonical B1 overlap comparison.
- `STAGE15J_GLOBAL_STATUS.txt`: final global worker status at stop guard.
- `logs/STAGE15J_FULL_LOG.txt`: wrapper execution log.
- `plots/STAGE15J_final_cycle_by_case.svg`: final cycle reached by case.
- `plots/STAGE15J_final_accumulated_inelastic_by_case.svg`: final accumulated inelastic strain by case.
- `plots/STAGE15J_b1_transferability_map.svg`: B1 transferability map.
- `plots/STAGE15J_selected_loop_examples.svg`: selected hysteresis loop examples.
