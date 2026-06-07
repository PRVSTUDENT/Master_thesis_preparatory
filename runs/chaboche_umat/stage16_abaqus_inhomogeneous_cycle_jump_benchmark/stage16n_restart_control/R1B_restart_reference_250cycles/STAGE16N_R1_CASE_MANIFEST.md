# R1B_restart_reference_250cycles

- Abaqus job: `stage16n_r1b_restart_ref_250cycles`
- Target cycle: `250`
- Restart checkpoints requested in cycle steps: `100, 250`
- Restart keyword: `*RESTART, WRITE, FREQUENCY=1` inside checkpoint cycle steps
- Purpose: generate native Abaqus restart files before any restart-preserved UMAT overwrite.
