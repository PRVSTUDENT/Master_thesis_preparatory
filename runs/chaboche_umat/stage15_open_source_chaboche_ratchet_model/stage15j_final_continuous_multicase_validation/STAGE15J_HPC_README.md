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

