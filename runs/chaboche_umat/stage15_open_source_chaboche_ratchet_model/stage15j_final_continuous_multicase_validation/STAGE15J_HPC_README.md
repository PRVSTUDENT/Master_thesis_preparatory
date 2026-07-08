# Stage 15J HPC README

From this directory on the HPC:

```bash
python3 stage15j_preflight_check.py
bash run_stage15j_smoke_hpc.sh
qsub submit_stage15j_final_multicase.pbs
```

Monitor:

```bash
qstat -u "$USER"
cat STAGE15J_GLOBAL_STATUS.txt
ls -lh case_outputs | head -50
```

Stage 15J writes compact per-case target values, reduced cycle summaries, selected loops, status files, and checkpoints. It also writes final summary, metadata, transferability classification, canonical Stage 15G repeat check, and SVG plots.

Do not commit huge full files until file sizes are checked. Stage 15J is designed not to create full raw histories.

## Memory Safety Note

The first full run attempt, `1332149.mmaster02`, exceeded the 160 GB PBS cgroup memory limit with 40 active workers. A partial driver-state trim improved early memory behavior, but retry `1332165.mmaster02` again reached the cgroup limit after `02:31:46`. The fixed runner keeps 40 active continuous workers and trims every retained `Driver_sd` integration-history list to its latest state after every material increment, preventing per-step arrays from accumulating while preserving the continuous material state. Retries resume from checkpoints with `STAGE15J_RESUME=1`.
