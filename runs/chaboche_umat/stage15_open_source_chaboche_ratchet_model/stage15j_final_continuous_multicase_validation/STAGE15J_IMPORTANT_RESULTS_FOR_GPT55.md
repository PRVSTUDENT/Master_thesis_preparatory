# Stage 15J Important Results For GPT-5.5 Analysis

## Run Outcome

PBS job `1333807.mmaster02` (`stage15j_final_multi`) completed with scheduler exit status `0` on 2026-05-28. The wrapper log reports:

- Host: `mfatnode004.cluster`
- Active workers: `40`
- Stop guard: `70800` seconds
- Resume mode: `1`
- Final runner message: `Stage 15J finished: 40 cases`
- Postprocessing message: `wrote Stage 15J transferability postprocessing outputs`

The run used continuous real-NEML workers per case. It did not use the older 10,000-cycle chunk relaunch strategy, so Stage 15J should be treated as the final continuous multicase transferability validation.

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

Important correction: the canonical B1 repeat does not fully agree with Stage 15G over the full overlap range. It shows exact agreement only at the early preserved cycles up to `50000` cycles. At later cycles, the strain-like quantities show a growing offset. Therefore, Stage 15G remains the clean single-case B1 long reference, while Stage 15J is used primarily as the final continuous multicase transferability map.

At cycle `1500000`:

| Quantity | Stage 15J | Stage 15G | Absolute difference |
|---|---:|---:|---:|
| `strain_mean` | 45.70391764596161 | 55.45267197534096 | 9.748754329379352 |
| `ratcheting_strain` | 45.689947687551395 | 55.43870201693075 | 9.748754329379352 |

The comparison data are in `STAGE15J_CANONICAL_B1_REPEAT_CHECK.csv`. Report this as a consistency check with a documented long-cycle offset, not as a perfect reproduction of Stage 15G.

## Thesis Interpretation

The final continuous multicase validation confirms that the selected real-NEML Chaboche ratcheting model remains numerically stable over a broad B1-type asymmetric stress neighbourhood. All 40 cases ran without numerical failure. The 25 B1 grid cases were classified as clean transferability cases, showing that the adaptive cycle-jump strategy is not limited to a single stress path. The aggressive B1 cases remained stable but became computationally more demanding and therefore require stricter jump-size control. The B2 cases reached long cycle counts but remain diagnostic rather than the primary cycle-jump target.

The B1 grid was constructed using mean stresses from 30 to 70 MPa and stress amplitudes from 180 to 220 MPa. The canonical B1 case, corresponding to mean stress 50 MPa and amplitude 200 MPa, is contained inside this grid. All B1 grid cases were classified as clean transferability cases.

The strongest thesis-ready conclusion is: Stage 15 concludes with a real-NEML Chaboche ratcheting benchmark suitable for adaptive cycle-jump research. The fixed one-shot cycle-jump strategy was accurate only for local or moderate jumps, while the adaptive strategy provided accepted refined jumps for the canonical B1 case. The final continuous multicase validation extended the study to 40 stress paths and showed that the method is most suitable for a B1-type asymmetric stress-controlled neighbourhood. Aggressive B1 paths remain stable but require stricter jump-size control, and B2 paths are retained as diagnostic rather than primary cycle-jump targets. Therefore, the thesis result should be framed as a robust B1-type adaptive ratcheting benchmark, not as a universal fixed-jump rule for all cyclic stress paths.

## Recommended Figures

Use these four Stage 15J figures:

- `plots/STAGE15J_final_cycle_by_case.svg`
- `plots/STAGE15J_final_accumulated_inelastic_by_case.svg`
- `plots/STAGE15J_b1_transferability_map.svg`
- `plots/STAGE15J_selected_loop_examples.svg`

The most important one is `plots/STAGE15J_b1_transferability_map.svg`, which visually supports the final thesis claim that adaptive cycle jumping is transferable in the B1-type stress neighbourhood.

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
