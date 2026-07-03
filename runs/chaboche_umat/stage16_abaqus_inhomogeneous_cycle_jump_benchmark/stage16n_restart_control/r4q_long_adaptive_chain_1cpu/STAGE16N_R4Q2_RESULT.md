# Stage 16N-R4Q2 Result

Job: `1362597.mmaster02`

Controller: `R4Q2_continue_from_cycle500_1cpu`

Classification: completed feasibility block, not accuracy validation and not a new boundary-widening claim.

## PBS accounting

- `job_state=F`
- `Exit_status=0`
- `Stageout_status=1`
- `queue=mediumq`
- `exec_host=mnode075/2*0`
- `resources_used.walltime=09:13:54`
- `resources_used.cput=08:29:02`
- `resources_used.cpupercent=98`
- `resources_used.ncpus=1`
- Request: `select=1:ncpus=1:mpiprocs=1:ompthreads=1:mem=30gb`, `walltime=24:00:00`

`Stageout_status=1` is retained as an infrastructure warning, but the controller copied back the lightweight evidence listed below.

## Result

R4Q2 continued from the existing cycle-500 source produced by R4Q block 1. It did not rerun source250 or block 1.

- Source cycle: 500
- Jump target: 521
- Native continuation: 522--750
- Restart read: `STEP=479`, `INC=65`
- Status: `completed`
- Detail: `extraction=ok; cycle750_state=ok`
- Classification scope: feasibility
- Reference available: no
- Comparison status: not available

The completed block shows that the fixed 21-skipped-cycle rule can execute a second closed-loop block from the preserved cycle-500 restart source and produce a cycle-750 state. Because no matching cycle-750 reference comparison is available in the lightweight evidence, this is a feasibility result only.

## Evidence files

- `R4Q2_CONTINUE_STATUS.txt`
- `R4Q2_CONTINUE_BLOCK_SUMMARY.csv`
- `R4Q2_CONTINUE_CONTROLLER.log`
- `R4Q2_SOURCE500_TARGET521_EXTRAPOLATED_STATE.md`
- `qstat_r4q2_1362597_finished_full.txt`
- `qstat_r4q2_1362597_finished_queue.txt`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_cycle_metrics.csv`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_selected_cycle_local_states.csv`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_selected_cycle_loops.csv`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_sta_tail.txt`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_dat_tail.txt`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_msg_tail.txt`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_datacheck_dat_tail.txt`
- `stage16n_r4q2_block02_500_to_521_solve_522_to_750_datacheck_msg_tail.txt`

Heavy Abaqus outputs remain on scratch at:

`/scratch/pr21vyci/stage16n_r4q2_continue_from_cycle500_1cpu/1362597.mmaster02`

Do not treat this result as permission to widen the true-jump boundary beyond target271. The targeted scientific task remains diagnosing or redesigning the extrapolated-state predictor at target272.
