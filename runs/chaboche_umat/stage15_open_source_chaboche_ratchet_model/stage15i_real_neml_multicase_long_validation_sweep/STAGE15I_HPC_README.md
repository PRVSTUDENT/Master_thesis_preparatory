# Stage 15I HPC README

From this directory on the HPC:

```bash
python3 stage15i_preflight_check.py
bash run_stage15i_smoke_hpc.sh
qsub submit_stage15i_multicase_long_sweep.pbs
```

Monitor the job:

```bash
qstat -u "$USER"
cat STAGE15I_GLOBAL_STATUS.txt
ls -lh case_outputs | head -40
```

Stage 15I writes one compact cycle summary, selected-loop CSV, status file, and checkpoint file per case. It also writes `STAGE15I_MASTER_SUMMARY.md`, `STAGE15I_RUN_METADATA.json`, `STAGE15I_CASE_COMPLETION_SUMMARY.csv`, `STAGE15I_TARGET_CYCLE_VALUES.csv`, and `STAGE15I_GLOBAL_STATUS.txt`.

Do not commit full per-case cycle summary files until sizes are checked. The reduced target-cycle summary and selected loops are the preferred GitHub artifacts.
