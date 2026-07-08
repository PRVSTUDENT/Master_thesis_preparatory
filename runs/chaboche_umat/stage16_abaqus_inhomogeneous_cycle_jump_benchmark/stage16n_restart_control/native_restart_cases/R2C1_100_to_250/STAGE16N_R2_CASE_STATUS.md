# Stage 16N-R2 Native Restart Case Status

- PBS job: `manual_postprocess_followup`
- Abaqus job: `stage16n_r2c1_native_restart_100_to_250`
- Restart interval: `100 -> 250`
- Solver status: `completed_successfully`
- Postprocess status: `completed_successfully`
- Scientific status: `pass`

## Evidence

- Solver `.sta` ends with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`.
- Extraction on HPC wrote:
  - `stage16n_r2c1_native_restart_100_to_250_cycle_metrics.csv`
  - `stage16n_r2c1_native_restart_100_to_250_selected_cycle_loops.csv`
  - `stage16n_r2c1_native_restart_100_to_250_selected_cycle_local_states.csv`
- Comparison against the 1000-cycle reference at cycle 250 wrote `stage16n_native_restart_comparison_summary.csv`.

## Comparison Result

`stage16n_native_restart_comparison_summary.csv` reports `status=pass`, `max_global_error_pct=0`, and `max_primary_local_error_pct=0`.
