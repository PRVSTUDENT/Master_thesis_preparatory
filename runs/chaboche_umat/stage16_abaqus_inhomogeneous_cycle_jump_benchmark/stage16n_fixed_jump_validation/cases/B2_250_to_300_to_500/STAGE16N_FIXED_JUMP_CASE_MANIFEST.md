# Stage 16N-C Fixed State-Initialized Jump Case

- Case: `B2_250_to_300_to_500`
- Job: `stage16n_fixed_b2_250_to_300_to_500`
- Base cycle state: `250`
- Interpreted jump target cycle: `300`
- Compare cycle: `500`
- Skipped cycles: `50`
- Continued cycles in Abaqus deck: `200`
- State strategy: `zero_order_hold_from_base_cycle`
- Source state CSV: `stage16n_exact_state_cycle0250.csv`
- Source state binary: `stage16n_exact_state_cycle0250.bin`
- UMAT with reader hooks: `stage16n_sdvini_sigini_state_reader.for`
- PBS submit script: `submit_stage16n_fixed_b2_250_to_300_to_500.pbs`
- Nodes: `6642`
- Elements: `3148`
- Hole-ring elements: `60`
- Production policy: `1 MPI rank x 16 OpenMP threads`

This case intentionally measures a conservative zero-order fixed jump. It does not claim an exact restart or a high-order state extrapolation.
