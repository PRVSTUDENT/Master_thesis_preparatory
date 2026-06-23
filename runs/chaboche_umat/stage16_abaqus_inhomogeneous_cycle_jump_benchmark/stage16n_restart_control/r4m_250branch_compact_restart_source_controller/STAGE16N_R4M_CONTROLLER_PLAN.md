# Stage 16N-R4M 250-Branch Compact Restart-Source Controller Plan

R4M is the next safe storage-light path after R4L2-D1/E0 proved that the retained R1B source is incomplete for the current Abaqus restart/datacheck path.

## Corrected status

- 250 branch: methodologically validated by R4I-R1, R4I-R5, and R4K1.
- R4L/R4L2: no scientific true-jump result yet; blocked by incomplete restart-source packages, not by true-jump failure.
- R1A: not usable because restart companions are missing or broken.
- R1B: `.stt/.res/.mdl/.prt/.sim/.sta` are available, but the required exact `.odb` is missing.
- `stage16n_r1b_restart_ref_250cycles_datacheck.odb`: do not use; it is only a datacheck ODB, not a valid solved restart-source ODB.
- 505 branch: parked / not validated.
- R4J9/R4J10: blocked.

## Purpose

Rebuild one compact, complete cycle-250 restart-source package with:

- `stage16n_r1b_restart_ref_250cycles.odb`
- `stage16n_r1b_restart_ref_250cycles.stt`
- `stage16n_r1b_restart_ref_250cycles.res`
- `stage16n_r1b_restart_ref_250cycles.mdl`
- `stage16n_r1b_restart_ref_250cycles.prt`
- `stage16n_r1b_restart_ref_250cycles.sim`
- `stage16n_r1b_restart_ref_250cycles.sta`

Then use that package immediately for the first 250-branch true-jump candidate. Do not retain large heavy files after classification unless the source package is explicitly recorded in the heavy retention manifest with size and deletion condition.

## Preflight gate

Before submission:

- `qstat -u pr21vyci` must report no active jobs.
- `/scratch9/pr21vyci` should remain near the post-cleanup baseline, about 2.7T unless explicitly explained.
- `/scratch`, `/scratch9`, and `/home` storage gates must pass.
- R4J9/R4J10 must remain blocked.
- R4L/R4L2 must not be resubmitted with old retained R1A/R1B source packages.
- The datacheck ODB must not be linked or used as a substitute solved source ODB.

## Controller sequence

Task 1: Generate compact source through cycle 250.

- Use one scratch-only case directory.
- Use the exact Abaqus basename `stage16n_r1b_restart_ref_250cycles`.
- Generate the solved source package, not just datacheck files.
- Keep source heavy files in scratch only.

Task 2: Validate complete source package.

Require all exact files listed in the Purpose section. The `.sta` must show successful completion through cycle 250 and provide the restart row used by the continuation input.

Task 3: Datacheck target-270 continuation.

- `oldjob=stage16n_r1b_restart_ref_250cycles`
- no continuation restart writes
- stop immediately if datacheck fails
- copy `.dat/.msg/.log` tails and status

Task 4: If datacheck passes, run target-270 continuation.

- solve 271 -> 500
- extract comparison immediately
- copy only lightweight evidence
- delete heavy continuation files after classification

Task 5: Conditional follow-up.

- If target 270 passes and walltime remains, run one nearby confirmation target, preferably 280 or 275.
- If target 270 reviews or fails, run diagnostics only and do not run a second true-jump.

## Resources

Recommended practical first gate:

- one job only
- `entryq`
- 8 cores
- 50 GB
- 12-24 h

Use 16 cores / 90 GB / 24 h only if strict comparability with previous Stage 16N exact controls is more important than allocation efficiency. Recent accounting suggests 16-core jobs often averaged only about 3-4 active cores.

## Storage rules

Hard requirements:

- no heavy copy-back to `/home`
- no retained heavy continuation outputs after classification
- keep only lightweight evidence: `.md`, `.csv`, `.txt`, `.sta` tail, `.dat` tail, `.msg` tail, `.log`, qstat report
- delete `.odb/.stt/.res/.sim/.mdl/.prt/.dat/.msg` from case scratch after extraction and classification
- if the regenerated source package must be retained, record it in `STAGE16N_HEAVY_RETENTION_MANIFEST.md` with size and deletion condition

## Do not do

- Do not resubmit old R4L.
- Do not resubmit R4L2 with the incomplete R1B source.
- Do not use `stage16n_r1b_restart_ref_250cycles_datacheck.odb` as a solved source ODB.
- Do not run R4J9/R4J10.
- Do not chase the 505 branch now.

## Report-safe wording

The R4L2-D1/E0 diagnostics showed that the retained R1B source is incomplete for the current Abaqus restart path. Although the restart companion files `.stt`, `.res`, `.mdl`, `.prt`, `.sim`, and `.sta` are available, Abaqus input processing also requires the exact solved output database `stage16n_r1b_restart_ref_250cycles.odb`. Only a datacheck ODB was found, and the exact solved ODB is a broken symlink. Therefore, R4L2 remains blocked before any valid continuation solve or scientific comparison. The next storage-light path is to regenerate one compact, complete cycle-250 restart source package and use it immediately within a self-contained controller, followed by lightweight evidence extraction and heavy-file cleanup.
