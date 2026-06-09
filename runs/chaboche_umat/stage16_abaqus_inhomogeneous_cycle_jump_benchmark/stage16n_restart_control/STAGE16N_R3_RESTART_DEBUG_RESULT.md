# Stage 16N-R3 Restart Debug Result

## Objective

Use native Abaqus restart to preserve the finite-element state, then inspect UMAT restart-call metadata before implementing any STATEV overwrite.

## Result

Stage 16N-R3D restart-debug smoke tests passed.

| Case | PBS job | Restart | Target | Solver status | Debug status | Trace lines |
|---|---|---:|---:|---|---|---:|
| `R3D1_250_to_251_debug` | `1341601.mmaster02` | 250 | 251 | `completed_successfully` | `pass` | 64 |
| `R3D2_500_to_501_debug` | `1341602.mmaster02` | 500 | 501 | `completed_successfully` | `pass` | 68 |

Both jobs used the intended native restart path, the debug UMAT compiled and ran, and both Abaqus `.sta` files ended with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`.

## UMAT Restart Mapping

The first debug calls after native restart have:

```text
R3D1 restart 250 -> 251:
KSTEP = JSTEP(1) = 251
KINC  = 0
TIME(1) = 0
TIME(2) = 250.000000000019
```

```text
R3D2 restart 500 -> 501:
KSTEP = JSTEP(1) = 501
KINC  = 0
TIME(1) = 0
TIME(2) = 499.999999999974
```

Therefore the first safe overwrite trigger for a restart-preserved jump should be tied to:

```text
JSTEP(1) == target continuation step
KINC == 0
TIME(1) == 0
TIME(2) ~= checkpoint cycle
```

Use a tolerance for `TIME(2)` because Abaqus reports the restart cycle time with floating-point roundoff.

## Trace Examples

R3D1:

```text
STAGE16N_R3_DEBUG_TRACE NOEL=9 NPT=1 KSTEP=251
KINC=0 TIME1=0 TIME2=250.000000000019
STATEV1=3.00541041517388 STATEV8=-10.9356681430370 STATEV11=-9.676468148235075E-002
```

R3D2:

```text
STAGE16N_R3_DEBUG_TRACE NOEL=41 NPT=1 KSTEP=501
KINC=0 TIME1=0 TIME2=499.999999999974
STATEV1=5.39159405775104 STATEV8=-12.5609518413434 STATEV11=-0.337057524560302
```

## Interpretation

Native restart exposes the restarted material state to UMAT at `KINC=0` before the first continuation increment. This gives a practical hook for Stage 16N-R3 exact no-op overwrite and later small jump overwrite while preserving Abaqus' displacement, strain, equilibrium, and solver restart state.

## Next Step

Proceed to Stage 16N-R3E exact no-op overwrite:

```text
R3E1: restart 250 -> 500, overwrite independent STATEV with exact cycle-250 values at KINC=0
R3E2: restart 500 -> 750 or 1000, overwrite independent STATEV with exact cycle-500 values at KINC=0
```

Final overwrite logic should modify only independent material memory:

```text
STATEV(1)
STATEV(2:19)
STATEV(20:25)
```

Do not independently overwrite `STATEV(26)` or `STATEV(27)` in the thesis method; `STATEV(26)` is derived from `STATEV(1)`, and `STATEV(27)` is increment-local diagnostic state.
