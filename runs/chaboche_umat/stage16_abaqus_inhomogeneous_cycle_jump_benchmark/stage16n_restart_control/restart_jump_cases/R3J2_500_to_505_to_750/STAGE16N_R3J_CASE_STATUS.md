# Stage 16N-R3J2 Case Status

- PBS job: `1342924.mmaster02`
- Abaqus job: `stage16n_r3j2_jump_500_to_505_to_750_a4`
- Restart checkpoint: cycle 500
- Material-state jump: 500 -> 505
- Target comparison cycle: 750
- Slope pair used for extrapolation: 250 -> 500

## PBS accounting

- Final PBS state: `F`
- Queue: `teachingq`
- Requested resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`
- Requested walltime: `24:00:00`
- Host/vnode: `mnode102/0*0`, `(mnode102[0]:mem=94371840kb:ncpus=8+mnode102[1]:ncpus=8)`
- Created: Wed Jun 10 16:57:59 2026
- Started: Wed Jun 10 16:58:00 2026
- Finished: Wed Jun 10 21:08:11 2026
- Used walltime: `04:10:06`
- Used CPU time: `22:44:30`
- CPU percent: `646`
- Used memory: `94377920kb`
- Used virtual memory: `5635772kb`
- Used CPUs: `16`
- PBS `Exit_status`: `1`
- PBS `Stageout_status`: `1`

## Result

Abaqus completed successfully; the `.sta` file ends with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`. The nonzero PBS exit status was caused by the wrapper comparison step using a Windows-style reference path during the original job, not by solver failure.

The follow-up comparison was rerun on HPC with Linux reference paths. The result passed exactly:

- `status=pass`
- `max_global_error_pct=0`
- `max_primary_local_error_pct=0`
- `diagnostic_s11_error_pct=0`

## Lightweight evidence files

- `qstat_1342924_full.txt`
- `stage16n_r3j2_jump_500_to_505_to_750_a4.sta`
- `stage16n_r3j2_jump_500_to_505_to_750_a4.o1342924`
- `stage16n_r3j2_jump_500_to_505_to_750_a4_cycle_metrics.csv`
- `stage16n_r3j2_jump_500_to_505_to_750_a4_selected_cycle_loops.csv`
- `stage16n_r3j2_jump_500_to_505_to_750_a4_selected_cycle_local_states.csv`
- `stage16n_r3j2_jump_500_to_505_to_750_a4_comparison_summary.csv`
- `stage16n_r3j2_jump_500_to_505_to_750_a4_comparison_details.csv`
