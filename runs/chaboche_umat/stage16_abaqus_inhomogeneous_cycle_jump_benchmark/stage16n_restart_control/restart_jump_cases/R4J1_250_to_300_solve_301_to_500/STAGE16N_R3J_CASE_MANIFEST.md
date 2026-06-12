# Stage 16N-R3J Restart-Preserved Jump Case

- Case: `R4J1_250_to_300_solve_301_to_500`
- Job: `stage16n_r4j1_jump_250_to_300_solve_301_to_500`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart read: `STEP=250, INC=58`
- Native restart checkpoint: `250`
- Slope pair: `100 -> 250`
- Jump formula: `STATEV_jump = STATEV_base + 50 * dSTATEV/dN`
- Material-state jump: `250 -> 300`
- Solved continuation cycles: `301 -> 500`
- Continuation target: `500`
- Overwrite trigger: `JSTEP(1)=251`, `KINC=0`, `TIME(1)=0`, `TIME(2)~=250`
- Overwritten variables: `STATEV(1:25)`
- Not table-overwritten: `STATEV(26:27)`
- Pass criterion: `max_primary_local_error_pct <= 5`
- Review criterion: `5 < max_primary_local_error_pct <= 10`
- Fail criterion: `max_primary_local_error_pct > 10` or solver instability
- Diagnostic-only metric: `HOLE_RING_S11_MAX_ABS`
- Production resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`
