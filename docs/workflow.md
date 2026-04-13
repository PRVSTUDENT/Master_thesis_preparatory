# Workflow — Cyclic Jump Techniques in Abaqus

This document describes the end-to-end simulation workflow, from model setup to
the extraction of force-displacement data.

---

## Table of contents

1. [Background](#1-background)
2. [Model setup](#2-model-setup)
3. [Running the analysis](#3-running-the-analysis)
4. [Extracting force-displacement data](#4-extracting-force-displacement-data)
5. [Plotting and interpreting results](#5-plotting-and-interpreting-results)
6. [Tips and troubleshooting](#6-tips-and-troubleshooting)

---

## 1 Background

**Cycle-jumping** (also called *cycle-skipping* or *jump-in-cycles*) is a technique
that accelerates high-cycle fatigue finite-element analyses.  Instead of integrating
every loading cycle, the algorithm:

1. Runs a small "reference" block of cycles to characterise the current damage /
   plastic-strain state.
2. Extrapolates state variables forward over a large number of skipped cycles (the
   *jump size* Δ*N*).
3. Resumes detailed integration at the new state.

This can reduce wall-clock time by one to three orders of magnitude for problems with
millions of cycles, while maintaining acceptable accuracy.

---

## 2 Model setup

### 2.1 Parameters

All model parameters are collected in a JSON file under `models/`.  
Edit `models/<model_name>_parameters.json` before running the build script:

```json
{
  "material": {
    "E":   210000,
    "nu":  0.3,
    "sig_y": 250
  },
  "geometry": {
    "width":  10.0,
    "height": 50.0,
    "depth":   5.0
  },
  "loading": {
    "amplitude":   150.0,
    "R_ratio":      -1.0,
    "n_cycles_ref":  5,
    "jump_size":   500
  },
  "mesh": {
    "global_seed": 1.0
  }
}
```

| Key | Unit | Description |
|-----|------|-------------|
| `E` | MPa | Young's modulus |
| `nu` | — | Poisson's ratio |
| `sig_y` | MPa | Yield stress |
| `amplitude` | MPa or N | Load amplitude |
| `R_ratio` | — | Stress ratio (*σ*_min / *σ*_max) |
| `n_cycles_ref` | — | Reference cycles per jump block |
| `jump_size` | — | Δ*N* — cycles to skip per jump |
| `global_seed` | mm | FE mesh seed size |

### 2.2 Building the input file

```bash
abaqus cae noGUI=scripts/build_model.py
```

The script reads the parameter file and writes `models/<model_name>.inp`.

---

## 3 Running the analysis

### 3.1 Local machine

```bash
abaqus job=<job_name> input=models/<model_name>.inp cpus=4 interactive
```

The `interactive` flag keeps the terminal attached so you see the job status in
real time.  Remove it for background submission.

### 3.2 HPC / cluster (SLURM example)

```bash
sbatch scripts/submit_hpc.sh <job_name> <model_name>.inp
```

Adapt `scripts/submit_hpc.sh` to match your cluster's queue system and module
environment.

### 3.3 Monitoring convergence

While the job is running, tail the Abaqus message file:

```bash
tail -f models/<job_name>.msg
```

Key lines to watch:
* `STEP X INCREMENT Y` — current progress.
* `***WARNING` / `***ERROR` — issues to investigate.
* `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` — normal termination.

---

## 4 Extracting force-displacement data

Once the job has completed, an `*.odb` file is produced next to the input file.

### 4.1 Run the extraction script

```bash
abaqus python scripts/extract_results.py -- \
    --odb   models/<job_name>.odb \
    --set   LOAD_NODE \
    --step  "Step-1" \
    --output results/<job_name>_fd.csv
```

This opens the ODB, queries the reaction force (`RF`) and displacement (`U`) history
outputs at the named node set, and writes them to a CSV file with columns:

```
time, displacement_mm, force_N
```

### 4.2 CSV layout

| Column | Description |
|--------|-------------|
| `time` | Abaqus pseudo-time |
| `displacement_mm` | Nodal displacement in the load direction (mm) |
| `force_N` | Reaction force at the boundary node (N) |

---

## 5 Plotting and interpreting results

```bash
python scripts/plot_results.py \
    --data   results/<job_name>_fd.csv \
    --output results/<job_name>_hysteresis.png
```

The script produces:
* A **force-displacement hysteresis loop** for the last completed jump block.
* A **peak-force vs. cycle** evolution plot showing cyclic softening / hardening.

---

## 6 Tips and troubleshooting

| Symptom | Likely cause | Remedy |
|---------|-------------|--------|
| Job aborts at first increment | Too-large load step or bad BCs | Reduce initial increment size in the `.inp` or parameter file |
| Convergence warnings every increment | Mesh too coarse or material non-linearity | Refine mesh near stress concentrations; tighten Newton–Raphson tolerances |
| Jump introduces oscillations | Jump size Δ*N* too large | Halve `jump_size` and rerun |
| ODB missing history output | Node set name mismatch | Check `--set` argument matches the set defined in the model |
| Extraction script crashes with `KeyError` | Wrong step name | Use `abaqus python -c "from odbAccess import *; odb=openOdb('job.odb'); print(odb.steps.keys())"` to list steps |

---

*Last updated: April 2026*
