# Stage 16N-R4K1 Result

Checked: 2026-06-22 12:57 CEST

## Job

- PBS job: `1350764.mmaster02`
- PBS name: `stage16n_r4k_250branch_controller`
- Host: `mnode013`
- Requested resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`
- Final state: `job_state=F`, `Exit_status=0`, `Stageout_status=1`
- Walltime: `06:01:15`
- CPU time: `20:39:54`
- Average active cores: approximately `3.43 / 16`
- Peak PBS memory: `94371840kb`

## Scientific Result

R4K1 passed the 250-branch deck-clone exact-control gate.

The controller solved a deck-clone source branch from cycle 250 to 281, restarted from the interior cycle-280 record, continued through cycle 500, extracted the endpoint metrics, and compared against the 1000-cycle reference. Abaqus completed successfully and the comparison at cycle 500 was exact:

| Cycle | Status | Max global error | Max primary-local error | Diagnostic S11 error |
| --- | --- | ---: | ---: | ---: |
| 500 | pass | 0 | 0 | 0 |

## Interpretation

This confirms that the deck-clone/truncate strategy is not merely a restart-270 repair. Together with R4I-R1 and R4I-R5, the 250 branch now has exact deck-clone evidence for restart targets 270 and 280. Generated buffered source decks remain rejected for this workflow, but the 505--750 branch is still scientifically unclassified because R4I-R6/R4I-R6B failed during scratch `.stt` writing before a valid comparison.

R4J9/R4J10 should remain blocked until the remaining 505-branch provenance/control question is resolved. No new solver job should be submitted until the `/scratch9/pr21vyci` storage footprint is cleaned or explicitly reviewed.

## Uploaded Evidence

The lightweight R4K1 evidence is stored in:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4k_deck_clone_controllers/R4K1_250branch_controller/`

Key files:

- `STAGE16N_R4K_CASE_STATUS.md`
- `qstat_1350764_finished_full.txt`
- `stage16n_r4k_250branch_controller_1350764.pbs.out`
- `stage16n_r4k1_deck_clone_exact_250_to_280_to_500_comparison_summary.csv`
- `stage16n_r4k1_deck_clone_exact_250_to_280_to_500_comparison_details.csv`
- `stage16n_r4k1_deck_clone_exact_250_to_280_to_500_cycle_metrics.csv`
- `stage16n_r4k1_deck_clone_exact_250_to_280_to_500_selected_cycle_local_states.csv`
- `stage16n_r4k1_deck_clone_exact_250_to_280_to_500_selected_cycle_loops.csv`
- `stage16n_r4k1_deck_clone_exact_250_to_280_to_500.sta`
- `_logs/stage16n_r4k1_deck_clone_exact_250_to_280_to_500_compare.log`

