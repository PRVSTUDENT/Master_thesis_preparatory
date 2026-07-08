# Stage 16N-R4H Case Status

- PBS job: `1349086.mmaster02`
- Case: `R4H2_source_250_to_281_restart_280_to_500`
- Mode: `interior_source_split`
- Purpose: `source solve 250--281, restart from interior cycle 280, then solve 281--500`
- Base oldjob: `stage16n_r1a_restart_ref_500cycles`
- Continuation oldjob: `stage16n_r4h2_source_250_to_281_restart_280_to_500_source_250_to_281`
- Restart read: `STEP=280, INC=56`
- First solved cycle: `281`
- Final cycle: `500`
- UMAT overwrite: `none`
- Continuation solver status: `completed_successfully`
- Comparison summary: 500,fail,1.1887403,11.83033,0.92936729,stage16n_r4h2_source_250_to_281_restart_280_to_500_comparison_details.csv
- Finished: `2026-06-17 20:30:17`
