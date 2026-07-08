# Stage 16N R4I Buffer Diagnostic Attempt Result

Updated: 2026-06-20.

## Live job check

`qstat -u pr21vyci` returned no active jobs on 2026-06-20 06:27 CEST. The submitted R4I jobs and the archive inventory job were therefore checked through PBS history with `qstat -x -f`.

## PBS result

| Case | PBS job | Host | Start | Finish | Walltime | CPU time | CPU percent | Memory | Exit status | Stageout status |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| R4I1 deck clone 250--281, restart 280--500 | 1350232 | mnode101 | Fri Jun 19 05:29:11 2026 | Fri Jun 19 10:42:31 2026 | 05:13:15 | 20:07:50 | 558 | 94379784 kb | 1 | 1 |
| R4I2 buffer 250--300, restart 280--500 | 1350233 | mnode102 | Fri Jun 19 05:29:12 2026 | Fri Jun 19 11:12:51 2026 | 05:43:35 | 21:39:22 | 587 | 94377932 kb | 1 | 1 |
| R4I3 buffer 250--300, restart 270--500 | 1350234 | mnode101 | Fri Jun 19 10:42:34 2026 | Fri Jun 19 16:39:16 2026 | 05:56:36 | 22:10:57 | 569 | 94375908 kb | 1 | 1 |
| R4I4 buffer 500--525, restart 505--750 | 1350235 | mnode104 | Fri Jun 19 11:12:51 2026 | Fri Jun 19 16:39:13 2026 | 05:26:16 | 20:27:07 | 565 | 94375908 kb | 1 | 1 |

PBS marked all four R4I jobs failed, but the retained stdout shows that this is a post-solve workflow failure rather than an Abaqus continuation failure. For every case, the source solve completed, the datacheck completed, the continuation solve completed, and the extractor wrote cycle metrics plus selected-cycle loop/local-state CSVs.

## Failure point

The wrapper failed when `stage16n_compare_r3j_jump_against_reference.py` tried to open missing reference CSVs from the remote mirror:

- R4I1--R4I3: `../../../stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv`
- R4I4: `../../../stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv`

Because the comparison step raised `FileNotFoundError`, PBS recorded `Exit_status=1` and `Stageout_status=1`. The generated R4I metrics and selected-cycle CSVs were not preserved in the `/home` mirror. By the time of the follow-up check, `/scratch/pr21vyci` had only 48K in use, so the scratch run directories were no longer available for recovery.

## Archive inventory job

The archive inventory job `1350236.mmaster02` finished with `Exit_status=0` and `Stageout_status=1`. It ran in dry-run plan mode only. It did not delete files. The generated inventory contained only the header row and both the delete-candidate and keep lists were empty:

- `hpc_lightweight_stage_archive/heavy_file_inventory_20260619_163917.tsv`
- `hpc_lightweight_stage_archive/delete_candidates_20260619_163917.txt`
- `hpc_lightweight_stage_archive/keep_heavy_files_20260619_163917.txt`

## Interpretation

R4I cannot yet be classified using the R4H/R4I decision table. The solver evidence says all four source and continuation runs completed, including the intended restart reads:

- R4I1 restart read: source step 280, increment 54.
- R4I2 restart read: source step 280, increment 56.
- R4I3 restart read: source step 270, increment 60.
- R4I4 restart read: source step 505, increment 54.

However, the comparison CSVs needed to decide pass/review/fail were lost with the scratch cleanup. R4J9/R4J10 therefore remain blocked.

## Lightweight evidence saved

Retained lightweight evidence now exists in each R4I case folder:

- `qstat_<jobid>_finished_full.txt`
- `<case>.pbs.out`

The archive dry-run evidence is under `hpc_lightweight_stage_archive/`.

No heavy Abaqus artifacts were copied or committed.
