# Stage 16N-R4P Queue Plan

Batch name: `R4P_boundary_reproducibility_and_diagnostics`

Purpose: reproduce and diagnose the 250-branch true-jump boundary now bracketed between target271 and target272. Scientific basis before submission:

- R4M target270 passed.
- R4O target271 passed.
- R4O target272 failed.
- R4O target274 failed.
- Current accepted 250-branch boundary: target271 passes, target272 does not.

Submission policy:

- Submit exactly two dependency chains, A and B.
- Only A1 and B1 are runnable initially; later jobs use `afterany` dependencies.
- At most two R4P jobs should be active at the same time.
- Use `~/bin/qsub_abq_guarded` and a storage gate before submission.
- Do not submit R4J9/R4J10 or any 505-branch job.
- Regenerate the compact complete cycle-250 source package inside each scratch case only.
- Validate `.odb`, `.stt`, `.res`, `.mdl`, `.prt`, `.sim`, and `.sta`.
- Continuation true-jump decks use `*RESTART, READ` only; no continuation `*RESTART, WRITE`.
- Copy back only lightweight evidence: `.md`, `.csv`, `.txt`, `.log`, PBS output, and `.sta/.dat/.msg` tails.
- Delete heavy source and target files after classification.
- Record phase timing, CPU/memory accounting, scratch storage snapshots, predecessor status, and final status files even for skipped or diagnostic-only cases.
- Abort solver escalation if `/scratch9/pr21vyci` exceeds 5T.

## Chain A

| order | PBS wrapper | target | mode | dependency |
| --- | --- | ---: | --- | --- |
| A1 | `submit_stage16n_R4P_A1_repeat_target271.pbs` | 271 | repeat true-jump, 250 -> 271, solve 272 -> 500 | none |
| A2 | `submit_stage16n_R4P_A2_repeat_target272.pbs` | 272 | repeat true-jump, 250 -> 272, solve 273 -> 500 | afterany A1 |
| A3 | `submit_stage16n_R4P_A3_target272_exact_native_control.pbs` | 272 | exact/native source 250 -> 272, native continuation 273 -> 500 | afterany A2 |
| A4 | `submit_stage16n_R4P_A4_target272_failure_diagnostics.pbs` | 272 | target272 diagnostic rerun | afterany A3 |

## Chain B

| order | PBS wrapper | target | mode | dependency |
| --- | --- | ---: | --- | --- |
| B1 | `submit_stage16n_R4P_B1_repeat_target270.pbs` | 270 | repeat true-jump, 250 -> 270, solve 271 -> 500 | none |
| B2 | `submit_stage16n_R4P_B2_target271_diagnostics.pbs` | 271 | target271 diagnostic rerun | afterany B1 |
| B3 | `submit_stage16n_R4P_B3_8core_target271_calibration.pbs` | 271 | 8-core target271 calibration | afterany B2 |
| B4 | `submit_stage16n_R4P_B4_8core_target272_calibration.pbs` | 272 | 8-core target272 calibration | afterany B3 |

## Implementation Notes

- A2 and all later diagnostic/calibration cases record predecessor status but do not self-gate on predecessor pass/fail. The PBS dependency is `afterany`, as requested.
- A3 is the only case that writes a restart in an intermediate native source deck: `stage16n_r4p_target272_exact_native_source_250_to_272.inp` writes the native source restart at cycle272. The final A3 continuation deck still has no continuation restart write.
- The A3 continuation template uses `INC=__R4P_RESTART_INC__`; the runner resolves it from the generated exact-native source `.sta` before the datacheck.

