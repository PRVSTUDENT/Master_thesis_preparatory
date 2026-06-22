# Stage 16N-R4K2 505 Candidate Note

R4K2 preflight job `1350767.mmaster02` completed without launching Abaqus solve.

The corrected preflight excluded generated-buffer/source-split R4I and R4I-R branches, then found one large existing non-R4I candidate:

`/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source`

Observed files:

- `.stt`: 4.9G
- `.res`: 1.2M
- `.mdl`: 13M
- `.prt`: 2.0K
- `.sta`: completed successfully at cycle 505

Interpretation: this is a candidate existing 505 source from the earlier R4E exact-target control area. It is not yet treated as a validated deck-clone/truncate source. Review its provenance before using it for R4K2 continuation.
