# Stage 16N-B0 Cycle-100 Initialization Audit

## Purpose

This audit determines whether the Stage 16N-B0-1 local `SDV8` mismatch already exists immediately after exact state initialization, or whether it develops during the cycle-100 to cycle-250 continuation.

## Audit Case

```text
Case: B0_AUDIT_100_INITIALIZATION_ONLY
Injected state: exact reference cycle 100
Physical continuation: none
Step name: CYCLE_0100
```

The audit uses the same `SIGINI` / `SDVINI` binary state reader as B0-1.

## Files

```text
stage16n_prepare_b0_initialization_audit.py
run_stage16n_b0_initialization_audit_hpc.sh
stage16n_compare_b0_initialization_audit.py
STAGE16N_B0_100_INITIALIZATION_AUDIT.md
```

## Outputs

```text
stage16n_b0_100_binary_reader_audit.csv
stage16n_b0_100_initialization_pointwise_errors.csv
stage16n_b0_100_initialization_argmax_check.csv
stage16n_b0_100_initialization_summary.csv
STAGE16N_B0_100_INITIALIZATION_AUDIT_RESULT.md
```

## Decision Rule

If the binary audit passes but the Abaqus initialization audit already shows the local `SDV8` mismatch at cycle 100, then the issue is in Abaqus initialization/state consistency rather than cycle-100 to cycle-250 continuation.

If initialization is clean but B0-1 continuation is not, then the mismatch develops during continuation, likely due to missing displacement/strain/equilibrium history in manual `SDVINI` / `SIGINI` reinjection.
