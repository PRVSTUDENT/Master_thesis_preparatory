# Stage 16N-R4K2B Result

Updated: 2026-06-22

## Classification

`R4K2B_505candidate_validation_controller` completed as a solver job but failed the scientific validation gate.

- PBS job: `1352353.mmaster02`
- Exit status: `0`
- Stageout status: `1`
- Host: `mnode016`
- Walltime: `05:41:43`
- CPU time: `19:16:27`
- Requested cores: `16`
- Average active cores: about `3.38 / 16`

`Stageout_status=1` is recorded as an infrastructure/stage-out warning, not as the scientific failure mechanism, because lightweight evidence was recovered and committed.

## Scientific Result

R4K2B used the preserved R4E2 cycle-505 source directly:

- no new source `.stt` was generated;
- the scratch case linked the preserved R4E2 source files;
- the continuation read `STEP=505, INC=54`;
- cycles 506--750 were solved;
- the continuation deck did not request continuation restart writes;
- case-local heavy continuation files were cleaned after classification.

Abaqus completed through cycle 750, but the comparison was nonzero:

| Endpoint | Status | Max global error % | Max primary-local error % | Diagnostic S11 error % |
| --- | --- | ---: | ---: | ---: |
| 750 | review | 0.31896796 | 8.0369449 | 1.5702038 |

Therefore the preserved R4E2 cycle-505 candidate is scientifically unsuitable as a validated 505--750 continuation source.

## Consequence

- The 250 branch remains validated and ready for a storage-light true-jump controller after the next storage/resource gate.
- The 505 branch needs audit or redesign before further solver work.
- Do not reuse the R4E2 candidate as a validated 505 source.
- Keep R4J9/R4J10 blocked.

## Evidence

Lightweight evidence is stored in:

`runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/r4k_deck_clone_controllers/R4K2B_505candidate_validation_controller/`

Important files:

- `STAGE16N_R4K2B_CASE_STATUS.md`
- `qstat_1352353_finished_full.txt`
- `stage16n_r4k2b_505candidate_validation_1352353.pbs.out`
- `stage16n_r4k2b_505candidate_validation_505_to_750.sta`
- `stage16n_r4k2b_505candidate_validation_505_to_750_comparison_summary.csv`
- `stage16n_r4k2b_505candidate_validation_505_to_750_comparison_details.csv`
- `stage16n_r4k2b_505candidate_validation_505_to_750_cycle_metrics.csv`
- `stage16n_r4k2b_505candidate_validation_505_to_750_selected_cycle_local_states.csv`
- `stage16n_r4k2b_505candidate_validation_505_to_750_selected_cycle_loops.csv`
- `_logs/stage16n_r4k2b_505candidate_validation_505_to_750*.log`
