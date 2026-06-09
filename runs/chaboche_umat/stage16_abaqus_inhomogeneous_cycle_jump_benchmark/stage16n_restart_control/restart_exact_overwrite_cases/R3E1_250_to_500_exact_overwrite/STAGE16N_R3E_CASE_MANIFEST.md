# Stage 16N-R3E Exact Overwrite Case

- Case: `R3E1_250_to_500_exact_overwrite`
- Job: `stage16n_r3e1_exact_overwrite_250_to_500_a2`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart read: `STEP=250, INC=58`
- Continuation: `250 -> 500`
- Overwrite trigger: `JSTEP(1)=251`, `KINC=0`, `TIME(1)=0`, `TIME(2)~=250`
- Exact state source: `stage16n_r1a_restart_ref_500cycles.odb`, cycle `250`
- Overwritten variables: `STATEV(1:25)`
- Not table-overwritten: `STATEV(26:27)`
- Production resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`
