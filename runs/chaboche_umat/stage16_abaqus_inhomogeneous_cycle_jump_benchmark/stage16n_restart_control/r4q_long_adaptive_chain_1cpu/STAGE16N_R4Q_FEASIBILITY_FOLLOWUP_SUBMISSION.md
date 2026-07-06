# Stage 16N R4Q Feasibility Follow-up Submission

Updated: 2026-07-04 01:58 CEST

## Scope

R4Q3 reached cycle1000 cleanly but failed the strict primary-local 5% accuracy gate after reference repair:

- max global error: `2.330504e-05%`
- max primary-local error: `6.2795526%`
- controlling signal: `HOLE_RING_SDV1_MAX`
- diagnostic S11 error: `0.00031922278%`

The follow-up jobs are therefore explicitly classified as feasibility-only continuation after the cycle1000 accuracy fail. They are not accuracy-validation jobs and do not validate the adaptive rule beyond cycle1000.

## No-solver diagnostics

The no-Abaqus R4Q3D diagnostics completed locally:

- `R4Q3D1_local_error_decomposition.csv`: ranks all retained local scalar errors; the top metric is `HOLE_RING_SDV1_MAX` at `6.27955257%`.
- `R4Q3D2_HOLE_RING_SDV1_trace_compare.csv`: shows the repaired reference has selected local anchors through cycle1000, but R4Q3 retained local-state history only at cycle1000, so the lightweight evidence cannot distinguish sudden versus gradual SDV1 deviation.
- `R4Q3D3_tolerance_sensitivity.csv`: R4Q3 fails the official 5% primary-local gate but would pass 7.5% and 10% sensitivity gates while global and S11 remain below 1%.

The retained aggregate local-state CSVs do not include element/integration-point records, so the exact `HOLE_RING_SDV1_MAX` hotspot location cannot be identified from the current lightweight evidence.

## Feasibility queue

The active corrected feasibility-only dependent chain is:

- R4Q4F `1363629.mmaster02`: source1000 -> target1021, solve 1022--1250, dependency none, running at the live snapshot.
- R4Q5F `1363630.mmaster02`: source1250 -> target1271, solve 1272--1500, dependency `afterok:1363629.mmaster02`.
- R4Q6F `1363631.mmaster02`: source1500 -> target1521, solve 1522--1750, dependency `afterok:1363630.mmaster02`.
- R4Q7F `1363633.mmaster02`: source1750 -> target1771, solve 1772--2000, dependency `afterok:1363631.mmaster02`.

All four jobs use:

- `R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1`
- `classification_scope=feasibility_only_after_cycle1000_accuracy_fail`
- 1 CPU, 30 GB, 24 h
- guarded submission through `/home/pr21vyci/bin/qsub_abq_guarded`
- scratch-only execution with lightweight copy-back

The submit gate recorded no active queue before the corrected submission, `/scratch9/pr21vyci=4.2T`, and verified the R4Q3 heavy source files under `/scratch/pr21vyci/stage16n_r4q3_continue_from_cycle750_1cpu/1362636.mmaster02`.

## Live status

At the live post-submit snapshot, R4Q4F `1363629.mmaster02` was running in `mediumq` and had passed the predecessor self-gate:

- status: `running`
- phase: `prepare`
- restart record: `STEP=937`, `INC=63`
- detail: `source=1000 target=1021 solve=1022-1250 restart=937/63`

R4Q5F--R4Q7F were held behind PBS dependencies. Do not queue beyond cycle2000 until this feasibility chain is classified.

## Cycle5000 extension

Updated 2026-07-06 08:03 CEST: R4Q4F--R4Q7F completed cleanly through cycle2000, still as feasibility-only continuation after the R4Q3 cycle1000 strict local accuracy fail. The next feasibility-only chain was submitted through `/home/pr21vyci/bin/qsub_abq_guarded` with 1 CPU, 30 GB, 24 h per job, scratch-only execution, lightweight copy-back, strict `afterok` dependencies, and `R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1`.

- R4Q8F `1364994.mmaster02`: source2000 -> target2021, solve 2022--2250, dependency none.
- R4Q9F `1364995.mmaster02`: source2250 -> target2271, solve 2272--2500, dependency `afterok:1364994.mmaster02`.
- R4Q10F `1364996.mmaster02`: source2500 -> target2521, solve 2522--2750, dependency `afterok:1364995.mmaster02`.
- R4Q11F `1364997.mmaster02`: source2750 -> target2771, solve 2772--3000, dependency `afterok:1364996.mmaster02`.
- R4Q12F `1364998.mmaster02`: source3000 -> target3021, solve 3022--3250, dependency `afterok:1364997.mmaster02`.
- R4Q13F `1364999.mmaster02`: source3250 -> target3271, solve 3272--3500, dependency `afterok:1364998.mmaster02`.
- R4Q14F `1365000.mmaster02`: source3500 -> target3521, solve 3522--3750, dependency `afterok:1364999.mmaster02`.
- R4Q15F `1365001.mmaster02`: source3750 -> target3771, solve 3772--4000, dependency `afterok:1365000.mmaster02`.
- R4Q16F `1365002.mmaster02`: source4000 -> target4021, solve 4022--4250, dependency `afterok:1365001.mmaster02`.
- R4Q17F `1365003.mmaster02`: source4250 -> target4271, solve 4272--4500, dependency `afterok:1365002.mmaster02`.
- R4Q18F `1365004.mmaster02`: source4500 -> target4521, solve 4522--4750, dependency `afterok:1365003.mmaster02`.
- R4Q19F `1365005.mmaster02`: source4750 -> target4771, solve 4772--5000, dependency `afterok:1365004.mmaster02`.

The post-submit live snapshot shows R4Q8F running and R4Q9F--R4Q19F held behind the strict dependency chain. R4Q19F stops at cycle5000; no jobs were queued beyond cycle5000.

The R4Q3N exact/native diagnostic was also submitted. The first guarded attempt `1365006.mmaster02` self-gated before Abaqus because the diagnostic gate did not recognize the older R4Q2 status layout. The corrected guarded retry `1365007.mmaster02` is running and uses the R4Q2 cycle750 source without the 750 -> 771 extrapolated overwrite.

## Skipped submit attempts

Three earlier F-chain submissions stopped before Abaqus because the predecessor self-gate was too strict for the repaired R4Q3 status layout:

- `1363409`--`1363412`: selected an incompatible older block-summary schema.
- `1363435`--`1363439`: found the correct R4Q3 completion row but rejected the `passed` preflight status file.
- `1363512`--`1363516`: the repaired status file contained a UTF-8 BOM, so an anchored status grep failed.

These attempts all ended in seconds with `Exit_status=0` and no Abaqus solve. The runner was corrected before the active `1363629`--`1363633` chain.
