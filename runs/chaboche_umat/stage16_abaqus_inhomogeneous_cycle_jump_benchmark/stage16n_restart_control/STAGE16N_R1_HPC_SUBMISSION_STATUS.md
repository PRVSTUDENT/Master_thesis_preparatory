# Stage 16N-R1 HPC Submission Status

Last updated: 2026-06-07 17:52 Europe/Berlin.

## Purpose

Stage 16N-R1 creates native Abaqus restart-enabled no-jump reference runs before any restart-preserved UMAT memory overwrite is attempted. This stage does not use `SDVINI`/`SIGINI` scratch reinjection and does not implement cycle jumping yet.

## Generated Jobs

| Case | PBS job | Abaqus job | Target | Restart checkpoints | Status |
|---|---|---|---:|---|---|
| R1B | `1341177.mmaster02` | `stage16n_r1b_restart_ref_250cycles` | 250 cycles | 100, 250 | running at submission check |
| R1A | `1341178.mmaster02` | `stage16n_r1a_restart_ref_500cycles` | 500 cycles | 100, 250, 500 | running at submission check |

Both jobs use:

```text
select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
walltime=24:00:00
Abaqus cpus=16 mp_mode=threads
```

## Submission Notes

The first attempted submissions, `1341175.mmaster02` and `1341176.mmaster02`, failed before Abaqus started because the generated per-case shell runner had Windows CRLF line endings. PBS history showed both used only one second of walltime and exited with status 2. The generated runner was fixed to write LF line endings explicitly, the remote scripts were normalized with `perl -pi -e 's/\r$//'`, and the corrected jobs were resubmitted as `1341177.mmaster02` and `1341178.mmaster02`.

## PBS Snapshot for Corrected Jobs

At the first `qstat -f` check:

```text
1341177.mmaster02
job_state = R
queue = teachingq
Resource_List.select = 1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
Resource_List.walltime = 24:00:00
Resource_List.mem = 90gb
Resource_List.ncpus = 16
Resource_List.mpiprocs = 1
resources_used.ncpus = 16
resources_used.walltime = 00:00:00
resources_used.cput = 00:00:00
resources_used.mem = 0b
resources_used.vmem = 0kb
ctime = Sun Jun  7 17:52:40 2026
stime = Sun Jun  7 17:52:41 2026
exec_vnode = (mnode100[0]:mem=94371840kb:ncpus=8+mnode100[1]:ncpus=8)

1341178.mmaster02
job_state = R
queue = teachingq
Resource_List.select = 1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb
Resource_List.walltime = 24:00:00
Resource_List.mem = 90gb
Resource_List.ncpus = 16
Resource_List.mpiprocs = 1
resources_used.ncpus = 16
resources_used.walltime = 00:00:00
resources_used.cput = 00:00:00
resources_used.mem = 0b
resources_used.vmem = 0kb
ctime = Sun Jun  7 17:52:40 2026
stime = Sun Jun  7 17:52:40 2026
exec_vnode = (mnode101[0]:mem=94371840kb:ncpus=8+mnode101[1]:ncpus=8)
```

A second early running check at about two minutes confirmed that both jobs had moved past the pre-solver shell failure and were consuming nonzero resources:

```text
1341177.mmaster02
job_state = R
resources_used.walltime = 00:01:52
resources_used.cput = 00:01:07
resources_used.cpupercent = 175
resources_used.mem = 803108kb
resources_used.vmem = 7794956kb

1341178.mmaster02
job_state = R
resources_used.walltime = 00:01:51
resources_used.cput = 00:03:03
resources_used.cpupercent = 275
resources_used.mem = 1385964kb
resources_used.vmem = 7671560kb
```

## Next Check

Monitor:

```bash
qstat -f 1341177.mmaster02 1341178.mmaster02
tail -80 /home/pr21vyci/master_thesis/Abaqus_trial/stage16n_r1b_restart_ref_250cycles.o1341177
tail -80 /home/pr21vyci/master_thesis/Abaqus_trial/stage16n_r1a_restart_ref_500cycles.o1341178
```

After completion, verify that `.res`, `.stt`, `.mdl`, and/or `.sim` restart files exist in each case directory before preparing native restart continuation tests.
