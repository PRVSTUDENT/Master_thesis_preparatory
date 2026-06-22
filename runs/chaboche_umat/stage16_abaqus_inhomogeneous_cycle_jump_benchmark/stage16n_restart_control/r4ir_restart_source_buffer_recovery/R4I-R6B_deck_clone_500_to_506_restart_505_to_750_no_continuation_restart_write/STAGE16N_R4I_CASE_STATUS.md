# Stage 16N-R4I Case Status

- PBS job: `1350763.mmaster02`
- Job: `stage16n_r4ir6b_deck_clone_500_to_506_restart_505_to_750_no_continuation_restart_write`
- Source job: `stage16n_r4ir6b_deck_clone_500_to_506_restart_505_to_750_no_continuation_restart_write_source_500_to_506`
- Source style: `deck_clone`
- Purpose: `R4I-R6B recovery: deck-clone source 500--506, restart interior 505, continue 506--750 with no continuation restart-write requests`
- Continuation restart-write setting: continuation deck contains `*RESTART, READ` only and no `*RESTART, WRITE` card.
- Classification: `source_restart_write_infrastructure_failure_no_scientific_comparison`
- Failure evidence: the source solve failed before reaching the continuation solve, with `WriteAll: Input/output error` while writing the source `.stt` file on scratch.
- Last observed source progress: source `.sta` reached `CYCLE_0503` before `THE ANALYSIS HAS NOT BEEN COMPLETED`.
- PBS accounting: `Exit_status=1`, `Stageout_status=1`, walltime `00:05:21`, cput `00:11:04`, average active cores about `2.07/16` (12.9%).
- Scratch footprint at inspection: failed scratch run directory was about `2.6G`, including a partial `2.23G` source `.stt`.
- Finished: `2026-06-22 05:50:35`
