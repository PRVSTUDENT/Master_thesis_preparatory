# Stage 13P Partial 4380-Cycle Reference Salvage Note

## Context

The Stage 13 5000-cycle no-skip reference was submitted to the TU Freiberg HPC teaching queue. The job reached the queue walltime limit before completing the full 5000 cycles.

No Abaqus `.res` restart file was available, so the job was not continued as a restart analysis.

## Salvaged Partial Reference

The partial ODB was postprocessed through cycle 4380.

## Extracted Data

- Extracted rows: 4380
- First cycle: 1
- Last cycle: 4380
- Cycle 4380 frame time: 4379.99023438

## Cycle 4380 Values

- STATEV1: 25.3516654968
- S11: 221.764282227 MPa
- RIGHT_FACE_RF1_SUM: 887.057128906

## Interpretation

This is a partial reference only. It should not be used as the final 5000-cycle reference for Stage 13 percentage-scaling comparisons. It can be used only for partial-history diagnostics or for designing shorter follow-up studies.

The complete Stage 13 5000-cycle reference remains unresolved unless rerun with sufficient walltime or restart capability.
