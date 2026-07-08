# Stage 16N Restart Source Inventory

Date: 2026-06-22

Purpose: inventory retained restart-source material before any further R4L/R4L2 solver submission. No Abaqus solver job was submitted during this inventory.

## Queue And Storage Gate

- Active jobs: none reported by `qstat -u pr21vyci`.
- `/scratch9`: 33T total, 7.1T used, 26T free, 22% used.
- `/scratch`: 101T total, 82T used, 19T free, 82% used.
- `/home`: 17T total, 13T used, 3.4T free, 80% used.
- `/scratch9/pr21vyci`: about 2.7T.

## Candidate Folders Found

The search for `.stt/.res/.mdl/.prt/.odb` under R1A, R1B, R4I-R1, R4I-R5, and R4K1 found only R1A/R1B restart-reference candidates:

- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles`
- `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles`
- `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles`
- `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles`

No complete retained heavy source set was found for R4I-R1, R4I-R5, or R4K1. Those directories currently contain lightweight evidence and controller files, not reusable heavy Abaqus restart source sets.

## Completeness Check

| Candidate | Required restart files | ODB | STA/provenance | Decision |
| --- | --- | --- | --- | --- |
| R1A offload | incomplete: only `.stt` found in the offload folder | missing | missing in offload folder | Not usable alone |
| R1A home view | `.stt`, `.res`, `.prt`, `.sim`, `.sta` accessible; `.mdl` symlink is broken/missing | missing/broken | 500-cycle `.sta` completed successfully | Not complete for Abaqus restart because `.mdl` is missing |
| R1B offload | incomplete: only `.stt` found in the offload folder | missing | missing in offload folder | Not usable alone |
| R1B home view | `.stt`, `.res`, `.mdl`, `.prt`, `.sim`, `.sta` accessible | missing/broken | 250-cycle `.sta` completed successfully | Complete enough for Abaqus restart if the controller does not need ODB extraction |

## R1B Details

R1B is the only viable 250-branch restart candidate found by this inventory. Its resolved files are split between `/home` and `/scratch9`:

- `.stt`: `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles/stage16n_r1b_restart_ref_250cycles.stt`
- `.res`, `.mdl`, `.prt`, `.sim`, `.sta`: `/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles/`

The R1B `.sta` ends with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` at cycle 250. The `.odb` symlink is broken/missing, so any R4L redesign using R1B must avoid ODB-dependent state extraction and use cached validated jump-state files or another lightweight state source.

## Decision

Do not resubmit the existing R4L controller unchanged. R4L failed because it tried to build a source from the incomplete R1A retained source. A possible R4L2 redesign path exists:

1. Use R1B as the restart source for the validated 250 branch.
2. Link `oldjob=stage16n_r1b_restart_ref_250cycles`.
3. Avoid ODB extraction by using retained cached jump-state CSV/BIN for the 270/280 target, or create a new lightweight state source explicitly.
4. Keep continuation restart writing disabled.
5. Copy only lightweight evidence and delete classified heavy outputs.

No new solver job should be submitted until the redesigned controller explicitly validates:

- complete restart source set: yes,
- required Abaqus restart files present: yes,
- source provenance: R1B clean cycle-250 completion,
- ODB dependency removed or replaced: yes.
