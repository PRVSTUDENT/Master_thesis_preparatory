# Stage 16N-R1 Check Result - 2026-06-08

## Queue Status

`qstat -u pr21vyci` returned no active jobs. Both Stage 16N-R1 restart-enabled reference jobs have finished.

## PBS Accounting

| Case | PBS job | Exit status | Walltime | CPU time | CPU percent | Max memory reported |
|---|---|---:|---:|---:|---:|---:|
| R1B restart reference to cycle 250 | `1341177.mmaster02` | 2 | 03:13:22 | 18:58:17 | 655 | 94375776 kb |
| R1A restart reference to cycle 500 | `1341178.mmaster02` | 2 | 08:32:36 | 43:30:54 | 661 | 94375928 kb |

PBS marked both jobs failed because the post-run status-file block in `run_stage16n_r1_restart_reference_hpc.sh` hit a shell syntax error after extraction. The Abaqus solver and extractor both completed successfully before that shell error.

## Abaqus Status

Both `.sta` files end with:

```text
THE ANALYSIS HAS COMPLETED SUCCESSFULLY
```

Both output logs also show the intended parallelism:

```text
1 MPI RANK x 16 THREADS
```

## Restart Files

Native Abaqus restart files now exist.

### R1B, 250 cycles

```text
stage16n_r1b_restart_ref_250cycles.res  29M
stage16n_r1b_restart_ref_250cycles.mdl  50M
stage16n_r1b_restart_ref_250cycles.sim  1.6M
stage16n_r1b_restart_ref_250cycles.stt  226G
stage16n_r1b_restart_ref_250cycles.odb  427M
```

### R1A, 500 cycles

```text
stage16n_r1a_restart_ref_500cycles.res  78M
stage16n_r1a_restart_ref_500cycles.mdl  107M
stage16n_r1a_restart_ref_500cycles.sim  1.6M
stage16n_r1a_restart_ref_500cycles.stt  1.1T
stage16n_r1a_restart_ref_500cycles.odb  783M
```

The `.stt` files are very large. Do not delete them until native restart continuation has been tested, because they may be required by Abaqus restart.

## Lightweight Extraction

Both jobs wrote:

```text
*_cycle_metrics.csv
*_selected_cycle_loops.csv
*_selected_cycle_local_states.csv
```

## Endpoint Metric Check Against Existing 1000-Cycle Reference

The shared global cycle metrics match the existing 1000-cycle reference exactly at the endpoint cycles checked.

### R1B at cycle 250

```text
U1_max error:        0%
U1_min error:        0%
RF1_max error:       0%
RF1_min error:       0%
loop_area_abs error: 0%
max shared global metric error: 0%
```

### R1A at cycle 500

```text
U1_max error:        0%
U1_min error:        0%
RF1_max error:       0%
RF1_min error:       0%
loop_area_abs error: 0%
max shared global metric error: 0%
```

## Conclusion

Stage 16N-R1 achieved its immediate purpose: restart-enabled native Abaqus reference runs to cycles 250 and 500 completed, extracted correctly, match the existing 1000-cycle reference at endpoint global metrics, and produced native restart files.

The next stage should be a native restart continuation control, with no UMAT overwrite:

```text
R1C: restart from cycle 100 -> continue to cycle 250
R1D: restart from cycle 250 -> continue to cycle 500
```

Only after native restart continuation is proven should restart-preserved UMAT memory overwrite be implemented.
