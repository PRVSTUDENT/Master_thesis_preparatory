# Stage 16N-R4I Case Status

- PBS job: `1350743.mmaster02`
- Job: `stage16n_r4ir6_deck_clone_500_to_506_restart_505_to_750`
- Source job: `stage16n_r4ir6_deck_clone_500_to_506_restart_505_to_750_source_500_to_506`
- Source style: `deck_clone`
- Purpose: `R4I-R6 deck-clone confirmation: clone/truncate the clean direct replay deck shape, solve 500--506, restart interior 505, continue 506--750`
- Restart read: `STEP=505, INC=58`
- First solved cycle: `506`
- Intended final cycle: `750`
- Classification: `infrastructure_failure_no_scientific_comparison`
- Failure evidence: continuation Abaqus solve failed with `WriteAll: Input/output error` while writing the continuation `.stt` file on scratch; the status file ended at cycle 731 and reports `THE ANALYSIS HAS NOT BEEN COMPLETED`.
- PBS accounting: `Exit_status=1`, `Stageout_status=0`, walltime `05:36:52`, cput `23:30:31`, average active cores about `4.19/16` (26.2%).
- Finished: `2026-06-22 00:01:21`
