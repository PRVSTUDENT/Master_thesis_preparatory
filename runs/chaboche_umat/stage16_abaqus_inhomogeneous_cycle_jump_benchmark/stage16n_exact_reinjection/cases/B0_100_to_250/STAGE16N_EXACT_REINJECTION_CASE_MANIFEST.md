# Stage 16N-B Exact Reinjection Case

- Case: `B0_100_to_250`
- Job: `stage16n_exact_b0_100_to_250`
- Base cycle: `100`
- Compare cycle: `250`
- Continuation cycles: `150`
- Source state CSV: `stage16n_exact_state_cycle0100.csv`
- Source state binary: `stage16n_exact_state_cycle0100.bin`
- Local state CSV used by Fortran: `state.csv`
- Local state binary used by Fortran: `state.bin`
- UMAT with reader hooks: `stage16n_sdvini_sigini_state_reader.for`
- PBS submit script: `submit_stage16n_exact_b0_100_to_250.pbs`
- Nodes: `6642`
- Elements: `3148`
- Hole-ring elements: `60`
- Production policy: `1 MPI rank x 16 OpenMP threads`
