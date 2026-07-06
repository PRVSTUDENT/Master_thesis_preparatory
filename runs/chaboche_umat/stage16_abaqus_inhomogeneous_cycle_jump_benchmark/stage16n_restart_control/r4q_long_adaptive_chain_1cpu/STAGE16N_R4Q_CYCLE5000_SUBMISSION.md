# Stage 16N R4Q Cycle5000 Feasibility Submission

Updated: 2026-07-06 08:03 CEST

## Classification

`classification_scope=feasibility_only_after_cycle1000_accuracy_fail`

R4Q3 reached cycle1000 technically cleanly, but the repaired strict accuracy comparison failed the 5% primary-local gate:

- max global error: `2.330504e-05%`
- max primary-local error: `6.2795526%`
- controlling signal: `HOLE_RING_SDV1_MAX`
- diagnostic S11 error: `0.00031922278%`

Therefore R4Q8F--R4Q19F are technical feasibility continuation only. They do not validate the adaptive cycle-jump rule beyond cycle1000.

## Pre-submit Gate

The required pre-submit checks were run on 2026-07-06 before submission:

- `qstat -u pr21vyci`: no active jobs before the R4Q8F--R4Q19F submission.
- `/scratch9`: 33T total, 11T used, 23T free, 33% used.
- `/scratch`: 101T total, 85T used, 16T free, 85% used.
- `/home`: 17T total, 14T used, 2.8T free, 83% used.
- `/scratch9/pr21vyci`: 6.2T, above the 5T warning threshold; the required size audit was run.
- R4Q7F cycle2000 heavy source verified at `/scratch/pr21vyci/stage16n_r4q7f_continue_from_cycle1750_1cpu/1363633.mmaster02`.
- Required heavy files verified for the cycle2000 source: `.sta`, `.res`, `.stt`, `.mdl`, `.prt`, `.sim`, `.odb`.
- R4Q2 cycle750 heavy source verified for the R4Q3N diagnostic at `/scratch/pr21vyci/stage16n_r4q2_continue_from_cycle500_1cpu/1362597.mmaster02`.

## Submitted Chain

All jobs were submitted through `/home/pr21vyci/bin/qsub_abq_guarded` with 1 CPU, 30 GB, 24 h, scratch-only execution, lightweight copy-back, and `R4Q_ALLOW_FEASIBILITY_AFTER_1000_FAIL=1`.

| Job | PBS ID | Dependency | Block |
| --- | --- | --- | --- |
| R4Q8F | `1364994.mmaster02` | none | source2000 -> target2021, solve 2022--2250 |
| R4Q9F | `1364995.mmaster02` | `afterok:1364994.mmaster02` | source2250 -> target2271, solve 2272--2500 |
| R4Q10F | `1364996.mmaster02` | `afterok:1364995.mmaster02` | source2500 -> target2521, solve 2522--2750 |
| R4Q11F | `1364997.mmaster02` | `afterok:1364996.mmaster02` | source2750 -> target2771, solve 2772--3000 |
| R4Q12F | `1364998.mmaster02` | `afterok:1364997.mmaster02` | source3000 -> target3021, solve 3022--3250 |
| R4Q13F | `1364999.mmaster02` | `afterok:1364998.mmaster02` | source3250 -> target3271, solve 3272--3500 |
| R4Q14F | `1365000.mmaster02` | `afterok:1364999.mmaster02` | source3500 -> target3521, solve 3522--3750 |
| R4Q15F | `1365001.mmaster02` | `afterok:1365000.mmaster02` | source3750 -> target3771, solve 3772--4000 |
| R4Q16F | `1365002.mmaster02` | `afterok:1365001.mmaster02` | source4000 -> target4021, solve 4022--4250 |
| R4Q17F | `1365003.mmaster02` | `afterok:1365002.mmaster02` | source4250 -> target4271, solve 4272--4500 |
| R4Q18F | `1365004.mmaster02` | `afterok:1365003.mmaster02` | source4500 -> target4521, solve 4522--4750 |
| R4Q19F | `1365005.mmaster02` | `afterok:1365004.mmaster02` | source4750 -> target4771, solve 4772--5000 |

R4Q19F is the final queued block. No jobs were queued beyond cycle5000.

## Diagnostic Control

The requested diagnostic was submitted as `R4Q3N_exact_native_control_750_to_1000`.

- First guarded attempt: `1365006.mmaster02`, finished in 21 s with `Exit_status=0` and self-gated before Abaqus because the diagnostic status matcher did not recognize the historical R4Q2 status layout. This is infrastructure-only and not a diagnostic solve.
- Corrected guarded attempt: `1365007.mmaster02`, submitted at 2026-07-06 08:03 CEST and running in the live verification snapshot.

The corrected diagnostic uses the R4Q2 cycle750 source and does not apply the 750 -> 771 extrapolated overwrite. Its purpose is to determine whether the R4Q3 `HOLE_RING_SDV1_MAX` error comes from the extrapolated jump state or from local metric/reference sensitivity.

## Live Scheduler Snapshot

At the post-submit live snapshot, `1364994.mmaster02` (R4Q8F) and `1365007.mmaster02` (corrected R4Q3N diagnostic) were running in `mediumq`. R4Q9F--R4Q19F were held behind strict `afterok` dependencies.

## Evidence Files

- `R4Q8F_TO_R4Q19F_SUBMIT_GATE.txt`
- `R4Q8F_TO_R4Q19F_SCRATCH9_SIZE_AUDIT.txt`
- `R4Q8F_TO_R4Q19F_SUBMITTED_JOBS.txt`
- `R4Q3N_EXACT_NATIVE_CORRECTED_SUBMISSION_STATUS.txt`
- `qstat_r4q8f_to_r4q19f_plus_r4q3n_1365007_live_verify.txt`
- `qstat_1365007_post_submit_f.txt`
