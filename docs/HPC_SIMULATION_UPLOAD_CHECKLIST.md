# HPC Simulation Upload Checklist for ChatGPT Analysis

Use this checklist after every HPC Abaqus/cycle-jump simulation so ChatGPT can analyze the run without needing `.odb` or other large solver files.

## Recommended upload location

For each run, create one lightweight review folder:

```text
docs/hpc_review_payloads/<stage_or_run_name>/
```

Example:

```text
docs/hpc_review_payloads/stage14c_adaptive_sweep_2000cycles_2026-05-21/
```

Only upload text/CSV/Markdown/log/control files. Do not upload heavy Abaqus generated files.

---

## 1. Always upload these final result files

Upload these whenever they exist:

```text
*_SUMMARY.csv
*_MASTER_SUMMARY.csv
*_CASE_SUMMARY.csv
*_BLOCK_HISTORY.csv
*_REPORT.md
*_DIAGNOSTIC.csv
*_ERRORS.csv
*_PREDICTIONS.csv
```

For the current Stage 14C workflow, the minimum analysis package is:

```text
STAGE14C_SWEEP_REPORT.md
STAGE14C_SWEEP_CASE_SUMMARY.csv
STAGE14C_SWEEP_BLOCK_HISTORY.csv
STAGE14C_SWEEP_MASTER_SUMMARY.csv
STAGE14C_SWEEP_LOCAL_INSTABILITY_DIAGNOSTIC.csv   # if created
```

For Stage 14B, the minimum package was:

```text
STAGE14B_ADAPTIVE_REPORT.md
STAGE14B_ADAPTIVE_SUMMARY.csv
STAGE14B_ADAPTIVE_BLOCK_HISTORY.csv
```

For fixed Stage 14, the minimum package was:

```text
STAGE14_BLOCKWISE_REPORT.md
STAGE14_BLOCKWISE_SUMMARY.csv
```

---

## 2. Always upload the scripts that generated the run

Upload the controller/generator/postprocess/PBS scripts used for that run:

```text
make_*_block_job.py
run_*_controller_hpc.sh
run_*_sweep_controller_hpc.sh
*_update_summary.py
submit_*_hpc.pbs
submit_*_long_hpc.pbs
*_postprocess*.py
```

These are necessary because the numerical result cannot be interpreted safely without knowing:

```text
DeltaN selection rule
recovery window length
STATEV/stress injection mode
prediction order
rollback or stop rules
PBS resources and walltime
Abaqus module/environment settings
```

---

## 3. Upload controller logs, but only lightweight text logs

Upload the main controller log and progress/status file:

```text
_logs/*controller*.log
_logs/*progress_status*.txt
```

Also upload small per-case console logs only if a case failed:

```text
_logs/*generate_console.log
_logs/*datacheck_console.log
_logs/*full_console.log
_logs/*postprocess_console.log
_logs/*summary_console.log
```

If there are many logs, upload only:

```text
main controller log
failed case logs
last 200-500 lines of long logs
```

---

## 4. Upload PBS/job status information

Create one small text file per run, for example:

```text
HPC_JOB_STATUS.txt
```

Include:

```text
Job ID
Queue
Node/host
Exit_status
Start time
Finish time
Walltime used
CPU time used
CPU percent
Memory used
VMem used
Requested CPUs
Requested memory
Requested walltime
```

Example command on HPC:

```bash
qstat -f <JOBID> > HPC_JOB_STATUS.txt
```

or paste/copy the final job accounting output into this file.

---

## 5. Upload reference values used for error calculation

If the summary file does not already include the reference values, upload the small reference CSV used for comparison, for example:

```text
reference_cycle_values.csv
reference_2000cycle_final_values.csv
*_reference_summary.csv
```

For cycle-jump work, make sure the uploaded summaries contain at least:

```text
reference_STATEV1
reference_S11
reference_RIGHT_FACE_RF1_SUM
final_STATEV1
final_S11
final_RIGHT_FACE_RF1_SUM
final error percentages
```

