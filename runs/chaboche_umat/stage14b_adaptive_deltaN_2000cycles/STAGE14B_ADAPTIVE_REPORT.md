# Stage 14B Adaptive DeltaN Report

Generated: 2026-05-21 19:03:54

## Method

Adaptive blockwise cycle jumping with Abaqus/Standard recovery windows. DeltaN is selected from a local STATEV1 curvature estimate, then limited by safety factor and min/max bounds.

## Final Summary

- final_cycle: `2000`
- final_STATEV1: `28.4674358368`
- reference_STATEV1: `12.6968250275`
- final_statev1_error_pct: `124.209089872`
- final_S11: `-9611.54101562`
- reference_S11: `300.884613037`
- final_s11_error_pct: `3294.42756431`
- final_RIGHT_FACE_RF1_SUM: `-38446.1650391`
- reference_RIGHT_FACE_RF1_SUM: `1203.53845215`
- final_rf1_error_pct: `3294.42764545`
- outcome: `not_accepted`
- number_of_blocks: `30`
- solved_recovery_cycles: `291`
- skipped_cycles: `1669`
- effective_speedup_estimate: `6.64451827243`
- best_fixed_stage14_statev1_error_pct: `2.85226684954`
- best_fixed_stage14_strategy: `jump25`

## Block History

| Block | Base | Target | Recovery End | DeltaN | m STATEV1 | c STATEV1 | Est. local err % | Recovered STATEV1 | Status |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 10 | 35 | 45 | 25 | 0.00718564433711 | -1.10361725167e-06 | 0.138003001365 | 0.321219146252 | accepted_exploratory_success |
| 2 | 45 | 70 | 80 | 25 | 0.00714677146503 | -1.11262003667e-06 | 0.0695542722317 | 0.570977926254 | accepted_exploratory_success |
| 3 | 80 | 106 | 116 | 26 | 0.00710781982967 | -1.12255414333e-06 | 0.0502027940691 | 0.826469421387 | accepted_exploratory_success |
| 4 | 116 | 148 | 158 | 32 | 0.00706851482391 | -1.07288360667e-06 | 0.0521835556915 | 1.12290227413 | accepted_exploratory_success |
| 5 | 158 | 195 | 205 | 37 | 0.00702376025064 | -1.05301539167e-06 | 0.0521260290182 | 1.45253384113 | accepted_exploratory_success |
| 6 | 205 | 246 | 256 | 41 | 0.00697502068111 | -1.05301539167e-06 | 0.0509090885295 | 1.80773937702 | accepted_exploratory_success |
| 7 | 256 | 302 | 312 | 46 | 0.00692272186279 | -1.03314717667e-06 | 0.0514099162322 | 2.19484901428 | accepted_exploratory_success |
| 8 | 312 | 363 | 373 | 51 | 0.00686618259975 | -9.93410748333e-07 | 0.0507629991811 | 2.61309313774 | accepted_exploratory_success |
| 9 | 373 | 429 | 439 | 56 | 0.00680661201477 | -9.53674318333e-07 | 0.0499408744691 | 3.06171011925 | accepted_exploratory_success |
| 10 | 439 | 502 | 512 | 63 | 0.00674435070583 | -8.74201456667e-07 | 0.0497576634575 | 3.55338859558 | accepted_exploratory_success |
| 11 | 512 | 578 | 588 | 66 | 0.00667810440063 | -9.13937885e-07 | 0.0498368854423 | 4.06026601791 | accepted_exploratory_success |
| 12 | 588 | 660 | 670 | 72 | 0.00661189215524 | -8.74201456667e-07 | 0.0499508202738 | 4.60176086426 | accepted_exploratory_success |
| 13 | 670 | 747 | 757 | 77 | 0.00654350008283 | -8.74201456667e-07 | 0.0507592634407 | 5.17035484314 | accepted_exploratory_success |
| 14 | 757 | 842 | 852 | 85 | 0.00647415433611 | -7.94728598333e-07 | 0.0501857842349 | 5.78468084335 | accepted_exploratory_success |
| 15 | 852 | 947 | 957 | 95 | 0.00640201568604 | -7.15255735e-07 | 0.0504873449023 | 6.456138134 | accepted_exploratory_success |
| 16 | 957 | 1051 | 1061 | 94 | 0.00632640293666 | -7.94728596667e-07 | 0.0497971999721 | 7.11336803436 | accepted_exploratory_success |
| 17 | 1061 | 1166 | 1176 | 105 | 0.00625460488456 | -7.15255738333e-07 | 0.0507438317709 | 7.83187675476 | accepted_exploratory_success |
| 18 | 1176 | 1281 | 1291 | 105 | 0.00617722102574 | -7.15255736667e-07 | 0.046493181296 | 8.54152870178 | accepted_exploratory_success |
| 19 | 1291 | 1396 | 1406 | 105 | 0.00610406058175 | -6.35782876667e-07 | 0.0381679309469 | 9.24280738831 | accepted_exploratory_success |
| 20 | 1406 | 1511 | 1521 | 105 | 0.00603485107422 | -4.76837158333e-07 | 0.0266144249918 | 9.93640327454 | accepted_exploratory_success |
| 21 | 1521 | 1558 | 1568 | 37 | 0.00598771231515 | -7.15255737333e-06 | 0.0481979748105 | 10.2174482346 | accepted_exploratory_success |
| 22 | 1568 | 1593 | 1603 | 25 | 0.00585842132568 | -9.50495402017e-05 | 0.286600181251 | 10.4590616226 | accepted_exploratory_success |
| 23 | 1603 | 1628 | 1638 | 25 | 0.00784846714564 | -0.00094620386759 | 2.77504574742 | 10.9877710342 | not_accepted |
| 24 | 1638 | 1663 | 1673 | 25 | 0.0315156664167 | -0.00354560216269 | 9.40924264369 | 12.2103290558 | not_accepted |
| 25 | 1673 | 1698 | 1708 | 25 | 0.0459789548601 | -0.00250673294067 | 5.86351496516 | 13.835641861 | not_accepted |
| 26 | 1708 | 1813 | 1823 | 105 | 0.0499999182565 | -3.17891466666e-07 | 0.00918165346929 | 19.5894565582 | not_accepted |
| 27 | 1823 | 1928 | 1938 | 105 | 0.0499997820173 | 0 | 0 | 25.3464336395 | not_accepted |
| 28 | 1938 | 1974 | 1984 | 36 | 0.0500000544957 | 0 | 0 | 27.6534347534 | not_accepted |
| 29 | 1984 | 1988 | 1998 | 4 | 0.0500000544957 | 6.35782899998e-07 | 1.82608112975e-05 | 28.3604354858 | not_accepted |
| 30 | 1998 | 1999 | 2000 | 1 | 0.0500000544957 | 3.17891449999e-07 | 0 | 28.4674358368 | not_accepted |

## Interpretation

Compare this adaptive run against the completed fixed Stage 14 strategies. If STATEV1 remains above 1%, the limiting factor is likely recovery-window length, linear state prediction, or reinjection transient rather than only fixed DeltaN selection.
