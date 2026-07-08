# Stage 16N-R3J Jump Case Status

- PBS job: `1345012.mmaster02`
- Abaqus job: `stage16n_r4j6_jump_500_to_510_solve_511_to_750`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart checkpoint: `500`
- Slope pair: `250 -> 500`
- Material-state jump: `500 -> 510`
- Continuation target: `750`
- Overwrite trigger: `JSTEP(1)=501, KINC=0, TIME(2)~=500`
- Overwritten variables: `STATEV(1:25)`
- Diagnostic/derived variables not table-overwritten: `STATEV(26:27)`
- Solver status: `completed_successfully`
- Comparison summary: 750,review,0.31107055,7.2880782,1.323401,stage16n_r4j6_jump_500_to_510_solve_511_to_750_comparison_details.csv
- Finished: `2026-06-14 12:46:57`
