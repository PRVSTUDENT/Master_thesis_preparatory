# Stage 16N Heavy Retention Manifest

Updated: 2026-06-22

Purpose: list the intentionally retained heavy Stage 16N restart/source data after the `/scratch9/pr21vyci` cleanup. These files remain on scratch only while they are provenance-critical for a documented review or gated controller. They must not be copied to Git or `/home`.

## Retention Rule

- Keep only meaningful lightweight evidence in Git/home.
- Use scratch only for active/provenance-critical heavy restart data.
- Delete classified heavy scratch outputs after extraction and upload.
- Before any new solver job, re-check direct `/scratch9/pr21vyci` usage and this manifest.

## Retained Heavy Sources

| ID | Path | Current size | Reason for keeping | Scientific use | Deletion condition |
| --- | --- | ---: | --- | --- | --- |
| R4E2-505-candidate | `/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4E2_500_to_505_exact_solve_506_to_750/stage16n_r4e2_exact_500_to_505_solve_506_to_750_exact_target_source.*` | `.stt` 4.9G; `.res` 1.2M; `.mdl` 13M; `.prt` 2.0K; support `.odb/.dat/.msg/.sta/.sim/.inp` small relative to `.stt` | Candidate existing cycle-505 restart source found by R4K2 preflight. R4K2B later tested it without regenerating a source `.stt`. | R4K2B completed `505 -> 750` from this source, but comparison was `review` with nonzero errors; do not reuse it as a validated 505 continuation source. | Ready for retirement review/deletion after confirming the uploaded R4K2B evidence is sufficient and no separate provenance audit still needs the files. |
| R1A-reference | `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1A_restart_reference_500cycles/` | 1.3T | Canonical long reference restart/output folder retained after `/home` offload cleanup. Many historical restart workflows refer to `stage16n_r1a_restart_ref_500cycles`. | Source/reference for restart reads at cycles 100, 250, and 500; provenance fallback for Stage 16N restart controls. | Delete only after all future workflows reference a smaller validated canonical source or after the user explicitly retires R1A dependency. |
| R1B-reference | `/scratch9/pr21vyci/home_offload/home/pr21vyci/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/R1B_restart_reference_250cycles/` | 276G | Canonical 250-cycle reference restart/output folder retained after `/home` offload cleanup. | Fallback/reference for lower-cycle Stage 16N restart controls. | Delete only after confirming no remaining workflow requires the 250-cycle restart reference, or after replacement by a smaller validated canonical source. |

## Not Automatically Retained

The rest of `/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls` is not automatically retention-approved. It remains present only because the R4E2 candidate lives inside that tree and has not yet been isolated or retired. R4K2B rejected the candidate scientifically, so the next storage review should audit this tree and delete nonessential heavy outputs once the uploaded lightweight evidence is confirmed sufficient.

## Current Scratch State

Last verified after R4K2B cleanup:

- `/scratch9`: 33T total, 7.1T used, 26T free, 22% used.
- `/scratch9/pr21vyci`: about 2.7T.
- R4K2B scratch case: about 3.5M after classification cleanup, with no top-level heavy Abaqus result files.
