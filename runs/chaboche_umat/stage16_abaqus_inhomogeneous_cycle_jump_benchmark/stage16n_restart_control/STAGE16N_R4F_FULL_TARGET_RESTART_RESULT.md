# Stage 16N R4F Full-Target Native Restart Result

Updated: 2026-06-17.

## Job status

Both R4F controls completed with `Exit_status=0`.

| Case | PBS job | Host | Walltime | CPU time | CPU percent | Memory | Solver status |
|---|---:|---|---:|---:|---:|---:|---|
| R4F1 | 1347842 | mnode101 | 03:31:18 | 19:57:42 | 649 | 94371840 kb | source and continuation completed |
| R4F2 | 1347843 | mnode102 | 03:30:05 | 19:05:48 | 635 | 94375936 kb | source and continuation completed |

## Classification

| Case | Restart chain | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error | Controlling primary metric |
|---|---|---:|---|---:|---:|---:|---|
| R4F1 | 250 -> full restart 280 -> solve 281--500 | 500 | fail | 1.1887403% | 11.83033% | 0.92936729% | `HOLE_RING_SDV8_MAX` |
| R4F2 | 500 -> full restart 505 -> solve 506--750 | 750 | review | 0.31896796% | 8.0369449% | 1.5702038% | `HOLE_RING_SDV8_MAX` |

Classification rule:

- `pass`: primary local error <= 5%.
- `review`: primary local error > 5% and <= 10%.
- `fail`: primary local error > 10%.

## Comparison detail

R4F1 at cycle 500:

- `RF1_max` global error is 1.1887403%.
- `HOLE_RING_SDV8_MAX` is 80.6553497314 versus reference 91.477432251, giving 11.83033%.
- `HOLE_RING_SDV11_MAX` is 54.3769416809 versus reference 60.1659240723, giving 9.6216961%.

R4F2 at cycle 750:

- `RF1_max` global error is 0.31896796%.
- `HOLE_RING_SDV8_MAX` is 77.679397583 versus reference 84.4680480957, giving 8.0369449%.
- `HOLE_RING_SDV11_MAX` is 52.5581130981 versus reference 57.0726051331, giving 7.9100858%.

## Interpretation

The R4F result is mixed, so the conclusion should not be reduced to a pure material-only overwrite limitation.

R4F2 improves strongly relative to R4E2/R4J8: the primary local error drops from 13.598377% to 8.0369449%, and the diagnostic S11 error drops from 13.011616% to 1.5702038%. This supports the hypothesis that material-only overwrite is incomplete on the 500 -> 505 -> 750 branch.

R4F1 does not improve relative to R4E1/R4J7: the primary local error remains about 11.83%. Because R4F1 uses a full native target restart at cycle 280 and no overwrite, this points away from the material-only overwrite mechanism as the sole explanation. The next audit should focus on the 250 -> 280 -> 500 branch itself: native restart phase, reference/comparison mapping, selected-cycle local-state extraction, and the identity of the local maximum controlling `HOLE_RING_SDV8_MAX`.

Current decision:

- Do not run R4J9/R4J10 yet.
- Treat material-only overwrite as a contributor, proven most clearly by the R4F2 improvement.
- Treat R4F1 as evidence of an additional restart/comparison/branch-specific issue that must be audited before further extrapolated refinement.

## Lightweight evidence copied into Git

R4F1:

- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/STAGE16N_R4F_CASE_STATUS.md`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_fullrestart_280_solve_281_to_500_comparison_summary.csv`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_fullrestart_280_solve_281_to_500_comparison_details.csv`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_fullrestart_280_solve_281_to_500_cycle_metrics.csv`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_fullrestart_280_solve_281_to_500_selected_cycle_local_states.csv`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_source_250_to_280.sta`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_fullrestart_280_solve_281_to_500.sta`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/stage16n_r4f1_fullrestart_280_solve_281_to_500.o1347842`
- `full_target_restart_cases/R4F1_250_to_280_fullrestart_solve_281_to_500/_logs/`

R4F2:

- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/STAGE16N_R4F_CASE_STATUS.md`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_fullrestart_505_solve_506_to_750_comparison_summary.csv`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_fullrestart_505_solve_506_to_750_comparison_details.csv`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_fullrestart_505_solve_506_to_750_cycle_metrics.csv`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_fullrestart_505_solve_506_to_750_selected_cycle_local_states.csv`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_source_500_to_505.sta`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_fullrestart_505_solve_506_to_750.sta`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/stage16n_r4f2_fullrestart_505_solve_506_to_750.o1347843`
- `full_target_restart_cases/R4F2_500_to_505_fullrestart_solve_506_to_750/_logs/`
