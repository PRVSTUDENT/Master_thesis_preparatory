# Stage 16N-R4M Result

## Classification

R4M finished successfully and is a scientific pass for the 250 -> 270 -> 500 target-270 true-jump gate.

- PBS job: `1353942.mmaster02`
- Controller: `R4M_250branch_compact_restart_source_controller`
- Job name: `stage16n_r4m_compact_source`
- Classification: `target270_pass`
- Target: regenerate cycle-250 source, then continue 271 -> 500 from target 270
- R4J9/R4J10: blocked
- 505 branch: parked

## Restart-Source Recovery

R4M regenerated a complete cycle-250 restart-source package with the exact basename required by the R4L2/D1 blocker:

```text
stage16n_r1b_restart_ref_250cycles
```

The source package included all required files in scratch:

| extension | size | note |
| --- | ---: | --- |
| `.odb` | 523M | required solved output database recovered by regeneration |
| `.stt` | 276G | large restart state, scratch-only |
| `.res` | 36M | restart companion |
| `.mdl` | 61M | restart companion |
| `.prt` | 48K | restart companion |
| `.sim` | 2.1M | restart companion |
| `.sta` | 1.4M | source solve status |

This confirms the previous R4L2-D1 failure was a missing-source-package blocker, not a scientific true-jump failure.

## Target-270 Comparison

The continuation comparison reached cycle 500 and passed:

| metric | value |
| --- | ---: |
| status | `pass` |
| max global error | 0.39923577% |
| max primary-local error | 3.9830029% |
| diagnostic S11 error | 0.1398007% |

Largest listed comparison components:

- `RF1_max`: 0.39923577%
- `loop_area_abs`: 0.31779856%
- `HOLE_RING_MISES_MAX`: 0.048681883%
- `HOLE_RING_SDV1_MAX`: 3.9830029%
- `HOLE_RING_SDV8_MAX`: 1.0667941%
- `HOLE_RING_SDV11_MAX`: 1.8988424%
- `HOLE_RING_S11_MAX_ABS`: 0.1398007%

## PBS Accounting

PBS finished with `Exit_status=0` and `Stageout_status=1`. The stage-out warning is treated as an infrastructure warning only, because the lightweight evidence was recovered and the controller classification/comparison files are present.

| item | value |
| --- | ---: |
| queue | `mediumq` |
| host | `mnode001` |
| requested cores | 16 |
| requested memory | 90gb |
| requested walltime | 24:00:00 |
| walltime used | 11:05:25 |
| cput used | 48:19:32 |
| PBS `cpupercent` | 654 |
| average active cores from cput/walltime | about 4.36 / 16 |
| average active cores implied by `cpupercent` | about 6.54 / 16 |
| memory used | 94372028kb |

## Storage And Cleanup

Pre-submit storage gate on 2026-06-23:

- `/scratch9`: 33T total, 7.1T used, 26T free, 22% used
- `/scratch`: 101T total, 82T used, 19T free, 82% used
- `/home`: 17T total, 13T used, 3.4T free, 80% used
- `/scratch9/pr21vyci`: about 2.7T

End-of-job storage record:

- `/scratch9`: 33T total, 7.8T used, 25T free, 24% used
- `/scratch`: 101T total, 82T used, 19T free, 82% used
- `/home`: 17T total, 13T used, 3.4T free, 80% used
- `/scratch9/pr21vyci`: about 3.4T

The R4M scratch case was cleaned after classification and was about 3.4M when checked. No top-level heavy Abaqus output files remained in the R4M scratch case after cleanup.

## Evidence Files

Important lightweight evidence in this directory:

- `qstat_1353942_finished_full.txt`
- `STAGE16N_R4M_CONTROLLER_STATUS.md`
- `STAGE16N_R4M_SOURCE_PACKAGE_MANIFEST.md`
- `STAGE16N_R4M_TARGET270_COMPARISON_SUMMARY.txt`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_comparison_summary.csv`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_comparison_details.csv`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_cycle_metrics.csv`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_selected_cycle_local_states.csv`
- `stage16n_r1b_restart_ref_250cycles_sta_tail.txt`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_sta_tail.txt`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_dat_tail.txt`
- `stage16n_r4m_target270_jump_250_to_270_solve_271_to_500_msg_tail.txt`
- `_logs/`

## Next Safe Step

R4M repairs the missing complete R1B restart-source package only within a storage-light, scratch-cleaned controller and proves target 270. Do not run R4J9/R4J10 or any 505-branch job from this result. The next useful 250-branch work should be a controlled target-280 or nearby confirmation using the R4M pattern, with the same datacheck gate, lightweight copy-back, and heavy cleanup rules.
