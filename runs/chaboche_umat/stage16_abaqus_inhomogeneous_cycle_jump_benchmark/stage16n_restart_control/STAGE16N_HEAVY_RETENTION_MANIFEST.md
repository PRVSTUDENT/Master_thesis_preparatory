# Stage 16N Heavy Retention Manifest

Updated: 2026-07-06

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
| R4Q7F-cycle2000-source | `/scratch/pr21vyci/stage16n_r4q7f_continue_from_cycle1750_1cpu/1363633.mmaster02/stage16n_r4q7f_block07_1750_to_1771_solve_1772_to_2000.*` | `.stt` 419G; `.odb` 324M; `.res` 45M; `.mdl` 112M; `.sim` 1.6M; `.sta` 924K; `.prt` 2.0K; cycle1750 and cycle2000 source-state CSV/summary files present | Provenance-critical restart source for the next feasibility-only R4Q8F--R4Q19F chain from cycle2000 to cycle5000. | Enables R4Q8F source2000 -> target2021 and downstream self-gated strict `afterok` continuation. Classification remains `feasibility_only_after_cycle1000_accuracy_fail`; it must not be used to claim validation beyond cycle1000. | Delete only after the R4Q8F--R4Q19F chain has either completed/failed with lightweight evidence copied back, or after the user explicitly retires the cycle5000 feasibility chain. |
| R4Q2-cycle750-diagnostic-source | `/scratch/pr21vyci/stage16n_r4q2_continue_from_cycle500_1cpu/1362597.mmaster02/stage16n_r4q2_block02_500_to_521_solve_522_to_750.*` | `.stt` 420G; `.odb` 324M; `.res` 45M; `.mdl` 112M; `.sim` 1.6M; `.sta` 704K; `.prt` 2.0K | Provenance-critical source for `R4Q3N_exact_native_control_750_to_1000`, the diagnostic native continuation without the 750 -> 771 extrapolated overwrite. | Tests whether the R4Q3 cycle1000 `HOLE_RING_SDV1_MAX` strict local error comes from extrapolated jump state or from local metric/reference sensitivity. | Delete only after R4Q3N completes or is intentionally abandoned and its lightweight comparison evidence is uploaded. |
| R4Q8F--R4Q19F-active-downstream | `/scratch/pr21vyci/stage16n_r4q8f_continue_from_cycle2000_1cpu/` through `/scratch/pr21vyci/stage16n_r4q19f_continue_from_cycle4750_1cpu/` | Pending submission; expected to retain only active predecessor restart source while each dependent job is running/held | Active strict `afterok` feasibility-only chain to cycle5000. Each job must self-gate on predecessor completion, endpoint extraction, heavy restart files, and parsed restart `STEP/INC`. | Technical feasibility continuation after the R4Q3 strict local accuracy fail. | Delete each case-local heavy output after extraction/classification unless it is the immediate active restart source for the next queued job. Do not queue beyond cycle5000 without a new manifest update and user instruction. |

## Not Automatically Retained

The rest of `/scratch9/pr21vyci/stage16n_scratch_runs_r4e_exact_controls` is not automatically retention-approved. It remains present only because the R4E2 candidate lives inside that tree and has not yet been isolated or retired. R4K2B rejected the candidate scientifically, so the next storage review should audit this tree and delete nonessential heavy outputs once the uploaded lightweight evidence is confirmed sufficient.

## Current Scratch State

Last verified before R4Q8F--R4Q19F and R4Q3N submission on 2026-07-06:

- `/scratch9`: 33T total, 11T used, 23T free, 33% used.
- `/scratch`: 101T total, 85T used, 16T free, 85% used.
- `/home`: 17T total, 14T used, 2.8T free, 83% used.
- `/scratch9/pr21vyci`: about 6.2T, above the 5T warning threshold; the required size audit was run before submission.
- Largest `/scratch9/pr21vyci` entries in the audit: `home_offload` 1.6T, `stage16n_scratch_runs_r4e_exact_controls` 1.1T, `stage16n_r4q_long_adaptive_chain_1cpu` 522G, `stage16n_r4q7f_continue_from_cycle1750_1cpu` 514G, `stage16n_r4q2_continue_from_cycle500_1cpu` 514G, `stage16n_r4q4f_continue_from_cycle1000_1cpu` 512G, `stage16n_r4q3_continue_from_cycle750_1cpu` 512G, `stage16n_r4q6f_continue_from_cycle1500_1cpu` 511G, and `stage16n_r4q5f_continue_from_cycle1250_1cpu` 511G.
