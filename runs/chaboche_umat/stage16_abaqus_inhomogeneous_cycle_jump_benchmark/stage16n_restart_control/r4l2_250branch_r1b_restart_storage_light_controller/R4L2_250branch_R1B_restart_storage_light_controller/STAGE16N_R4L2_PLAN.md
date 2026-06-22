# Stage 16N-R4L2 R1B Restart Storage-Light Controller Plan

R4L2 replaces the blocked R1A-based R4L attempt with a direct R1B restart-source controller.

## Gate

- Do not use R1A.
- Do not require the broken/missing R1B `.odb`.
- Require readable R1B `.stt`, `.res`, `.mdl`, `.prt`, `.sim`, and `.sta`.
- Require the R1B `.sta` to show successful completion through cycle 250.
- Keep R4J9/R4J10 blocked.
- Keep the 505 branch parked after the R4K2B review result.

## Controller

- Oldjob: `stage16n_r1b_restart_ref_250cycles`
- Restart read: cycle 250, increment read from the R1B `.sta`
- R4L2-1: cached true-jump target 270, solve 271 -> 500
- R4L2-2: cached true-jump target 280, solve 281 -> 500 only if R4L2-1 passes
- Continuation restart writing: disabled
- Source ODB extraction: disabled
- Heavy copy-back: disabled
- Heavy cleanup after each classified case: enabled

If a required cached jump state is missing, the controller writes a `blocked_missing_cached_jump_state` status and stops before Abaqus.
