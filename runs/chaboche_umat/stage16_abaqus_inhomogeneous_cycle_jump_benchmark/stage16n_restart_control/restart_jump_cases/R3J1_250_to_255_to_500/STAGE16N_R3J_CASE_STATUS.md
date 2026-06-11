# Stage 16N-R3J1 Case Status

- PBS job: `1342923.mmaster02`
- Abaqus job: `stage16n_r3j1_jump_250_to_255_to_500_a4`
- Restart checkpoint: cycle 250
- Material-state jump: 250 -> 255
- Target comparison cycle: 500
- Slope pair used for extrapolation: 100 -> 250

## PBS accounting

- Final PBS state: `F`
- Queue: `teachingq`
- Requested resources: `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`
- Requested walltime: `24:00:00`
- Host/vnode: `mnode101/0*0`, `(mnode101[0]:mem=94371840kb:ncpus=8+mnode101[1]:ncpus=8)`
- Created: Wed Jun 10 16:57:59 2026
- Started: Wed Jun 10 16:58:01 2026
- Finished: Wed Jun 10 21:05:59 2026
- Used walltime: `04:07:53`
- Used CPU time: `22:42:03`
- CPU percent: `637`
- Used memory: `94375924kb`
- Used virtual memory: `5533876kb`
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

- `qstat_1342923_full.txt`
- `stage16n_r3j1_jump_250_to_255_to_500_a4.sta`
- `stage16n_r3j1_jump_250_to_255_to_500_a4.o1342923`
- `stage16n_r3j1_jump_250_to_255_to_500_a4_cycle_metrics.csv`
- `stage16n_r3j1_jump_250_to_255_to_500_a4_selected_cycle_loops.csv`
- `stage16n_r3j1_jump_250_to_255_to_500_a4_selected_cycle_local_states.csv`
- `stage16n_r3j1_jump_250_to_255_to_500_a4_comparison_summary.csv`
- `stage16n_r3j1_jump_250_to_255_to_500_a4_comparison_details.csv`
