# Stage 16N-R3J Jump Case Status

- PBS job: `1344231.mmaster02`
- Abaqus job: `stage16n_r3j3_jump_250_to_260_to_500`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart checkpoint: `250`
- Slope pair: `100 -> 250`
- Material-state jump: `250 -> 260`
- Continuation target: `500`
- Overwrite trigger: `JSTEP(1)=251, KINC=0, TIME(2)~=250`
- Overwritten variables: `STATEV(1:25)`
- Diagnostic/derived variables not table-overwritten: `STATEV(26:27)`
- Solver status: `completed_successfully`
- Comparison summary: 500,pass,0,0,0,stage16n_r3j3_jump_250_to_260_to_500_comparison_details.csv
- Finished: `2026-06-11 14:04:11`
