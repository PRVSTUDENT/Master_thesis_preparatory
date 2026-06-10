# Stage 16N-R3J Restart-Preserved Jump Case

- Case: `R3J2_500_to_505_to_750`
- Job: `stage16n_r3j2_jump_500_to_505_to_750_a4`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart read: `STEP=500, INC=65`
- Native restart checkpoint: `500`
- Slope pair: `250 -> 500`
- Jump formula: `STATEV_jump = STATEV_base + 5 * dSTATEV/dN`
- Material-state jump: `500 -> 505`
- Continuation target: `750`
- Overwrite trigger: `JSTEP(1)=501`, `KINC=0`, `TIME(1)=0`, `TIME(2)~=500`
- Overwritten variables: `STATEV(1:25)`
- Not table-overwritten: `STATEV(26:27)`
- Pass criterion: `max_primary_local_error_pct <= 5`
- Review criterion: `5 < max_primary_local_error_pct <= 10`
- Fail criterion: `max_primary_local_error_pct > 10` or solver instability
- Diagnostic-only metric: `HOLE_RING_S11_MAX_ABS`
- Production resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`
