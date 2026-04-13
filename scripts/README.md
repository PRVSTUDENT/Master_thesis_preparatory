# scripts/

This folder contains all Python scripts used with Abaqus and for standalone
post-processing.

## Naming convention

| Prefix | Purpose |
|--------|---------|
| `build_*` | Build / parametrise an Abaqus model and write an `.inp` file |
| `run_*` | Submit or manage Abaqus jobs (batch helpers) |
| `extract_*` | Open an ODB and extract results to lightweight files (CSV, JSON) |
| `plot_*` | Standalone plotting / visualisation scripts (no Abaqus required) |

## How to run

Scripts that need the Abaqus Python kernel are invoked as:

```bash
# CAE (graphical or headless) — for model building
abaqus cae noGUI=scripts/build_model.py

# Abaqus Python — for ODB post-processing
abaqus python scripts/extract_results.py -- --odb models/job.odb --output results/fd.csv
```

Standalone post-processing scripts (those that only use NumPy / Matplotlib) can be
run with a regular Python interpreter:

```bash
python scripts/plot_results.py --data results/force_disp.csv
```
