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

The first full run attempt, `1332149.mmaster02`, exceeded the 160 GB PBS cgroup memory limit with 40 active workers. The fixed runner keeps 40 active continuous workers but trims each `Driver_sd` object to its latest state after every material increment, preventing retained per-step arrays from accumulating. The retry resumes from checkpoints with `STAGE15J_RESUME=1`.
