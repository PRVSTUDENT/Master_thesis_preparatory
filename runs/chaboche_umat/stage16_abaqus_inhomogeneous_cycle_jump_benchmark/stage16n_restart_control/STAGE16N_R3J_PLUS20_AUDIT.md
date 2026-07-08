# Stage 16N-R3J +20 Audit

Date: 2026-06-12

## Summary

R3J5 and R3J6 passed the restart-preserved UMAT material-state overwrite test, but the audit found that the current continuation decks do not yet skip Abaqus load-cycle steps. They restart at the native checkpoint and solve the ordinary continuation step range while overwriting the material memory at the first continuation increment.

## Results Audited

| Case | Jump | Endpoint | Status | Max global error | Max primary local error | Diagnostic S11 error |
|---|---:|---:|---|---:|---:|---:|
| R3J5 | 250 -> 270 | 500 | pass | 0% | 0% | 0% |
| R3J6 | 500 -> 520 | 750 | pass | 0% | 0% | 0% |

## Audit Checks

| Check | R3J5 | R3J6 | Interpretation |
|---|---|---|---|
| Not self-compared | Pass | Pass | The case metrics and reference metrics are separate files with different SHA-256 hashes. |
| Extrapolated state differs from base | Pass | Pass | The generated state summaries report 25,184 element/IP records and material-state cycles 270 and 520. |
| UMAT overwrite fired | Pass | Pass | Overwrite traces contain 9 diagnostic lines at `KSTEP=251` and `KSTEP=501`. |
| Endpoint cycles correct | Pass | Pass | Comparison endpoints are cycles 500 and 750. |
| Continuation skips solved load cycles | Not yet | Not yet | The decks start at `CYCLE_0251` and `CYCLE_0501`, and the metrics cover cycles 251--500 and 501--750. |

## Key Evidence

- R3J5 comparison summary: `restart_jump_cases/R3J5_250_to_270_to_500/stage16n_r3j5_jump_250_to_270_to_500_comparison_summary.csv`
- R3J6 comparison summary: `restart_jump_cases/R3J6_500_to_520_to_750/stage16n_r3j6_jump_500_to_520_to_750_comparison_summary.csv`
- R3J5 overwrite trace: `restart_jump_cases/R3J5_250_to_270_to_500/_logs/stage16n_r3j5_jump_250_to_270_to_500_overwrite_trace.txt`
- R3J6 overwrite trace: `restart_jump_cases/R3J6_500_to_520_to_750/_logs/stage16n_r3j6_jump_500_to_520_to_750_overwrite_trace.txt`
- R3J5 continuation deck begins with `*STEP, NAME=CYCLE_0251`.
- R3J6 continuation deck begins with `*STEP, NAME=CYCLE_0501`.

## Scientific Interpretation

The +20 result remains valuable: native Abaqus restart plus UMAT-based overwrite is stable for nonzero material-state jumps of +5, +10, and +20 cycles in the inhomogeneous plate-with-hole model.

However, the present R3J decks should be described as restart-preserved material-state overwrite validation, not yet as computational cycle-skipping acceleration. Before claiming acceleration, the next deck generator should either start the continuation after the jumped cycle label, or provide a separate accounting that demonstrates fewer solved load cycles between checkpoint and endpoint.

## Decision

Do not submit R3J7/R3J8 as acceleration evidence in the current deck form. The +50 cases may be useful as a larger material-state perturbation test, but a thesis-safe acceleration test needs a corrected continuation-step strategy first.
