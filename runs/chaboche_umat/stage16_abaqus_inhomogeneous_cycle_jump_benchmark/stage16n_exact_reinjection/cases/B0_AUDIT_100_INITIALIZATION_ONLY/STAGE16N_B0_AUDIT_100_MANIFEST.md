# Stage 16N-B0 Initialization-Only Audit Manifest

- Case: `B0_AUDIT_100_INITIALIZATION_ONLY`
- Job: `stage16n_b0_audit_100_initialization_only`
- Injected state: exact reference cycle 100
- Purpose: determine whether local SDV8 mismatch exists immediately after initialization/equilibration
- Deck: `stage16n_b0_audit_100_initialization_only.inp`
- UMAT/reader: `stage16n_sdvini_sigini_state_reader.for`
- Submit script: `submit_stage16n_b0_audit_100_initialization_only.pbs`
- Nodes: `6642`
- Elements: `3148`
- Hole-ring elements: `60`
- Mail policy: `#PBS -m abe`, `#PBS -M pr21vyci@mailserver.tu-freiberg.de`
