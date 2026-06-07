# R1A_restart_reference_500cycles

- Abaqus job: `stage16n_r1a_restart_ref_500cycles`
- Target cycle: `500`
- Restart checkpoints requested in cycle steps: `100, 250, 500`
- Restart keyword: `*RESTART, WRITE, FREQUENCY=1` inside checkpoint cycle steps
- Purpose: generate native Abaqus restart files before any restart-preserved UMAT overwrite.
