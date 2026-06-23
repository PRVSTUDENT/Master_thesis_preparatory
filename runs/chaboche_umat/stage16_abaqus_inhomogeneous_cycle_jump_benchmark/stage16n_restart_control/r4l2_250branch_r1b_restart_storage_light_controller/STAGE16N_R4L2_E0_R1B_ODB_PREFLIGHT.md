# Stage 16N-R4L2-E0 R1B ODB Preflight

R4L2-E0 was a no-solver recovery/preflight after the R4L2-D1 datacheck result.

## Purpose

Find or prove absence of a valid R1B output database required by the R4L2 continuation/datacheck path.

## Queue and storage gate

- Active jobs: none reported by `qstat -u pr21vyci`.
- `/scratch9`: 33T total, 7.1T used, 26T free, 22% used.
- `/scratch`: 101T total, 82T used, 19T free, 82% used.
- `/home`: 17T total, 13T used, 3.4T free, 80% used.
- `/scratch9/pr21vyci`: about 2.7T.

## Search result

The broad R1B ODB candidate search under `/scratch9/pr21vyci` and `/home/pr21vyci/master_thesis/Abaqus_trial` found only:

```text
24100124 /home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles/stage16n_r1b_restart_ref_250cycles_datacheck.odb
```

No readable exact `stage16n_r1b_restart_ref_250cycles.odb` was found.

The broken-symlink scan found the exact R1B ODB symlink and two downstream links pointing through it:

```text
/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles/stage16n_r1b_restart_ref_250cycles.odb -> /scratch/pr21vyci/home_offload/20260618_085426/home/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles/stage16n_r1b_restart_ref_250cycles.odb
/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/native_restart_cases/R2C1_100_to_250/stage16n_r1b_restart_ref_250cycles.odb -> ../../R1B_restart_reference_250cycles/stage16n_r1b_restart_ref_250cycles.odb
/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_debug_cases/R3D1_250_to_251_debug/stage16n_r1b_restart_ref_250cycles.odb -> ../../R1B_restart_reference_250cycles/stage16n_r1b_restart_ref_250cycles.odb
```

The target of the primary exact ODB symlink is missing or unreadable.

## R1B package status

The retained R1B source folder contains readable standard restart companions:

- `.stt`
- `.res`
- `.mdl`
- `.prt`
- `.sim`
- `.sta`

The `.sta` tail still shows `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` at cycle 250.

However, the exact `stage16n_r1b_restart_ref_250cycles.odb` is not readable. The only found ODB-like candidate is `stage16n_r1b_restart_ref_250cycles_datacheck.odb`, which is not the required exact continuation oldjob ODB and should not be treated as a validated substitute without a separate datacheck proof.

## Classification

R1B is restart-companion-complete for `.stt/.res/.mdl/.prt/.sim/.sta`, but incomplete for the current R4L2 Abaqus restart/datacheck path because `.odb` is missing or unreadable.

R4L2 remains blocked before any valid continuation solve or scientific comparison.

## Next rule

Do not submit R4L2 production. Do not run R4J9/R4J10.

Safe options:

- Option A: regenerate a compact R1B restart-source package through cycle 250, including `.odb`, with strict cleanup and retention rules.
- Option B: redesign the continuation path so Abaqus does not require oldjob `.odb`, then prove that with a short datacheck-only job before production.
- Option C: postpone true-jump testing and document that cleanup removed the required `.odb` for R1B-based continuation.

Given the storage constraints, Option B is only acceptable as a cheap datacheck experiment. If it still asks for `.odb`, use Option A once with strict cleanup and retention rules.
