# Stage 16N-R4Q Result

Job: `1362114.mmaster02`

Checked: 2026-07-02 Europe/Berlin

## PBS result

- PBS state: `F`
- Exit status: `0`
- Stageout status: `1`
- Queue: `mediumq`
- Host: `mnode028/0`
- Requested resources: `1:ncpus=1:mpiprocs=1:ompthreads=1:mem=30gb`, walltime `24:00:00`
- Used walltime: `20:52:02`
- Used CPU time: `19:27:30`
- CPU percent: `99`
- Peak recorded memory: `31457284kb`

`Stageout_status=1` is retained as an infrastructure warning, not as the scientific classification, because the controller copied the lightweight status, block summary, logs, and extracted evidence back to the repository tree.

## Scientific classification

R4Q is a partial feasibility result for the validated 21-cycle rule, not a completed long-chain validation to cycle 1000/2000/5000.

Block 1 completed:

- Source cycle: `250`
- Extrapolated target: `271`
- Native continuation: `272 -> 500`
- Status: `completed`
- Classification scope: `feasibility`
- Reference available: `no`
- Comparison status: `not_available`
- Detail: `extraction=ok`

The first block therefore confirms that the already accepted 250-branch rule can be executed as a closed-loop controller step and can produce a new cycle-500 source state for the next block.

Block 2 stopped before solving:

- Source cycle: `500`
- Extrapolated target: `521`
- Intended native continuation: `522 -> 750`
- Status: `datacheck_failure`
- Comparison status: `not_run`
- Detail: `datacheck failed`

The controller log shows the setup cause before Abaqus datacheck:

```text
stage16n_make_r4q_restart_deck.py: error: argument --old-inc: invalid int value: ''
Abaqus Error: The following file(s) could not be located: stage16n_r4q_block02_500_to_521_solve_522_to_750.inp
```

This is a controller/deck-generation stop caused by an empty restart increment for the new cycle-500 source, not a scientific rejection of the `500 -> 521 -> 750` adaptive jump.

## Evidence paths

- `R4Q_LONG_CHAIN_STATUS.txt`
- `R4Q_LONG_CHAIN_BLOCK_SUMMARY.csv`
- `R4Q_LONG_CHAIN_CONTROLLER.log`
- `qstat_r4q_1362114_finished_full.txt`
- `R4Q_SOURCE250_TARGET271_EXTRAPOLATED_STATE.md`
- `R4Q_SOURCE500_TARGET521_EXTRAPOLATED_STATE.md`
- `_source_state/stage16n_exact_state_cycle0500_summary.md`
- `stage16n_r4q_block01_250_to_271_solve_272_to_500_cycle_metrics.csv`
- `stage16n_r4q_block01_250_to_271_solve_272_to_500_selected_cycle_local_states.csv`
- `stage16n_r4q_block01_250_to_271_solve_272_to_500_selected_cycle_loops.csv`
- `_logs/stage16n_r4q_block02_500_to_521_solve_522_to_750_datacheck.log`

## Next step

Do not submit another R4Q production job until the block-2 restart provenance is reviewed and the deck-generation logic reliably resolves the `old_inc` from the cycle-500 source state or `.sta` evidence. A cheap no-solver/controller preflight should confirm the generated block-2 `.inp` before any new Abaqus solve is launched.