---

## 6. Upload block/case metadata

For blockwise or adaptive simulations, upload metadata files if they are lightweight:

```text
*_metadata.csv
*_case_config.csv
*_case_plan.csv
*_sweep_plan.md
*_block_plan.csv
```

These are especially useful for debugging:

```text
base_cycle
target_cycle
recovery_end_cycle
DeltaN
raw_formula_DeltaN
m_STATEV1
c_STATEV1
estimated local error
prediction order
injection mode
recovery window
rollback status
```

---

## 7. Upload small diagnostic plots if available

Upload `.png` or `.svg` plots only if they are lightweight and directly useful:

```text
*_statev1_error_vs_cycle.png
*_deltaN_vs_block.png
*_m_statev1_vs_block.png
*_curvature_vs_block.png
*_s11_rf1_error_vs_block.png
*_hysteresis_selected_cycles.png
```

Avoid large image dumps. Prefer a few clear summary plots.

---

## 8. Do not upload these heavy Abaqus files

Do not upload or commit these unless explicitly requested:

```text
*.odb
*.sim
*.prt
*.sta
*.msg
*.dat
*.lck
*.com
*.mdl
*.cax
*.023
*.stt
*.env
*.res
*.fil
*.abq
*.pac
*.sel
*.mdl
*.ipm
*.log   # except selected lightweight controller logs
```

Important: `.sta`, `.msg`, and `.dat` are useful for debugging failed Abaqus jobs, but normally keep them out of Git. If needed, upload only a small extracted text file such as:

```text
FAILED_CASE_STA_TAIL.txt
FAILED_CASE_MSG_TAIL.txt
FAILED_CASE_DAT_ERROR_EXTRACT.txt
```

---

## 9. Suggested exact review-folder structure

Use this structure for every completed HPC run:

```text
docs/hpc_review_payloads/<run_name>/
│
├── README.md
├── HPC_JOB_STATUS.txt
├── <STAGE>_REPORT.md
├── <STAGE>_SUMMARY.csv
├── <STAGE>_CASE_SUMMARY.csv
├── <STAGE>_BLOCK_HISTORY.csv
├── <STAGE>_MASTER_SUMMARY.csv
├── <STAGE>_DIAGNOSTIC.csv
│
├── scripts/
│   ├── make_*_block_job.py
│   ├── run_*_controller_hpc.sh
│   ├── *_update_summary.py
│   ├── submit_*_hpc.pbs
│   └── *_postprocess*.py
│
├── logs/
│   ├── main_controller.log
│   ├── progress_status.txt
│   └── failed_case_log_extracts.txt
│
└── figures/
    ├── statev1_error_vs_cycle.png
    ├── deltaN_vs_block.png
    └── selected_hysteresis_loops.png
```

---

## 10. Minimal package if time is short

If you only have time to upload a small package, upload these five items:

```text
1. Final report Markdown: *_REPORT.md
2. Final summary CSV: *_SUMMARY.csv or *_CASE_SUMMARY.csv
3. Block history CSV: *_BLOCK_HISTORY.csv
4. Main controller script: run_*_controller_hpc.sh
5. Block generator script: make_*_block_job.py
```

With these five files, ChatGPT can usually identify:

```text
whether the run was accepted
where the first failure occurred
whether DeltaN selection behaved correctly
whether recovery windows were too short
whether the implementation matches the intended method
```

---

## 11. Git safety command before committing

Before committing a review payload, always run:

```bash
git diff --cached --name-only | egrep '\.(odb|sim|prt|sta|msg|dat|lck|com|mdl|cax|023|stt|env|res|fil|abq|pac|sel|ipm)$' || true
```

If this prints anything, unstage those files before committing.

On PowerShell:

```powershell
git diff --cached --name-only | Select-String '\.(odb|sim|prt|sta|msg|dat|lck|com|mdl|cax|023|stt|env|res|fil|abq|pac|sel|ipm)$'
```

If nothing is printed, the staged files are probably safe.
