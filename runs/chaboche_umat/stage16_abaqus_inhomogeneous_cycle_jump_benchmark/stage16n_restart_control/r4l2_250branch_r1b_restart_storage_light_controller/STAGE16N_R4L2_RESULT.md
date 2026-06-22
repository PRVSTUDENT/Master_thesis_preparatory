# Stage 16N-R4L2 Result

R4L2 has not produced a scientific true-jump result yet.

## Submitted job

- Controller: `stage16n_r4l2_250branch_r1b_restart_storage_light_controller`
- PBS job: `1353909.mmaster02`
- Queue reported by PBS: `mediumq`
- Host: `mnode069`
- Exit status: `0`
- Stageout status: `1`
- Walltime: `00:01:17`
- CPU time: `00:00:17`
- CPU percent: `41`
- Average active cores: about `0.22 / 16`

## Classification

`1353909.mmaster02` is an infrastructure/controller setup failure, not a scientific R4L2 result.

The useful gate evidence is positive:

- R1B was used as `oldjob=stage16n_r1b_restart_ref_250cycles`.
- R1A was not used.
- The controller did not require the broken/missing R1B `.odb`.
- Required R1B companions `.stt/.res/.mdl/.prt/.sim/.sta` were linked.
- The R1B `.sta` showed successful completion through cycle 250, with restart row `STEP=250, INC=58`.
- Cached target-270 jump state was found from `restart_jump_cases/R4J3_250_to_270_solve_271_to_500`.

The blocking evidence is:

- R4L2-1 datacheck failed in the Abaqus input file processor before a valid continuation solve.
- The follow-on solve also failed in the Abaqus input file processor.
- No valid comparison CSV was produced.
- R4L2-2 was not run.

Because the first controller version continued after the failed datacheck and then cleaned the heavy `.dat` files, the exact Abaqus input-processor error message was not retained in this job's lightweight evidence. The runner has been patched after this attempt so a future diagnostic attempt stops immediately on datacheck/solve failure and saves small `.dat` tail text files before heavy cleanup.

## Storage result

Heavy continuation outputs were not copied to Git/home. The scratch case was cleaned of case-local heavy Abaqus files after classification.

## Next rule

Do not treat R4L2 as scientifically failed. It is still blocked at setup/input-processing. Do not run R4L2-2 or any broad true-jump batch until the R4L2-1 input-processor failure is diagnosed from retained `.dat` tail evidence.
