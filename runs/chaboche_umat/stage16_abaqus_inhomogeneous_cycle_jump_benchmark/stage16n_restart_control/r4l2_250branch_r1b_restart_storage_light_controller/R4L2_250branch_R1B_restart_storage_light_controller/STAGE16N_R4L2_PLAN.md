# Stage 16N-R4L2 R1B Restart Storage-Light Controller Plan

R4L2 replaces the blocked R1A-based R4L attempt with a direct R1B restart-source controller.

## Gate

- Do not use R1A.
- R4L2-D1 corrected the old assumption: this continuation/datacheck path requires the R1B `.odb`.
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

## R4L2-D1 diagnostic gate

Do not resubmit the production controller until the cheap diagnostic gate has run.

- Runner: `run_stage16n_r4l2_d1_r1b_datacheck_hpc.sh`
- PBS wrapper: `submit_stage16n_r4l2_d1_r1b_datacheck.pbs`
- Resources: 8 cores, 50 GB, 1 h
- Scope: R1B preflight plus target-270 continuation datacheck only
- Continuation solve: disabled in D1 even if datacheck passes
- Evidence: datacheck `.dat/.msg/.log` tails copied as text before heavy cleanup
- Pass meaning: input processing is cleared; production remains blocked until explicitly allowed
- Fail meaning: fix the exact input-processor error from the retained lightweight tails before any production solve

## R4L2-D1 outcome

`1353941.mmaster02` reached the Abaqus input file processor and failed during datacheck before any continuation solve. The exact retained error is that `stage16n_r1b_restart_ref_250cycles.odb` does not exist or is unreadable in the scratch case.

Do not submit the production controller. The next fix must either provide a provenance-valid R1B `.odb` alongside the restart companions or redesign/regenerate the continuation input so Abaqus input processing does not require the source `.odb`.

R4L2-E0 no-solver preflight found no readable exact `stage16n_r1b_restart_ref_250cycles.odb`; only `stage16n_r1b_restart_ref_250cycles_datacheck.odb` exists, and the exact `.odb` is a broken symlink. R4L2-D2 is blocked until the ODB dependency is resolved.
