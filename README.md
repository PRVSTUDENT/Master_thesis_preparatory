# Master Thesis Preparatory — Cyclic Jump Techniques in Abaqus

This repository contains the preparatory simulation work for a master thesis focused on
**cyclic jump (cycle-jumping) techniques** in finite-element fatigue analyses performed
with [Abaqus](https://www.3ds.com/products-services/simulia/products/abaqus/).

Cycle-jumping accelerates high-cycle fatigue simulations by skipping large blocks of
cycles whose response can be extrapolated, instead of integrating every single cycle.
The scripts here set up, run, and post-process such analyses so the approach can be
reproduced and extended.

---

## Repository layout

```
Master_thesis_preparatory/
├── scripts/          # Abaqus Python scripts (model generation & post-processing)
├── models/           # Abaqus input files (.inp) and related model data
├── results/          # Simulation output data (force-displacement CSVs, ODB extracts)
├── docs/             # Extended workflow documentation
├── .gitignore        # Ignores Abaqus temporaries and large binary outputs
└── README.md         # This file
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Abaqus (SIMULIA) | 2021 or later |
| Python (bundled with Abaqus) | 3.x |
| Python (standalone, for post-processing) | 3.8+ |
| NumPy / Matplotlib | latest stable |

---

## Quick start

### 1 — Build and submit a model

```bash
# From the repository root, run the model-generation script inside Abaqus Python:
abaqus cae noGUI=scripts/build_model.py
```

This creates an Abaqus input file (`*.inp`) in the `models/` folder.

### 2 — Run the simulation

```bash
abaqus job=<job_name> input=models/<model_name>.inp cpus=4 interactive
```

### 3 — Extract force-displacement data

```bash
abaqus python scripts/extract_results.py -- --odb models/<job_name>.odb \
                                             --output results/force_disp.csv
```

### 4 — Plot results (standalone Python)

```bash
python scripts/plot_results.py --data results/force_disp.csv
```

---

## Workflow overview

A detailed step-by-step description of the full workflow (model setup → analysis →
post-processing) is available in [`docs/workflow.md`](docs/workflow.md).

---

## Folder conventions

* **`scripts/`** — All executable Python scripts.  
  File names follow `<verb>_<subject>.py` (e.g. `build_model.py`, `extract_results.py`).  
  Scripts intended to run inside Abaqus/CAE are marked with a module-level comment
  `# Run with: abaqus cae noGUI=<script>` or `# Run with: abaqus python <script>`.

* **`models/`** — Abaqus `.inp` files and any supporting keyword files.  
  Large binary `.odb` files should **not** be committed; add them to `.gitignore`.

* **`results/`** — Lightweight extracted data (CSV, JSON, etc.) that can be committed.  
  Raw ODB files and large field-output files stay local / on HPC storage.

* **`docs/`** — Markdown documentation beyond this README.

---

## Contributing / extending

1. Keep scripts self-contained and add a short docstring at the top of every file.
2. Commit only source files and lightweight results; let `.gitignore` handle the rest.
3. Use descriptive commit messages (`Add cycle-jump extrapolation script`, etc.).

---

## License

This repository is part of a master thesis project and is shared for academic
reproducibility. Please contact the author before reusing any content.

