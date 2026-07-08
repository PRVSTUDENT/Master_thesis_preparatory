# Stage 16N-R4Q3 Result

Job: `1362636.mmaster02`

Controller: `R4Q3_continue_from_cycle750_1cpu`

Classification: completed cycle1000 checkpoint solve with successful state extraction; repaired accuracy comparison is classified as `accuracy_validation_fail` under the strict 5% primary-local gate.

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
- Original comparison status: `comparison_error`
- Repaired comparison status: `accuracy_validation_fail`

The Abaqus solve and cycle1000 state extraction completed. The cycle1000 metrics row is present in the R4Q3 output, with `RF1_max=2908.24456024`, `RF1_min=-3074.8221283`, `RF1_mean=534.29378297`, and `loop_area_abs=577.068180846`.

The comparison script failed because `reference_1000_cycle_metrics.csv` does not contain a `cycle=1000` row in the expected `global_cycle_metric` table. The failure is therefore a reference-data coverage/setup blocker for the accuracy comparison, not a failed R4Q3 solve.

## Reference repair and comparison

The original copied reference files came from the incomplete `stage16n_1000cycle_pilot` extraction:

- `reference_1000_cycle_metrics.csv`: cycles 1--593, no cycle1000 row.
- `reference_1000_selected_cycle_local_states.csv`: selected cycles through 500 only.

The valid repair source already existed in the repository:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_parallel_max_reference/`

That reference is documented as a completed 1000-cycle non-jump baseline. Its metric CSV contains cycles 1--1000, and its selected local-state CSV contains cycles 1, 2, 10, 50, 100, 250, 500, 750, and 1000. The repair copied those valid lightweight CSVs into:

- `R4Q3_REFERENCE_REPAIR_reference_1000_cycle_metrics.csv`
- `R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv`

No Abaqus solve was submitted for the repair. The existing comparison script was rerun for cycle1000 and completed successfully.

Repaired comparison summary:

- Classification: `accuracy_validation_fail`
- Global maximum error: `2.330504e-05%`
- Primary-local maximum error: `6.2795526%`
- Diagnostic S11 error: `0.00031922278%`
- Controlling metric: `HOLE_RING_SDV1_MAX`

This is not an Abaqus failure and not a reference-blocked result anymore. It is a strict local-state accuracy miss at cycle1000: global hysteresis and S11 are essentially identical, but the primary-local SDV1 metric exceeds the 5% gate. Because the requested classification set is pass/fail/blocked, the checkpoint is classified as `accuracy_validation_fail`.

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
- `STAGE16N_R4Q3_REFERENCE_REPAIR_RESULT.md`
- `R4Q3_REFERENCE_REPAIR_STATUS.txt`
- `R4Q3_REFERENCE_REPAIR_AVAILABLE_CYCLES.csv`
- `R4Q3_REFERENCE_REPAIR_COMPARE.log`
- `R4Q3_REFERENCE_REPAIR_cycle1000_comparison_summary.csv`
- `R4Q3_REFERENCE_REPAIR_cycle1000_comparison_details.csv`
- `R4Q3_REFERENCE_REPAIR_reference_1000_cycle_metrics.csv`
- `R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv`
- R4Q4--R4Q7 `*_STATUS.txt`, `*_BLOCK_SUMMARY.csv`, `*_CONTROLLER.log`, and finished qstat records.

Heavy Abaqus outputs remain on scratch at:

`/scratch/pr21vyci/stage16n_r4q3_continue_from_cycle750_1cpu/1362636.mmaster02`

Do not queue beyond cycle1000 unless the user explicitly decides to continue as feasibility-only or revises the local-state gate. Under the current strict primary-local gate, R4Q3 is not an accuracy-validation pass.
