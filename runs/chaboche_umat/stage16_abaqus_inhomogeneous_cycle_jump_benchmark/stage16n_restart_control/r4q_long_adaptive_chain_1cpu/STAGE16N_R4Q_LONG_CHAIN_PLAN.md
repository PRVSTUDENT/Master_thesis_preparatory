# Stage 16N-R4Q Long Adaptive Chain 1-CPU Plan

## Purpose

R4Q is a one-job, sequential, storage-light Abaqus restart-chain test for repeated adaptive cycle jumps.

This is not a direct 250 -> 1000/2000/5000 jump. It repeatedly applies the tested safe adaptive jump size:

```text
source S -> jump target S+21 -> native continuation target+1 to S+250
```

The intended checkpoint order is:

```text
1000 first
2000 second
5000 only if walltime remains
```

## Scientific classification

If reference/no-jump results exist at a completed block end, R4Q may compare against them. Otherwise the result must be classified as restart-chain feasibility, not full accuracy validation.

Current lightweight reference evidence is known for the 1000-cycle reference. The controller therefore stages 1000-cycle reference CSVs when present and marks later checkpoints as feasibility-only unless matching reference CSVs are added.

## Controller settings

- Controller: `R4Q_long_adaptive_chain_1cpu`
- Source cycle start: `250`
- Safe jump: `21`
- Block size: `250`
- Checkpoints: `1000`, `2000`, `5000`
- Queue: `entryq`
- Resources: `select=1:ncpus=1:mpiprocs=1:ompthreads=1:mem=30gb`
- Walltime: `24:00:00`
- Abaqus CPUs: `1`
- Working directory: `/scratch/$USER/stage16n_r4q_long_adaptive_chain_1cpu/${PBS_JOBID}`
- PBS stdout: `/scratch/pr21vyci/stage16n_r4q_long_adaptive_chain_1cpu/r4q_long_chain.pbs.out`

## Storage rules

- Run Abaqus only in scratch.
- Copy back only lightweight evidence.
- Keep only the newest block-end restart package needed for the next block.
- Delete older heavy restart packages and case-local heavy outputs after evidence extraction.
- Stop cleanly before walltime exhaustion and copy the latest lightweight status.

## Required status files

- `R4Q_LONG_CHAIN_STATUS.txt`
- `R4Q_LONG_CHAIN_BLOCK_SUMMARY.csv`
- `R4Q_LONG_CHAIN_CONTROLLER.log`
