# Stage 15G Real NEML Long B1 Validation Baseline Plan

Stage 15G runs one real NEML B1 validation lane for an overnight PBS allocation. It is not a prediction-only benchmark.

## Goal

Create a longer B1 reference baseline beyond the Stage 15D limit of 279725 cycles so Stage 15H can validate adaptive cycle-jump predictions at higher cycle counts.

## Case

- Case: `B1_stress_m150_to_250`
- Stress path: `-150 MPa -> 250 MPa`
- Points per cycle: `40`
- Target cycles: `2000000`
- Active real NEML workers: `1`

## Output Strategy

Cycle summaries are compact:

- Write every cycle from 1 to 10000.
- After 10000, write every 100 cycles.
- Always write preserved target cycles.
- Always write checkpoint/final cycles.
- Flush after every written row.

Selected loops store only 40 stress-strain points at selected cycles.

## Preserve Cycles

`1000, 5000, 10000, 15000, 50000, 100000, 106250, 200000, 250000, 279725, 300000, 500000, 750000, 1000000, 1250000, 1500000, 1750000, 2000000`

## Stop And Resume

The run stops cleanly at the 23h35m walltime guard and writes final summary files. Checkpoints are written atomically every 1000 cycles and contain current cycle, driver state arrays, timing, and metadata.

