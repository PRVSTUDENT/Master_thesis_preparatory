# Stage 16N-R3J Jump Case Status

- PBS job: `1344232.mmaster02`
- Abaqus job: `stage16n_r3j4_jump_500_to_510_to_750`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart checkpoint: `500`
- Slope pair: `250 -> 500`
- Material-state jump: `500 -> 510`
- Continuation target: `750`
- Overwrite trigger: `JSTEP(1)=501, KINC=0, TIME(2)~=500`
- Overwritten variables: `STATEV(1:25)`
- Diagnostic/derived variables not table-overwritten: `STATEV(26:27)`
- Solver status: `completed_successfully`
- Comparison summary: 750,pass,0,0,0,stage16n_r3j4_jump_500_to_510_to_750_comparison_details.csv
- Finished: `2026-06-11 14:03:28`
