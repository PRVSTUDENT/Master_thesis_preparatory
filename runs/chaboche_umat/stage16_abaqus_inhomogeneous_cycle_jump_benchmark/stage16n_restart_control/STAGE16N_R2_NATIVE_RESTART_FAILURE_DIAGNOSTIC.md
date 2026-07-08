# Stage 16N-R2 Native Restart Failure Diagnostic

## Summary

Stage 16N-R2 did not fail because Abaqus could not read the restart data or because the solver diverged.

Both corrected jobs reached the end of the analysis successfully inside Abaqus:

- `1341284.mmaster02` / `R2C1` completed `100 -> 250`
- `1341285.mmaster02` / `R2C2` completed `250 -> 500`

The PBS `Exit_status = 1` therefore points to wrapper or postprocessing failure after the Abaqus solve completed, not to a restart syntax, STEP/INC selection, or convergence failure.

## Evidence

### R2C1 (`1341284.mmaster02`)

- PBS history: `Exit_status = 1`
- `resources_used.walltime = 01:55:33`
- `resources_used.cput = 11:15:42`
- `resources_used.cpupercent = 639`
- `resources_used.mem = 94374872kb`
- `resources_used.vmem = 5116372kb`
- `exec_host = mnode100/0*0`
- `.sta` ends with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`
- `.msg` shows restart continuation was read and the final restart information was written at `STEP 250 AFTER INCREMENT 58`
- `.msg` reports `0 ERROR MESSAGES`
- Datacheck output confirms the intended restart start point was found on the restart file:
  - `STEP 100 INCREMENT 53 HAS BEEN FOUND ON THE RESTART FILE`

### R2C2 (`1341285.mmaster02`)

- PBS history: `Exit_status = 1`
- `resources_used.walltime = 03:43:52`
- `resources_used.cput = 20:26:04`
- `resources_used.cpupercent = 643`
- `resources_used.mem = 94375848kb`
- `resources_used.vmem = 8489656kb`
- `exec_host = mnode101/0*0`
- `.sta` ends with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`
- `.msg` shows restart continuation was read and the final restart information was written at `STEP 500 AFTER INCREMENT 65`
- `.msg` reports `0 ERROR MESSAGES`
- Datacheck output confirms the intended restart start point was found on the restart file:
  - `STEP 250 INCREMENT 58 HAS BEEN FOUND ON THE RESTART FILE`

## Failure Classification

Current classification:

1. restart input syntax problem: no
2. wrong STEP/INC checkpoint selection: no
3. missing oldjob files: no for the corrected jobs; the first attempt did fail for this reason, but not the corrected runs
4. datacheck failure: no for the corrected jobs
5. solver convergence failure after restart: no
6. output/extraction/postprocessing failure after Abaqus completed: yes, most likely

## Interpretation

The native restart control gate is still open from a scientific standpoint, but the Abaqus solver itself appears to have executed correctly for both R2 cases.

The most likely explanation for `Exit_status = 1` is a wrapper or postprocessing script failure after solver completion, similar to the earlier R1 exit-status-2 status-script issue.

That means the next repair should focus on the runner/postprocessing path, not on the restart mechanics themselves.

## Next Step

Do not submit additional production restart jobs yet.

Prepare a minimal restart smoke test instead:

- `R2-mini-1`: restart from cycle 100 and continue only to cycle 101
- `R2-mini-2`: restart from cycle 250 and continue only to cycle 251

Use the same 16-CPU threaded setup, but shorten walltime for a quick wrapper-restart check.
