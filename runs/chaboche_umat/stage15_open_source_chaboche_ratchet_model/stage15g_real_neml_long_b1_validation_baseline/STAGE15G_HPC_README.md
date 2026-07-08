# Stage 15G HPC README

Stage 15G runs one real-NEML B1 long validation baseline.

## Preflight

```bash
cd ~/master_thesis/Abaqus_trial/runs/chaboche_umat/stage15_open_source_chaboche_ratchet_model/stage15g_real_neml_long_b1_validation_baseline
python3 stage15g_preflight_check.py
```

## Smoke Test

```bash
bash run_stage15g_smoke_hpc.sh
```

The smoke test runs only 100 cycles and verifies real NEML, cycle summary, selected loops, checkpoint, status, and finite values.

## Full Run

Only submit after preflight and smoke pass:

```bash
qsub submit_stage15g_long_b1.pbs
```

## Monitor

```bash
cat case_outputs/B1_long_status.txt
tail -n 5 case_outputs/B1_long_cycle_summary.csv
```

## Notes

- Active real-NEML workers: 1
- PBS CPUs requested: 30
- Walltime: 23:55:00
- Stop guard: 23:35:00
- Full raw material-point histories are not stored.

