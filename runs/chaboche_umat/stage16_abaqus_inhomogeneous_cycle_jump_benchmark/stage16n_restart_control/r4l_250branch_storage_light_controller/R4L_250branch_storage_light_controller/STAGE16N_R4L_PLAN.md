# Stage 16N-R4L 250-Branch Storage-Light Controller

Prepared: 2026-06-22

Purpose: run first true cycle-jump candidates only on the validated 250 -> 500 branch, using the confirmed deck-clone/truncate restart-source construction and storage-light result retention.

## Controller Sequence

1. R4L1: conservative true-jump candidate around restart target 270.
2. If R4L1 passes, R4L2: nearby confirmation candidate around restart target 280.
3. If R4L1 reviews or fails, stop before R4L2 and write diagnostic summaries.

## Rules

- Use 16 cores, 90 GB, 24 h for scientific continuity.
- Do not run R4J9/R4J10.
- Do not run another 505-source job.
- Do not regenerate a 505 `.stt`.
- Do not write continuation restart output.
- Copy only lightweight evidence back to Git/home.
- Delete R4L case-local heavy Abaqus files after classification.

## Current Scientific Gate

- 250 branch: validated by R4I-R1, R4I-R5, and R4K1 with zero comparison error.
- 505 branch: parked after R4K2B completed but reproduced a review/fail signature.
- Generated source-split/buffer method: retired.
