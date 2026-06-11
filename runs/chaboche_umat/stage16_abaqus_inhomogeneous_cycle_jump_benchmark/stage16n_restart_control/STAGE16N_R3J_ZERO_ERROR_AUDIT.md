# Stage 16N-R3J Zero-Error Audit

Audit date: 2026-06-11 Europe/Berlin

Purpose: verify that the exact zero-error R3J result was not caused by accidentally comparing a reference output against itself or by a no-op UMAT jump.

## Summary

The audit supports the +5 R3J result as a real restart-preserved material-memory jump:

- R3J output CSVs and reference CSVs are distinct files with distinct inode, size, timestamp, and SHA-256 hashes on HPC.
- The UMAT overwrite hook fired at the intended restart continuation calls:
  - R3J1: `KSTEP=251`, `KINC=0`, `TIME2=250.000000000019`.
  - R3J2: `KSTEP=501`, `KINC=0`, `TIME2=499.999999999974`.
- The extrapolated `state.csv` differs from the base checkpoint state for every integration point in `STATEV(1:25)`.
- The cycle rows extracted from the R3J jobs have the intended endpoint cycles:
  - R3J1 rows cover cycles 251-500 and include target cycle 500.
  - R3J2 rows cover cycles 501-750 and include target cycle 750.
- The comparison used the intended target endpoints:
  - R3J1 compared cycle 500 against the pilot 1000-cycle reference.
  - R3J2 compared cycle 750 against the parallel 1000-cycle reference.

## File-Identity Check

R3J1 jump metrics:

```text
inode=15070398187
size=24393
sha256=d2767c555a94326525b181f7bb378145fe48b87aae1364960bbfd70d87705055
```

R3J1 pilot reference metrics:

```text
inode=8646437272
size=57660
sha256=324bce83fb519b5a306bb1f31cc47d8ca8933e3581b5a3ff7edd56faf83e04d7
```

R3J2 jump metrics:

```text
inode=17267811518
size=24409
sha256=cbf1aaab481976b2fbf8713bb5f6776324be6878f6a5f93c7472d7d9c925683b
```

R3J2 parallel reference metrics:

```text
inode=34395911545
size=97338
sha256=28313ca943cd5089de11155f2874b295aae0d29472bed17fea7f6c0deffd6c92
```

## UMAT Overwrite Trace

The overwrite marker is written to the Abaqus `.dat` file, not to `.msg`. The wrapper grep currently checks `.msg`, so the generated `_overwrite_trace.txt` files are empty even though the overwrite occurred.

R3J1 `.dat` contains 9 sampled overwrite traces, for example:

```text
STAGE16N_R3J_OVERWRITE NOEL=1 NPT=1 KSTEP=251
KINC=0 TIME1=0.0 TIME2=250.000000000019 STATEV1=2.97743529081345 STATEV8=-11.7529139836629 STATEV11=-0.005321951031995316
```

R3J2 `.dat` contains 9 sampled overwrite traces, for example:

```text
STAGE16N_R3J_OVERWRITE NOEL=1 NPT=1 KSTEP=501
KINC=0 TIME1=0.0 TIME2=499.999999999974 STATEV1=5.83907624721527 STATEV8=-11.3875962066650 STATEV11=-0.005878125810995697
```

## Extrapolated-State Delta Check

R3J1 base checkpoint cycle 250 vs extrapolated state cycle 255:

```text
records=25184
state_fields=25
changed_records=25184
changed_values=478496
max_abs_delta=0.527609507243
max_rel_delta=0.00615826766755
max_delta_field=SDV8
max_delta_key=(NOEL=1240, NPT=3)
sum_abs_delta=5753.63205921
```

R3J2 base checkpoint cycle 500 vs extrapolated state cycle 505:

```text
records=25184
state_fields=25
changed_records=25184
changed_values=478496
max_abs_delta=0.29437286377
max_rel_delta=0.0114675398283
max_delta_field=SDV2
max_delta_key=(NOEL=1240, NPT=3)
sum_abs_delta=3522.13992805
```

## Remaining Implementation Fix

The R3J runner should grep the Abaqus `.dat` file for `STAGE16N_R3J_OVERWRITE`, not only the `.msg` file. The R3J case generator was also updated so future generated runners use repository-relative Linux reference paths for HPC comparison instead of Windows absolute paths.
