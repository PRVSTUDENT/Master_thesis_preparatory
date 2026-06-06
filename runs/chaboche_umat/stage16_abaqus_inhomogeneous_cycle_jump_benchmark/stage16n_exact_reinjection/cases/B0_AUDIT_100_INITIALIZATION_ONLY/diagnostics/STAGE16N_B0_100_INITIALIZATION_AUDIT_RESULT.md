# Stage 16N-B0 Cycle-100 Initialization Audit Result

## Purpose

Determine whether the B0-1 local SDV8 mismatch already exists immediately after exact cycle-100 initialization.

## Binary Reader Audit

- Target point: element `1242`, IP `7`
- Maximum CSV-vs-binary absolute error over audited S/SDV values: `3.5527136788e-15`

## Abaqus Initialization Audit

- Reference step: `CYCLE_0100`
- Audit step: `CYCLE_0100`
- Common hole-ring element/IP records: `480`
- SDV8 median relative error: `12.7022400013%`
- SDV8 p95 relative error: `150.665385224%`
- SDV8 max relative error: `479.089668372%`
- Reference SDV8 argmax: element `1242`, IP `7`
- Audit SDV8 argmax: element `1242`, IP `7`
- Same SDV8 argmax location: `true`

## Output Files

- `stage16n_b0_100_binary_reader_audit.csv`
- `stage16n_b0_100_initialization_pointwise_errors.csv`
- `stage16n_b0_100_initialization_argmax_check.csv`
- `stage16n_b0_100_initialization_summary.csv`

## Diagnostic Conclusion

The binary extraction/reader pipeline is correct:

```text
maximum CSV-vs-binary absolute error = 3.55e-15
```

Therefore the B0-1 local mismatch is not caused by the Python binary writer or direct-access binary format.

The Abaqus initialization-only audit already shows a local `SDV8` mismatch before any cycle-100 to cycle-250 physical continuation:

```text
SDV8 median relative error = 12.7022 %
SDV8 p95 relative error    = 150.665 %
SDV8 max relative error    = 479.090 %
SDV8 argmax location       = same element/IP, 1242/7
```

This means the error is introduced during manual `SDVINI` / `SIGINI` initialization plus the tiny equilibrium step, not during the long B0-1 continuation.

Most likely interpretation:

```text
The injected stress and STATEV fields are read correctly, but manual SDVINI/SIGINI does not reconstruct the compatible displacement/strain/equilibrium field from the full reference. Strain-like local STATEV components such as SDV8 are therefore adjusted during the first equilibrium solve.
```

B0-1 remains useful as a practical state-initialized continuation test, but it is not a mathematically exact restart. Do not use it as a clean exact-reinjection proof gate for local STATEV fields without documenting this limitation or adding a true Abaqus restart/displacement-field comparison.
