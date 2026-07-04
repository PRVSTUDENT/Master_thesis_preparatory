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

## Skipped submit attempts

Three earlier F-chain submissions stopped before Abaqus because the predecessor self-gate was too strict for the repaired R4Q3 status layout:

- `1363409`--`1363412`: selected an incompatible older block-summary schema.
- `1363435`--`1363439`: found the correct R4Q3 completion row but rejected the `passed` preflight status file.
- `1363512`--`1363516`: the repaired status file contained a UTF-8 BOM, so an anchored status grep failed.

These attempts all ended in seconds with `Exit_status=0` and no Abaqus solve. The runner was corrected before the active `1363629`--`1363633` chain.
