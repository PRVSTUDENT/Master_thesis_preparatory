# Stage 16N R4Q Cycle-5000 Feasibility Chain Live Result

Checked: 2026-07-08 10:03 CEST on TU Freiberg PBS.

## Scheduler state

- R4Q8F `1364994.mmaster02` finished with `Exit_status=0`, `Stageout_status=1`, walltime `10:09:42`, and copied-back controller evidence.
- R4Q9F `1364995.mmaster02` finished with `Exit_status=0`, `Stageout_status=1`, walltime `09:27:56`, and copied-back controller evidence.
- R4Q10F `1364996.mmaster02` finished with `Exit_status=0`, `Stageout_status=1`, walltime `12:37:07`, and copied-back controller evidence.
- R4Q11F `1364997.mmaster02` finished with `Exit_status=0`, `Stageout_status=1`, walltime `10:29:28`, and copied-back controller evidence.
- R4Q12F `1364998.mmaster02` was running on `mnode023/2`, with walltime `07:18:04` at the check and restart point `STEP=2769, INC=57`.
- R4Q13F--R4Q19F `1364999.mmaster02`--`1365005.mmaster02` remain held behind strict `afterok` dependencies.

## Scientific classification

The completed R4Q8F--R4Q11F blocks are feasibility-only continuation after the R4Q3 cycle1000 strict-gate accuracy failure. They do not validate accuracy beyond cycle1000 and do not widen the accepted 250-branch true-jump boundary beyond target271.

Completed endpoint extractions:

- R4Q8F: source2000 -> target2021, solved 2022--2250, cycle2250 state extracted.
- R4Q9F: source2250 -> target2271, solved 2272--2500, cycle2500 state extracted.
- R4Q10F: source2500 -> target2521, solved 2522--2750, cycle2750 state extracted.
- R4Q11F: source2750 -> target2771, solved 2772--3000, cycle3000 state extracted.

Endpoint RF/loop metrics remain stable across the completed cycle5000-chain blocks:

| endpoint | RF1_max | RF1_min | RF1_mean | loop_area_abs |
| --- | ---: | ---: | ---: | ---: |
| 2250 | 2970.01662445 | -3065.62980652 | 352.421585721 | 580.000090221 |
| 2500 | 2970.0172348 | -3065.63053131 | 352.421655671 | 580.00001775 |
| 2750 | 2970.01766968 | -3065.63117981 | 352.42167823 | 579.999966069 |
| 3000 | 2970.01799011 | -3065.63172913 | 352.421677979 | 579.999915867 |

## Exact/native diagnostic

The corrected `R4Q3N_exact_native_control_750_to_1000` job `1365007.mmaster02` finished with `Exit_status=0`, `Stageout_status=1`, and `comparison_status=pass`. It used the R4Q2 cycle750 source, solved native cycles 751--1000, and explicitly did not apply the R4Q3 750 -> 771 extrapolated overwrite.

The cycle1000 diagnostic comparison reports:

- max global error: `3.1625025e-05%`
- max primary-local error: `4.1863684%`
- diagnostic S11 error: `0.00018241296%`

This supports the diagnosis that the R4Q3 strict-gate miss is tied to the extrapolated overwrite path or its local-state prediction, not to the native 750--1000 continuation or the repaired cycle1000 reference.
