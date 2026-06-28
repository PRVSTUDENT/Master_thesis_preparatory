# Stage 16N-R4O Boundary Refinement Queue Plan

## Purpose

R4O refines the current 250-branch true-jump bracket:

- R4M target270 passed at cycle 500.
- R4N target275 reviewed at cycle 500.

The goal is to locate the practical boundary between target270 and target275 while keeping the Stage 16N active-use policy at no more than two 16-core Abaqus jobs at once.

## Queue Shape

Six jobs are submitted as two PBS dependency chains. PBS ordering limits the chain progression, and each dependent job also self-gates by reading the previous job's copied-back comparison summary.

| Chain | Case | Target | Continuation | PBS dependency | Scientific gate |
| --- | --- | ---: | --- | --- | --- |
| A | `R4O_A1_target271` | 271 | 272 -> 500 | none | run |
| A | `R4O_A2_target272` | 272 | 273 -> 500 | `afterany:A1` | run only if A1 passed |
| A | `R4O_A3_target273` | 273 | 274 -> 500 | `afterany:A2` | run only if A2 passed |
| B | `R4O_B1_target274` | 274 | 275 -> 500 | none | run |
| B | `R4O_B2_repeat275` | 275 | 276 -> 500 | `afterany:B1` | run only if B1 passed |
| B | `R4O_B3_target276_guarded` | 276 | 277 -> 500 | `afterany:B2` | run only if B2 passed |

## Required Rules

- Submit through `/home/pr21vyci/bin/qsub_abq_guarded`.
- Request `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`.
- Regenerate the complete cycle-250 source package in scratch for each executed job.
- Validate `.odb/.stt/.res/.mdl/.prt/.sim/.sta` before continuation.
- Use continuation `*RESTART, READ` only; no continuation `*RESTART, WRITE`.
- Copy back only lightweight evidence.
- Delete classified heavy scratch files after extraction/comparison.
- Abort before solve if `/scratch9/pr21vyci` exceeds 5 TB.
- Do not submit R4J9/R4J10 or any 505-branch job.

## Interpretation

- If A1 reviews, the boundary is between 270 and 271.
- If A1/A2 pass but A3 reviews, the boundary is between 272 and 273.
- If A1/A2/A3 pass and B1 reviews, the boundary is between 273 and 274.
- If B1 passes and B2 reviews again, the boundary is between 274 and 275.
- If B2 passes on repeat, target275 is not stable/reproducible and needs audit before higher targets.
- B3 should only execute if the target275 repeat unexpectedly passes.
