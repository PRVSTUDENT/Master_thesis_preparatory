# Stage 14 Blockwise Report

Generated: 2026-05-17 06:34:56

## Purpose

Repeated, re-anchored blockwise cycle-jump controller for a 2000-cycle Chaboche UMAT problem.

## Reference Cycle 2000 Values

- Pending reference extraction.

## Strategy Definitions

- `jump25`: 10->500->510; 510->1000->1010; 1010->1500->1510; 1510->1990->2000
- `jump37`: 10->740->750; 750->1480->1490; 1490->1990->2000
- `jump50`: 10->1000->1010; 1010->1990->2000
- `jump65`: 10->1300->1310; 1310->1990->2000

## Block-By-Block Results

| Strategy | Block | Base | Target | Continue | Pre STATEV1 % | Pre S11 % | Final STATEV1 % | Final S11 % | Final RF1 % | Outcome |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

## Final Cycle 2000 Comparison

| Strategy | STATEV1 % | S11 % | RF1 % | Outcome |
|---|---:|---:|---:|---|

## Scientific Interpretation

Later blocks use the previous block's actual recovered route history as the prediction base. This tests a true repeated controller rather than independent idealized jumps from the no-skip reference.
