# Stage 16N-R4H Restart-Source Diagnostic Submission

Date: 2026-06-17

## Reason

R4G resolved the main ambiguity: direct original native restarts are exact, but
source-split replay is not. R4H therefore keeps R4J9/R4J10 blocked and tests
whether the source-split problem is caused by second-generation restart files,
restart from the final step of a short source job, or source-split phase/history.

The attempted no-new-job source-target audit on the retained R4G source jobs was
not sufficient: the R4G4/R4G5 source ODB extraction reported no selected
field-output frames. R4H source decks therefore explicitly request field output
at the target/interior restart cycle and at the source end cycle.

## Safety Gate

- `qstat -u pr21vyci`: no pre-existing PBS jobs listed before submission.
- `/home`: 17T total, 14T used, 2.9T available, 83% used.
- `/scratch`: 110T total, 82T used, 29T available, 75% used.
- `/home/pr21vyci`: 3.6T.
- Large restart-state files remain excluded from GitHub; only setup/status and
  lightweight future evidence should be uploaded.

## Prepared Cases

| Case | Mode | Restart source | First solved cycle | Endpoint | Purpose |
| --- | --- | --- | --- | --- | --- |
| R4H1 | long replay restart | R4G1 at cycle 280 | CYCLE_0281 | 500 | Test restart record from a long direct replay. |
| R4H2 | interior source split | source 250--281, restart 280 | CYCLE_0281 | 500 | Test whether one extra source cycle fixes final-step restart inconsistency. |
| R4H3 | long replay restart | R4G1 at cycle 270 | CYCLE_0271 | 500 | Test restart record from a long direct replay at 270. |
| R4H4 | interior source split | source 250--271, restart 270 | CYCLE_0271 | 500 | Test one-extra-cycle source behavior at 270. |
| R4H5 | long replay restart | R4G6 at cycle 505 | CYCLE_0506 | 750 | Test 500-branch restart record from long direct replay. |
| R4H6 | interior source split | source 500--506, restart 505 | CYCLE_0506 | 750 | Test one-extra-cycle source behavior at 505. |

All continuation decks passed the first-solved-step gate. The interior
source-split decks write restart records throughout the short source solve:
R4H2 has 31 restart-write steps, R4H4 has 21, and R4H6 has 6.

## PBS Submission

Submitted in the requested order:

| Case | PBS job | Initial state | Host/comment |
| --- | --- | --- | --- |
| R4H1 | 1349085.mmaster02 | running | mnode100 |
| R4H2 | 1349086.mmaster02 | running | mnode101 |
| R4H3 | 1349087.mmaster02 | queued | teachingq running-job limit |
| R4H4 | 1349088.mmaster02 | queued | teachingq running-job limit |
| R4H5 | 1349089.mmaster02 | queued | teachingq running-job limit |
| R4H6 | 1349090.mmaster02 | queued | teachingq running-job limit |

All jobs request:

```text
select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
walltime=24:00:00
queue=teachingq
```

Initial PBS timestamps:

```text
R4H1/R4H2 ctime: Wed Jun 17 16:55:56--57 2026
R4H1/R4H2 stime: Wed Jun 17 16:55:59 2026
R4H3--R4H6 ctime: Wed Jun 17 16:55:57 2026
```

Early log check:

- R4H1 datacheck completed successfully and the continuation solve started.
- R4H2 source solve started successfully.

## Expected Classification Logic

- If R4H1/R4H3 pass, generated restart records from a restarted long replay can
  be valid.
- If R4H2/R4H4 pass, avoid restarting from the final step of a short source
  solve; run one extra cycle and restart from the interior target cycle.
- If R4H2/R4H4 fail, the issue is deeper than final-step restart writing.
- If R4H5/R4H6 pass, the 500-branch issue is mainly source-final-step or
  material-only overwrite related.
- R4J9/R4J10 remain blocked until R4H is classified.

## Evidence to Collect After Completion

For each R4H case, upload only lightweight files:

```text
STAGE16N_R4H_CASE_STATUS.md
*_comparison_summary.csv
*_comparison_details.csv
*_cycle_metrics.csv
*_selected_cycle_local_states.csv
*_selected_cycle_loops.csv
*.sta
PBS stdout
qstat_<jobid>_finished_full.txt
small _logs/
```

Do not upload heavy Abaqus files:

```text
.odb .stt .res .sim .mdl .prt state.bin large state.csv
```
