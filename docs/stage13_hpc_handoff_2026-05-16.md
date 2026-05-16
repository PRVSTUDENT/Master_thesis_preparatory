# Stage 13 HPC Handoff - 2026-05-16

This file is a handoff note for a fresh Codex session. Read this first before touching the Stage 13 5000-cycle Abaqus run.

## Goal

Run the long 5000-cycle Chaboche Abaqus/Standard reference analysis on the TU Freiberg HPC instead of waiting for the local Windows workstation run.

The local Windows run had reached roughly 46.2% after running from 2026-05-15 into 2026-05-16. No `.res` restart file was found in the active local run folder, so the HPC job was submitted as a fresh run, not as a continuation.

## Local Workspace

Workspace root:

```text
D:\TUBAF\Master_Thesis\Abaqus_trial
```

Main local Stage 13 folder:

```text
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles
```

Important local files:

```text
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\chaboche_vp_v1_cyclic_eps005_5000cycles.inp
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\umat_chaboche_v1_with_sdvini_sigini.f
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\extract_5000cycle_reference_history.py
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\monitor_5000cycle_reference.py
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\submit_5000cycle_reference.pbs
```

## SSH Access

The user created and tested this SSH config:

```powershell
ssh -F $env:USERPROFILE\.ssh\codex_config tu_freiberg "hostname && pwd && whoami"
```

Expected result:

```text
mlogin01.cluster
/home/pr21vyci
pr21vyci
```

The config file is:

```text
C:\Users\pruth\.ssh\codex_config
```

The key is:

```text
C:\Users\pruth\.ssh\tu_freiberg_codex
```

## HPC Run Directory

Remote run directory:

```text
~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516
```

Full remote path:

```text
/home/pr21vyci/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516
```

Files uploaded there include the `.inp`, UMAT `.f`, extractor, progress monitor, and PBS script. The user may see only one folder if they run `ls` from `~/master_thesis/Abaqus_trial`; they must `cd stage13_reference_5000cycles_20260516` to see the Abaqus files.

## PBS/Abaqus Setup Found

The cluster uses PBS, not Slurm:

```text
qsub
qstat
qalter
```

General queues such as `longq` are `from_route_only` and cannot be submitted to directly. This user is in the teaching HPC group, so the working route is:

```text
entry_teachingq -> teachingq
```

Useful queue facts found:

```text
teachingq walltime max: 24:00:00
teachingq allowed for user group: t2-dl-rights-hpc_teaching
```

Modules required:

```bash
module load intel/2024.2.0
module load abaqus/2023
```

`module load abaqus/2023` alone was not enough because UMAT compilation failed with:

```text
sh: ifort: Kommando nicht gefunden.
Abaqus Error: Problem during compilation - umat_chaboche_v1_with_sdvini_sigini.f
```

Loading `intel/2024.2.0` provides `ifort` and `ifx`.

## Submitted Job

Current active HPC job:

```text
Job ID: 1324866.mmaster02
Job name: chaboche_5000
Queue: teachingq
Submission route: entry_teachingq
Resources: select=1:ncpus=40:mem=180gb
Walltime: 24:00:00
PBS mail points: ae
PBS mail user: pr21vyci@mailserver.tu-freiberg.de
```

PBS mail notification was added to the running job with:

```bash
qalter -m ae 1324866.mmaster02
```

The reusable PBS script was also updated to include:

```bash
#PBS -m ae
```

## Current Status Snapshot

Snapshot time: 2026-05-16, about 10:24 local HPC time.

At the last check:

```text
Job state: R
Elapsed wall time: about 03:15
Current Abaqus step time: about 1.66e+03 / 5000
Progress: about 33.2%
ODB size: about 1.2 GB
STA size: about 5.4 MB
```

The job was running and producing live Abaqus output files:

```text
chaboche_vp_v1_cyclic_eps005_5000cycles.odb
chaboche_vp_v1_cyclic_eps005_5000cycles.msg
chaboche_vp_v1_cyclic_eps005_5000cycles.sta
chaboche_vp_v1_cyclic_eps005_5000cycles.lck
```

## Monitoring Commands

Check PBS job status:

```powershell
ssh -F $env:USERPROFILE\.ssh\codex_config tu_freiberg "qstat -u pr21vyci"
```

Use the progress-bar monitor:

```powershell
ssh -t -F $env:USERPROFILE\.ssh\codex_config tu_freiberg "cd ~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516 && python3 monitor_5000cycle_reference.py"
```

Raw `.sta` tail:

```powershell
ssh -F $env:USERPROFILE\.ssh\codex_config tu_freiberg "cd ~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516 && tail -f chaboche_vp_v1_cyclic_eps005_5000cycles.sta"
```

Stop monitoring with `Ctrl+C`. This does not stop the Abaqus job.

## If The Job Finishes Successfully

1. Confirm no `.lck` file remains and PBS no longer shows job `1324866.mmaster02`.
2. Check the tail of the `.sta`, `.msg`, and `.dat` files for normal completion.
3. Confirm that `extract_5000cycle_reference_history.py` ran and produced:

```text
chaboche_vp_v1_cyclic_eps005_5000cycles_cycle_history.csv
STAGE13A_5000CYCLE_REFERENCE_SUMMARY.md
```

4. Copy back only the useful final artifacts first. Avoid copying giant transient files unless needed.

Suggested PowerShell copy-back command:

```powershell
scp -F $env:USERPROFILE\.ssh\codex_config "tu_freiberg:~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516/chaboche_vp_v1_cyclic_eps005_5000cycles_cycle_history.csv" "runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\"
scp -F $env:USERPROFILE\.ssh\codex_config "tu_freiberg:~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516/STAGE13A_5000CYCLE_REFERENCE_SUMMARY.md" "runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\"
```

Copy the `.odb` only if postprocessing on Windows requires it. It may be several GB:

```powershell
scp -F $env:USERPROFILE\.ssh\codex_config "tu_freiberg:~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516/chaboche_vp_v1_cyclic_eps005_5000cycles.odb" "runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\"
```

## If The Job Fails Or Hits Walltime

1. Inspect PBS history:

```powershell
ssh -F $env:USERPROFILE\.ssh\codex_config tu_freiberg "qstat -x -f 1324866.mmaster02"
```

2. Inspect remote logs:

```powershell
ssh -F $env:USERPROFILE\.ssh\codex_config tu_freiberg "cd ~/master_thesis/Abaqus_trial/stage13_reference_5000cycles_20260516 && tail -120 chaboche_5000.pbs.log && tail -120 chaboche_vp_v1_cyclic_eps005_5000cycles.msg && tail -80 chaboche_vp_v1_cyclic_eps005_5000cycles.sta"
```

3. If the job was killed by the 24h `teachingq` limit, check whether Abaqus produced restart-capable files. The original local run did not have a `.res` restart file, so do not assume restart is possible without confirming the actual remote files.
4. If a longer walltime is needed, the user likely needs access to a general HPC group/queue such as `entryq -> longq`; direct `longq` submission previously failed with `qsub: Access to queue is denied` or `Unauthorized Request`.

## Files Changed In This Session

Local files intentionally created/edited for the HPC workflow:

```text
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\submit_5000cycle_reference.pbs
runs\chaboche_umat\stage13_percentage_scaling_5000cycles\reference_5000cycles\monitor_5000cycle_reference.py
docs\stage13_hpc_handoff_2026-05-16.md
.agent.md
```

There were many pre-existing untracked/generated Abaqus files in the worktree. Do not clean, delete, or revert them unless the user explicitly asks.
