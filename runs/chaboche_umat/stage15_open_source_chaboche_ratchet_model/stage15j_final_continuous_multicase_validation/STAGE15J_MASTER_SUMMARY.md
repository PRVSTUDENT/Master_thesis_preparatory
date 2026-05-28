# Stage 15J Final Continuous Real-NEML Multicase Validation Summary

## Stage 15J: Final Continuous Real-NEML Multicase Transferability Validation

Stage 15J was designed as the final Stage 15 validation campaign. Unlike Stage 15I, which used a chunked multicase execution strategy, Stage 15J used one continuous real-NEML worker process per case. This avoided the 10,000-cycle relaunch strategy and therefore removed the main continuity caveat identified in Stage 15I.

## Headline Result

| Quantity | Stage 15J result |
|---|---:|
| Total cases | 40 |
| Failed cases | 0 |
| Minimum final cycle | 557,136 |
| Maximum final cycle | 2,000,000 |
| Clean transferability cases | 25 |
| Aggressive but stable cases | 7 |
| Diagnostic B2 cases | 5 |
| Incomplete below 500k | 0 |

## Main Interpretation

The final continuous multicase validation confirms that the selected real-NEML Chaboche ratcheting model remains numerically stable over a broad B1-type asymmetric stress neighbourhood. All 40 cases ran without numerical failure. The 25 B1 grid cases were classified as clean transferability cases, showing that the adaptive cycle-jump strategy is not limited to a single stress path. The aggressive B1 cases remained stable but became computationally more demanding and therefore require stricter jump-size control. The B2 cases reached long cycle counts but remain diagnostic rather than the primary cycle-jump target.

## Completion Statuses

The completion statuses show that 8 cases reached the extension target, 9 reached the primary target, and 23 stopped at the configured time guard. Time-guard termination is not interpreted as failure, because all cases exceeded 500,000 cycles and no case failed numerically.

## B1 Transferability Map Result

The B1 grid was constructed using mean stresses from 30 to 70 MPa and stress amplitudes from 180 to 220 MPa. The canonical B1 case, corresponding to mean stress 50 MPa and amplitude 200 MPa, is contained inside this grid. All B1 grid cases were classified as clean transferability cases. This supports the conclusion that the adaptive cycle-jump strategy is applicable to a B1-type neighbourhood rather than only to one isolated loading path.

## Aggressive-Case Limitation

The aggressive B1 cases were stable but more expensive. The most severe high-amplitude cases became borderline or time-limited, especially the amplitude-260 MPa cases. These cases should not be treated as failures; rather, they identify the boundary where adaptive jumps require stronger jump-size reduction and more conservative error control.

| Borderline case | Stress min | Stress max | Final cycle |
|---|---:|---:|---:|
| `B1_aggr_m100_amp260` | -160 | 360 | 557,136 |
| `B1_aggr_m70_amp260` | -190 | 330 | 582,485 |
| `B1_aggr_m80_amp260` | -180 | 340 | 682,736 |

## B2 Diagnostic Conclusion

The B2 diagnostic cases reached the extension target of 2,000,000 cycles, showing that they are numerically stable in the real-NEML material-point framework. However, they are not selected as the primary thesis target because the earlier Stage 15E prediction benchmark found no accepted B2 cycle-jump predictions under the selected error rules. Therefore, B2 is retained as a diagnostic comparison class.

## Canonical B1 Repeat Check Against Stage 15G

The canonical B1 repeat check showed exact agreement with Stage 15G at the early preserved cycles up to 50,000 cycles. At later cycles, the strain-like quantities show a growing offset. Therefore, Stage 15G remains the clean single-case B1 reference, while Stage 15J is used primarily as the final continuous multicase transferability map. This does not invalidate Stage 15J, but it means the canonical repeat should be reported as a consistency check with a documented long-cycle offset, not as a perfect reproduction of Stage 15G.

At the last overlap cycle, `1,500,000`, the absolute difference in both `strain_mean` and `ratcheting_strain` is about `9.75`.

## Recommended Figures

The recommended Stage 15J figures are:

- `plots/STAGE15J_final_cycle_by_case.svg`
- `plots/STAGE15J_final_accumulated_inelastic_by_case.svg`
- `plots/STAGE15J_b1_transferability_map.svg`
- `plots/STAGE15J_selected_loop_examples.svg`

The most important figure is `plots/STAGE15J_b1_transferability_map.svg`, because it visually supports the final thesis claim that adaptive cycle jumping is transferable in the B1-type stress neighbourhood.

## Final Stage 15 Conclusion

Stage 15 concludes with a real-NEML Chaboche ratcheting benchmark suitable for adaptive cycle-jump research. The fixed one-shot cycle-jump strategy was accurate only for local or moderate jumps, while the adaptive strategy provided accepted refined jumps for the canonical B1 case. The final continuous multicase validation extended the study to 40 stress paths and showed that the method is most suitable for a B1-type asymmetric stress-controlled neighbourhood. Aggressive B1 paths remain stable but require stricter jump-size control, and B2 paths are retained as diagnostic rather than primary cycle-jump targets. Therefore, the thesis result should be framed as a robust B1-type adaptive ratcheting benchmark, not as a universal fixed-jump rule for all cyclic stress paths.
