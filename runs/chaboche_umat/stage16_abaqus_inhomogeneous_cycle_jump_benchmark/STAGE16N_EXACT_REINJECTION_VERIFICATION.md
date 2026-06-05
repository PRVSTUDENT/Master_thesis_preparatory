# Stage 16N-B Exact State Reinjection Verification

## Purpose

Stage 16N-B verifies state transfer before any cycle-jump extrapolation is used. The gate is necessary because later cycle-jump error must be separable from `SDVINI` / `SIGINI` mapping error.

## Production Policy

Use the locked Stage 16N production setting for every exact reinjection case:

```text
PBS request   : select=1:ncpus=16:mpiprocs=1:ompthreads=16
Abaqus launch : cpus=16 mp_mode=threads
Expected msg  : 1 MPI RANK x 16 THREADS
```

## Files

```text
stage16n_extract_exact_state_for_reinjection.py
stage16n_prepare_exact_reinjection_cases.py
stage16n_sdvini_sigini_state_reader.for
run_stage16n_exact_reinjection_hpc.sh
stage16n_compare_exact_reinjection_against_reference.py
STAGE16N_EXACT_REINJECTION_VERIFICATION.md
```

## Verification Cases

```text
B0-1: exact cycle 100 state -> continue normally to cycle 250
B0-2: exact cycle 250 state -> continue normally to cycle 500
B0-3: exact cycle 500 state -> continue normally to cycle 1000
```

These are no-jump tests. They must not extrapolate stress or state variables.

## Workflow

1. Extract exact stress and `SDV1-SDV27` for each element/integration point from the completed 1000-cycle reference ODB.
2. Prepare continuation decks with `*INITIAL CONDITIONS, TYPE=SOLUTION, USER` and `*INITIAL CONDITIONS, TYPE=STRESS, USER`.
3. Generate a case-specific UMAT file where `SIGINI` and `SDVINI` read the extracted state CSV.
4. Run each continuation normally with the 16-CPU production launcher.
5. Compare final global and local metrics against the completed 1000-cycle full reference.

## Commands

From the Stage 16N directory on HPC:

```bash
cd ~/master_thesis/Abaqus_trial/runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark

abaqus python stage16n_extract_exact_state_for_reinjection.py \
  --odb stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles.odb \
  --cycles 100,250,500 \
  --outdir stage16n_exact_reinjection/state

python stage16n_prepare_exact_reinjection_cases.py
```

Then run each prepared case from its case directory using the 16-CPU PBS wrapper or interactively through:

```bash
bash ../../run_stage16n_exact_reinjection_hpc.sh <job-name>
```

For normal HPC submission, use the generated PBS scripts:

```bash
qsub stage16n_exact_reinjection/submits/submit_stage16n_exact_b0_100_to_250.pbs
qsub stage16n_exact_reinjection/submits/submit_stage16n_exact_b0_250_to_500.pbs
qsub stage16n_exact_reinjection/submits/submit_stage16n_exact_b0_500_to_1000.pbs
```

After all runs finish:

```bash
python stage16n_compare_exact_reinjection_against_reference.py
```

## Error Metrics

Compare at the target reference checkpoint:

```text
RF1_max
RF1_min
loop_area_abs
HOLE_RING_MISES_MAX
HOLE_RING_S11_MAX_ABS
HOLE_RING_SDV1_MAX
HOLE_RING_SDV8_MAX
HOLE_RING_SDV11_MAX
```

## Pass Criterion

Expected result: very small error. A first practical gate is:

```text
all monitored quantities <= 1% relative error
```

If exact reinjection does not pass, stop before Stage 16N-C. Fix the element/IP mapping or initialization logic first.
