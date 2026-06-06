# Stage 16N HPC Mail Policy

All future Stage 16N PBS submit scripts should explicitly request mail on job start, abort, and end:

```text
#PBS -m abe
#PBS -M pr21vyci@mailserver.tu-freiberg.de
```

Meaning:

```text
a = abort/failure mail
b = begin/start mail
e = end/completion mail
```

This is required because PBS defaults may only send abort mail. In the previous job accounting, `Mail_Points = a` meant that start and end notifications were not requested.

Before submitting any new generated PBS script, check:

```bash
grep -E '^#PBS -m|^#PBS -M' submit_script.pbs
```

After submission, verify with:

```bash
qstat -f <job_id> | egrep 'Mail_Points|Mail_Users'
```

Expected result:

```text
Mail_Points = abe
Mail_Users = pr21vyci@mailserver.tu-freiberg.de
```
