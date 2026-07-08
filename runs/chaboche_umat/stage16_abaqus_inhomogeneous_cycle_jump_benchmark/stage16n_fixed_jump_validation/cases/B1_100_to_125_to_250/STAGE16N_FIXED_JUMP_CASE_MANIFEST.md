# Stage 16N-C Fixed State-Initialized Jump Case

- Case: `B1_100_to_125_to_250`
- Job: `stage16n_fixed_b1_100_to_125_to_250`
- Base cycle state: `100`
- Interpreted jump target cycle: `125`
- Compare cycle: `250`
- Skipped cycles: `25`
- Continued cycles in Abaqus deck: `125`
- State strategy: `zero_order_hold_from_base_cycle`
- Source state CSV: `stage16n_exact_state_cycle0100.csv`
- Source state binary: `stage16n_exact_state_cycle0100.bin`
- UMAT with reader hooks: `stage16n_sdvini_sigini_state_reader.for`
- PBS submit script: `submit_stage16n_fixed_b1_100_to_125_to_250.pbs`
- Nodes: `6642`
- Elements: `3148`
- Hole-ring elements: `60`
- Production policy: `1 MPI rank x 16 OpenMP threads`

This case intentionally measures a conservative zero-order fixed jump. It does not claim an exact restart or a high-order state extrapolation.
