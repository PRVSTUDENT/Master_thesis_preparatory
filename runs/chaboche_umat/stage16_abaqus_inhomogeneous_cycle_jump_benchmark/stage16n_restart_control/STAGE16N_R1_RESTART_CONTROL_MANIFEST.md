# Stage 16N-R1 Restart-Control Manifest

Generated restart-enabled no-jump references for native Abaqus restart testing.

| Case | Job | Target cycle | Restart checkpoints |
|---|---|---:|---|
| `R1B_restart_reference_250cycles` | `stage16n_r1b_restart_ref_250cycles` | 250 | 100, 250 |
| `R1A_restart_reference_500cycles` | `stage16n_r1a_restart_ref_500cycles` | 500 | 100, 250, 500 |

Resource policy for each PBS job:

- `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`
- `walltime=24:00:00`
- Abaqus `cpus=16 mp_mode=threads`

These jobs do not perform UMAT overwrite or manual SDVINI/SIGINI reinjection.
They only create FE-consistent native Abaqus restart sources.
