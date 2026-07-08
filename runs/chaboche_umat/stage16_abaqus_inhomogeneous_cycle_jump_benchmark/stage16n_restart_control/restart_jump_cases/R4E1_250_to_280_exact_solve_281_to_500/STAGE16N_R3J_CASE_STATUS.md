# Stage 16N-R3J Jump Case Status

- PBS job: `1345655.mmaster02`
- Abaqus job: `stage16n_r4e1_exact_250_to_280_solve_281_to_500`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart checkpoint: `250`
- Slope pair: `100 -> 250`
- State mode: `exact_target`
- Material-state jump: `250 -> 280`
- Continuation target: `500`
- Overwrite trigger: `JSTEP(1)=251, KINC=0, TIME(2)~=250`
- Overwritten variables: `STATEV(1:25)`
- Diagnostic/derived variables not table-overwritten: `STATEV(26:27)`
- Solver status: `completed_successfully`
- Comparison summary: 500,fail,1.1886389,11.829104,0.92936729,stage16n_r4e1_exact_250_to_280_solve_281_to_500_comparison_details.csv
- Finished: `2026-06-15 19:50:18`
