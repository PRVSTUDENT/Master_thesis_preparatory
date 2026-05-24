# Stage 15E Test And Submission Log

## Local Checks

- Python preflight passed on local Windows Python.
- Reduced local smoke matrix produced 72 rows with all statuses `ok`.
- Full local matrix produced 4788 variable-level rows and 798 acceptance rows.

## HPC Preflight

The direct cluster command initially used `/usr/bin/python3` Python 3.6.8 without NumPy. The Stage 15E preflight and controller now self-reexec through the HPC Python module when needed.

Final HPC preflight passed with:

- Python 3.11.7
- NumPy 2.4.4
- pandas 3.0.2
- Stage 15D B1 target coverage verified to 250000 cycles
- Stage 15D B2 target coverage verified to 180000 cycles

## HPC Smoke Test

The HPC smoke test passed:

- Case: B1
- Base cycles: 10 and 50
- Target cycles: 100, 500, 1000
- Methods: `linear_last_2`, `least_squares_last_20`
- Rows produced: 72
- No NaN or inf
- Required SVG plots generated

## PBS Submission

Submitted:

```text
qsub submit_stage15e_cycle_jump.pbs
1330335.mmaster02
```

Final historical resource usage:

```text
job_state = F
resources_used.walltime = 00:00:16
resources_used.cput = 00:00:12
resources_used.mem = 316732kb
resources_used.vmem = 409796kb
```

## Result Summary

Stage 15E completed cleanly and produced:

- `STAGE15E_CYCLE_JUMP_MATRIX.csv`
- `STAGE15E_CYCLE_JUMP_ERRORS.csv`
- `STAGE15E_ACCEPTANCE_TABLE.csv`
- `STAGE15E_BEST_METHODS_BY_TARGET.csv`
- `STAGE15E_MASTER_SUMMARY.md`
- seven SVG plots

