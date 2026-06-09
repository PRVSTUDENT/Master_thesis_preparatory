# Stage 16N-R3 Restart Debug Case: R3D2_500_to_501_debug

- Job: `stage16n_r3d2_restart_debug_500_to_501`
- Source R1 case: `R1A_restart_reference_500cycles`
- Oldjob: `stage16n_r1a_restart_ref_500cycles`
- Restart read: `STEP=500, INC=65`
- Continue cycles: `501` to `501`
- UMAT behavior: debug print only
- STATEV overwrite: none

Debug trace fields:

```text
NOEL, NPT, KSTEP=JSTEP(1), KINC, TIME(1), TIME(2), STATEV(1), STATEV(8), STATEV(11)
```
