# Stage 16N-R4Q3 Result

Job: `1362636.mmaster02`

Controller: `R4Q3_continue_from_cycle750_1cpu`

Classification: completed cycle1000 checkpoint solve with successful state extraction; accuracy comparison is blocked by reference-table coverage, not by Abaqus solve failure.

## PBS accounting

- `job_state=F`
- `Exit_status=0`
- `Stageout_status=1`
- `queue=mediumq`
- `exec_host=mfatnode003/8`
- `resources_used.walltime=11:41:46`
- `resources_used.cput=10:46:26`
- `resources_used.cpupercent=99`
- `resources_used.ncpus=1`
- Request: `select=1:ncpus=1:mpiprocs=1:ompthreads=1:mem=30gb`, `walltime=24:00:00`

`Stageout_status=1` is retained as an infrastructure warning, but the controller copied back the lightweight status, summary, qstat, extraction, compact tail, and log evidence.

## Result

R4Q3 continued from the existing cycle-750 source produced by R4Q2.

- Source cycle: 750
- Jump target: 771
- Native continuation: 772--1000
- Restart read: `STEP=708`, `INC=62`
- Status: `completed`
- Detail: `extraction=ok; cycle1000_state=ok`
- Classification scope requested by the controller: accuracy validation
- Reference available flag: yes
- Comparison status: `comparison_error`

The Abaqus solve and cycle1000 state extraction completed. The cycle1000 metrics row is present in the R4Q3 output, with `RF1_max=2908.24456024`, `RF1_min=-3074.8221283`, `RF1_mean=534.29378297`, and `loop_area_abs=577.068180846`.

The comparison script failed because `reference_1000_cycle_metrics.csv` does not contain a `cycle=1000` row in the expected `global_cycle_metric` table. The failure is therefore a reference-data coverage/setup blocker for the accuracy comparison, not a failed R4Q3 solve.

## Dependent queue outcome

The dependent queue released after R4Q3, but R4Q4--R4Q7 self-gated and stopped without Abaqus solves:

- R4Q4 `1362637.mmaster02`: `previous_not_completed`, source1000 -> target1021 / solve 1022--1250 skipped.
- R4Q5 `1362638.mmaster02`: `previous_not_completed`, source1250 -> target1271 / solve 1272--1500 skipped.
- R4Q6 `1362639.mmaster02`: `previous_not_completed`, source1500 -> target1521 / solve 1522--1750 skipped.
- R4Q7 `1362640.mmaster02`: `previous_not_completed`, source1750 -> target1771 / solve 1772--2000 skipped.

This is the intended safe-stop behavior: the long chain halted at the cycle1000 review gate instead of running further blocks from an unvalidated checkpoint.

## Evidence files

- `R4Q3_CONTINUE_STATUS.txt`
- `R4Q3_CONTINUE_BLOCK_SUMMARY.csv`
- `R4Q3_CONTINUE_CONTROLLER.log`
- `qstat_r4q_1362636_finished_full.txt`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_cycle_metrics.csv`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_selected_cycle_local_states.csv`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_selected_cycle_loops.csv`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_sta_tail.txt`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_dat_tail.txt`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_msg_tail.txt`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_datacheck_dat_tail.txt`
- `stage16n_r4q3_block03_750_to_771_solve_772_to_1000_datacheck_msg_tail.txt`
- `_source_state/stage16n_exact_state_cycle1000_summary.md`
- `_logs/stage16n_r4q3_block03_750_to_771_solve_772_to_1000_compare_1000.log`
- R4Q4--R4Q7 `*_STATUS.txt`, `*_BLOCK_SUMMARY.csv`, `*_CONTROLLER.log`, and finished qstat records.

Heavy Abaqus outputs remain on scratch at:

`/scratch/pr21vyci/stage16n_r4q3_continue_from_cycle750_1cpu/1362636.mmaster02`

Do not queue beyond cycle1000 until the reference-data coverage problem is reviewed and the cycle1000 comparison is classified.
