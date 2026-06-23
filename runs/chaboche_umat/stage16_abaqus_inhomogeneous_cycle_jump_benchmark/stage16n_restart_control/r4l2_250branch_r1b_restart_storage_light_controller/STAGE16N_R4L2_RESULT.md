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
- The first uploaded controller evidence appeared to avoid the broken/missing R1B `.odb`, but the later D1 datacheck corrected this assumption.
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

The next allowed job is the short R4L2-D1 diagnostic gate, not a production controller:

- `R4L2-D1`: R1B preflight plus target-270 datacheck only.
- Use `submit_stage16n_r4l2_d1_r1b_datacheck.pbs` from the R4L2 case directory.
- Requested resources: 8 cores, 50 GB, 1 h.
- The D1 runner does not run the continuation solve even if datacheck passes.
- If D1 fails, retain and upload the generated datacheck tail files before any further change.

## R4L2-D1 diagnostic result

`1353941.mmaster02` completed the cheap diagnostic gate. It is still not a scientific R4L2 result.

- Queue: `shortq`
- Host: `mnode001`
- Requested resources: 8 cores, 50 GB, 1 h
- Exit status: `0`
- Stageout status: `1`
- Walltime: `00:00:24`
- CPU time: `00:00:12`
- CPU percent: `50`
- Average active cores: about `0.5 / 8`

D1 reached Abaqus, compiled and linked the UMAT, then failed in the Abaqus input file processor during datacheck. The retained `.dat` tail gives the exact blocker:

- `Restart file "stage16n_r1b_restart_ref_250cycles.odb" does not exist or is unreadable.`
- Abaqus then reported no such file under the D1 scratch case for `stage16n_r1b_restart_ref_250cycles.odb`.

The previous assumption that the missing R1B `.odb` was not required is therefore false for this continuation deck/datacheck path. The required R1B restart companions still link, and R1A remains disabled, but R4L2 cannot proceed until the R1B `.odb` dependency is resolved or the continuation input is redesigned so the input processor does not need it.

Local lightweight evidence:

- `R4L2_250branch_R1B_restart_storage_light_controller/STAGE16N_R4L2_D1_DIAGNOSTIC_STATUS.md`
- `R4L2_250branch_R1B_restart_storage_light_controller/stage16n_r4l2_d1_r1b_jump_250_to_270_datacheck_datacheck_dat_tail.txt`
- `R4L2_250branch_R1B_restart_storage_light_controller/_logs/stage16n_r4l2_d1_r1b_jump_250_to_270_datacheck_datacheck.log`
- `R4L2_250branch_R1B_restart_storage_light_controller/qstat_1353941_finished_full.txt`

## R4L2-E0 no-solver preflight

R4L2-E0 searched `/scratch9/pr21vyci` and `/home/pr21vyci/master_thesis/Abaqus_trial` for R1B ODB candidates. No readable exact `stage16n_r1b_restart_ref_250cycles.odb` was found. The only file candidate was `stage16n_r1b_restart_ref_250cycles_datacheck.odb`, and the exact R1B `.odb` path is a broken symlink to the old offload location under `/scratch/pr21vyci/home_offload/20260618_085426/...`.

The corrected status is:

- R1B is restart-companion-complete for `.stt/.res/.mdl/.prt/.sim/.sta`.
- R1B is incomplete for the current R4L2 Abaqus restart/datacheck path because the exact `.odb` is missing or unreadable.
- R4L2-D2 must not be submitted until the ODB dependency is resolved.

Report-safe statement:

The R4L2-D1 diagnostic resolved the previous ambiguity in the R1B restart-source setup. Although the retained R1B source contains the standard restart companion files and completed cycle 250, Abaqus input processing for the R4L2 continuation still requires the corresponding R1B output database, `stage16n_r1b_restart_ref_250cycles.odb`. Since this file is missing or unreadable, R4L2 remains blocked before any valid continuation solve or scientific comparison. Therefore, no conclusion can be drawn yet about the true-jump method from R4L2.
