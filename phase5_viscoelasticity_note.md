# Phase 5 note: Why viscoelasticity is not suitable for true metallic cyclic plasticity

## Main point
Viscoelasticity can produce time-dependent hysteresis, relaxation, and delayed recovery, but it is not the correct constitutive route for representing true metallic cyclic plasticity. In metals subjected to cyclic inelastic loading, the key mechanisms are plastic yielding, irreversible strain accumulation, and evolution of internal variables such as hardening or backstress terms. These are not naturally described by a purely viscoelastic formulation.

## Why viscoelasticity is not enough
A viscoelastic model is fundamentally intended to describe recoverable time-dependent material response. Even when it produces hysteresis in a stress-strain curve, that hysteresis is associated with delayed elastic response and energy dissipation, not with true plastic flow governed by a yield condition. For metallic cyclic plasticity, the important questions are different: when yielding starts, how reverse loading changes the response, whether hardening or softening develops over cycles, and whether ratcheting or progressive permanent strain occurs.

## Missing features for metallic cyclic plasticity
Viscoelasticity does not properly represent:
- permanent plastic deformation after unloading
- yield surface evolution
- backstress-driven Bauschinger effect
- cyclic hardening and softening in the plasticity sense
- ratcheting as progressive plastic strain accumulation under non-zero mean loading

## Why this matters for the present study
The present Abaqus benchmark work is focused on cyclic response in metallic materials. Therefore, the appropriate built-in comparison space is formed by plasticity-based hardening models such as linear kinematic, multilinear kinematic, and combined hardening. These models directly target cyclic plastic mechanisms, whereas viscoelasticity would describe a different material class and could lead to misleading interpretation if used as a substitute.

## Practical conclusion
Viscoelasticity may be useful as a conceptual contrast or as a model class for polymers and other time-dependent solids, but it is not an appropriate replacement for true metallic cyclic plasticity. For the current thesis direction, viscoelasticity should therefore remain only a short explanatory note, not a main modeling route.
