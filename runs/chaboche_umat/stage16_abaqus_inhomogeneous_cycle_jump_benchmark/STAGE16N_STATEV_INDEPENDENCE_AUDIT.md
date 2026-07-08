# Stage 16N STATEV Independence Audit

## Source

- UMAT: `runs\chaboche_umat\stage16_abaqus_inhomogeneous_cycle_jump_benchmark\stage16n_neml_equivalent_chaboche_umat.for`
- Purpose: identify which STATEV entries should be modified by a restart-preserved material-state jump.

## UMAT Layout Comment

```text
C State variable layout:
C   STATEV(1)      accumulated plastic strain alpha
C   STATEV(2:7)    backstress 1, Abaqus order 11,22,33,12,13,23
C   STATEV(8:13)   backstress 2, Abaqus order 11,22,33,12,13,23
C   STATEV(14:19)  backstress 3, Abaqus order 11,22,33,12,13,23
C   STATEV(20:25)  plastic strain tensor, Abaqus order 11,22,33,12,13,23
C   STATEV(26)     isotropic hardening R
C   STATEV(27)     last plastic multiplier increment
C ======================================================================
```

## Classification

| STATEV entry | Meaning | Classification | Consequence for Stage 16N-R |
|---:|---|---|---|
| 1 | accumulated plastic strain alpha | independent | History variable used by isotropic hardening and the return mapping. |
| 2:7 | backstress tensor 1 | independent | Nonlinear Chaboche kinematic hardening memory. |
| 8:13 | backstress tensor 2 | independent | Nonlinear Chaboche kinematic hardening memory. |
| 14:19 | backstress tensor 3 | independent | Nonlinear Chaboche kinematic hardening memory. |
| 20:25 | plastic strain tensor | independent | Plastic strain history used to keep strain decomposition consistent. |
| 26 | isotropic hardening R | derived | Recomputed as Q * (1 - exp(-b * alpha)); should not be independently jumped. |
| 27 | last plastic multiplier increment | derived/diagnostic | Increment-local output from the previous Abaqus increment; reset/recompute during continuation. |

## Recommended Jump Set

For the first restart-preserved overwrite/jump prototype, modify only:

- `STATEV(1)` accumulated plastic strain alpha
- `STATEV(2:19)` three Chaboche backstress tensors
- `STATEV(20:25)` plastic strain tensor

Do not independently inject `STATEV(26)` or `STATEV(27)`. `STATEV(26)` is a deterministic function of alpha in the UMAT and should be recomputed after the overwrite. `STATEV(27)` is an increment-local diagnostic/output value and should be reset or recomputed by the next constitutive update.

## Interpretation

The failed SDVINI/SIGINI route injected all available STATEV entries plus stress into a scratch FE model. That route does not preserve displacement, strain, equilibrium, or solver history. The Stage 16N-R repair should therefore keep Abaqus' FE state through native restart and overwrite only independent material memory inside the UMAT.
