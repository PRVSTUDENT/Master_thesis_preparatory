# Stage 16N Reinjection Limitation and Error Floor

Last updated: 2026-06-06

## Final Stage 16N-B0 conclusion

Stage 16N-B0 should be treated as a practical manual state-initialized continuation study, not as an exact Abaqus restart.

```text
Stage 16N-B0 state-initialized continuation:
Global continuation works.
Binary state transfer works.
Local exact restart is not achieved with SDVINI/SIGINI alone.
```

Use the phrase `state-initialized continuation using SDVINI/SIGINI` from this point onward. Do not describe this route as an exact Abaqus restart. A true exact restart would require Abaqus native restart files and the associated solver continuation state.

## Evidence

The binary state transfer itself is exact:

```text
Binary reader audit: passed
CSV-vs-binary maximum error: 3.5527136788e-15
```

The local mismatch appears after Abaqus receives the manually injected state and performs the initialization/equilibrium step:

```text
SDV8 median relative error: 12.7022%
SDV8 p95 relative error:    150.665%
SDV8 maximum relative error: 479.090%
SDV8 argmax location:       same element/IP, 1242/7
```

The B0-1 continuation from cycle 100 to cycle 250 reproduced the global response well but retained a local SDV8 mismatch:

```text
RF1 max error:        0.259048%
RF1 min error:        0.687538%
Loop area error:      0.967300%
HOLE_RING_SDV8 error: 10.9164%
```

Therefore the error is not caused by extraction, binary writing, binary reading, or a max-location shift. It is introduced by manual state initialization and equilibration.

## Numerical interpretation

The `SDVINI/SIGINI` route initializes:

```text
STATEV
stress
```

It does not reconstruct the full previous finite-element solution state:

```text
nodal displacement field
strain field
internal force equilibrium state
Newton/tangent history
exact loading-path state
```

As a result, strain-like or plastic-strain-like state variables can change immediately when Abaqus equilibrates the model. This creates a reinjection error floor that must be separated from later cycle-jump extrapolation error.

## Revised validation metrics

Primary pass/fail metrics for future fixed and adaptive cycle-jump validation:

```text
RF1 max/min error
loop area error
global hysteresis loop shape
HOLE_RING_SDV1_MAX
HOLE_RING_MISES_MAX
HOLE_RING_S11_MAX_ABS
```

Diagnostic-only metrics:

```text
HOLE_RING_SDV8_MAX
other strain-like STATEV components that change immediately during initialization
```

`HOLE_RING_SDV8_MAX` must still be reported, but it should not be used as a strict exact-restart pass/fail metric because it already shows a large initialization error before any jump extrapolation is applied.

## Consequence for Stage 16N-C

Stage 16N-C should proceed as:

```text
fixed state-initialized cycle-jump validation
```

not:

```text
exact restart cycle-jump validation
```

For every fixed jump, report:

```text
total error = reinjection baseline error + cycle-jump extrapolation error
```

Where possible, compare against the B0 reinjection baseline to estimate the additional jump error. Do not overclaim exact subtraction when signs, locations, or controlling variables differ.

## Current decision

B0-2 and B0-3 exact-reinjection jobs remain on hold. The next useful gate is a conservative fixed state-initialized jump case:

```text
cycle 100 -> cycle 125, continue normally to cycle 250
```

This case uses the same endpoint as B0-1, so the B0-1 state-initialized baseline can be reused when interpreting the fixed-jump error.
