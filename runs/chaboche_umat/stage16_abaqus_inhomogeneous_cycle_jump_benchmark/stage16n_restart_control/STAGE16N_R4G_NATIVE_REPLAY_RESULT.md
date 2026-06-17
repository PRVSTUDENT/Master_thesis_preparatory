# Stage 16N R4G Native Restart and Source-Split Replay Result

Updated: 2026-06-17.

## Job status

All six R4G jobs completed with `Exit_status=0`.

| Case | PBS job | Host | Walltime | CPU time | CPU percent | Memory |
|---|---:|---|---:|---:|---:|---:|
| R4G1 direct 250 -> 500 | 1348008 | mnode101 | 03:44:18 | 20:33:11 | 651 | 94371840 kb |
| R4G2 direct 270 -> 500 | 1348010 | mnode100 | 03:29:21 | 18:58:14 | 645 | 94375908 kb |
| R4G3 direct 280 -> 500 | 1348009 | mnode102 | 03:16:19 | 18:04:31 | 644 | 94373888 kb |
| R4G4 split 250 -> 270 -> 500 | 1348012 | mnode102 | 03:34:51 | 19:55:01 | 644 | 94377452 kb |
| R4G5 split 250 -> 280 -> 500 | 1348013 | mnode101 | 03:34:57 | 20:06:26 | 653 | 94373888 kb |
| R4G6 direct 500 -> 750 | 1348011 | mnode101 | 03:45:57 | 20:32:09 | 642 | 94377848 kb |

## Classification

| Case | Mode | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error | Controlling primary metric |
|---|---|---:|---|---:|---:|---:|---|
| R4G1 | direct original restart 250 -> 500 | 500 | pass | 0% | 0% | 0% | none |
| R4G2 | direct original restart 270 -> 500 | 500 | pass | 0% | 0% | 0% | none |
| R4G3 | direct original restart 280 -> 500 | 500 | pass | 0% | 0% | 0% | none |
| R4G4 | source split 250 -> 270 -> 500 | 500 | review | 2.5314199% | 9.3860617% | 1.2392968% | `HOLE_RING_SDV8_MAX` |
| R4G5 | source split 250 -> 280 -> 500 | 500 | fail | 1.1887403% | 11.83033% | 0.92936729% | `HOLE_RING_SDV8_MAX` |
| R4G6 | direct original restart 500 -> 750 | 750 | pass | 0% | 0% | 0% | none |

## Interpretation

The direct original native-restart path is clean. R4G1, R4G2, R4G3, and R4G6 all pass exactly with zero comparison error. This means direct native restarts at cycles 250, 270, 280, and 500 are usable in the retained R1A restart reference and the endpoint comparison mapping is clean for cycles 500 and 750.

The source-split replay path is the problem. R4G4 reproduces a review-level error after a source split to cycle 270, and R4G5 reproduces the R4F1 failure after a source split to cycle 280. R4G5 matches the R4F1 comparison summary exactly: endpoint 500, max global error 1.1887403%, max primary local error 11.83033%, diagnostic S11 error 0.92936729%.

Current decision:

- Do not run R4J9/R4J10 yet.
- Native restart and comparison mapping are not the main issue.
- The failure mechanism is source-split restart generation/selection or source-split phase history, not material-only overwrite alone.
- The next useful audit is to compare direct-original cycle-270/280 restart files against the source-split cycle-270/280 restart files and inspect first continuation step state/field identity.

## Lightweight evidence copied into Git

Each R4G case directory contains:

- `STAGE16N_R4G_CASE_STATUS.md`
- `*_comparison_summary.csv`
- `*_comparison_details.csv`
- `*_cycle_metrics.csv`
- `*_selected_cycle_local_states.csv`
- `*_selected_cycle_loops.csv`
- `*.sta`
- `*.o<jobid>`
- `qstat_<jobid>_finished_full.txt`
- `_logs/*.log`

Heavy Abaqus files were intentionally not copied:

- `.odb`
- `.stt`
- `.res`
- `.sim`
- `.mdl`
- `.prt`
- `state.bin`
- large `state.csv`
