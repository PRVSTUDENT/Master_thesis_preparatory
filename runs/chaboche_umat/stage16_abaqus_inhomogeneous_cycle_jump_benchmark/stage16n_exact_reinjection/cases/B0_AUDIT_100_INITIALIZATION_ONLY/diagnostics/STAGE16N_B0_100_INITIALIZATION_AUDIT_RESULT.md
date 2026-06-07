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
