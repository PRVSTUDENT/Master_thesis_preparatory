# Phase 4 final model comparison notes

## Controlled comparison setup
All three models were compared using the same benchmark geometry, mesh, displacement-controlled 2-cycle loading history, and postprocessing workflow. Therefore, the main difference between results comes from the hardening-law definition rather than from changes in boundary conditions or numerical setup.

## Main observations
- Linear kinematic hardening produced the lowest force level and a stable symmetric loop.
- Multilinear kinematic hardening produced a stronger response than linear kinematic but remained below the tuned combined-hardening model.
- Tuned combined hardening produced the widest and strongest loop among the three models.

## Practical interpretation
- Linear kinematic hardening is the simplest useful cyclic-plasticity warm-up model.
- Multilinear kinematic hardening is a useful intermediate model when piecewise plastic hardening data are available.
- Combined hardening is the most suitable built-in model for the present thesis stage because it gives the richest cyclic response among the tested Abaqus built-in options.

## Numerical ranking by force level
1. Linear kinematic
2. Multilinear kinematic
3. Combined tuned
