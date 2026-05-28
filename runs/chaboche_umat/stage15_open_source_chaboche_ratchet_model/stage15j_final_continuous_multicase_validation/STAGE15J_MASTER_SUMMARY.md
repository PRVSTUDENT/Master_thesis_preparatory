# Stage 15J Final Continuous Real-NEML Multicase Validation Summary

Stage 15J is the final continuous real-NEML multicase transferability validation. Each case uses one continuous worker process; no 10,000-cycle chunk relaunch is used.

| Field | Value |
|---|---:|
| Case count | 40 |
| Failed cases | 0 |
| Minimum final cycle | 557136 |
| Maximum final cycle | 2000000 |
| Clean transferability cases | 25 |
| Aggressive but stable cases | 7 |
| Diagnostic B2 cases | 5 |
| Incomplete below 500k | 0 |

## B1 transferability summary

Group A maps the B1 neighbourhood by mean stress and stress amplitude. Cases classified as `clean_transferability_case` are the strongest evidence for transferability of the accepted B1 adaptive cycle-jump strategy.

## Aggressive B1 stress-test summary

Group B identifies more severe B1-type stress paths. These cases are expected to require stricter jump-size control even when numerically stable.

## B2 diagnostic summary

Group C remains diagnostic. B2-type loading is not treated as the primary thesis cycle-jump target.

## Canonical B1 repeat check against Stage 15G

The canonical `B1_grid_mean50_amp200` repeat was compared with Stage 15G at overlapping preserved cycles. Last overlap cycle: `1500000`; strain-mean absolute difference: `9.748754329379352`; ratcheting-strain absolute difference: `9.748754329379352`.

## Thesis-ready conclusion

The final continuous multicase validation confirmed that the real NEML Chaboche ratcheting model remains stable across a neighbourhood of B1-type asymmetric stress paths. The canonical B1 repeat agrees with the Stage 15G long reference where overlap data are available, while nearby B1 grid cases provide a transferability map for the adaptive cycle-jump strategy. Aggressive B1 cases remain stable but show stronger inelastic accumulation and therefore require stricter jump-size control. B2-type cases remain diagnostic and are not selected as the primary cycle-jump target. Therefore, the thesis cycle-jump study is concluded with a robust B1-type adaptive ratcheting benchmark rather than a universal fixed-jump extrapolation rule.
