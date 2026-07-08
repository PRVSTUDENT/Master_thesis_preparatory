# Stage 16N-R3J +10 Zero-Error Audit

Date: 2026-06-11

## Scope

This audit checks the credibility of the exactly zero-error R3J +10 restart-preserved jump results:

- R3J3: native restart at cycle 250, material-state jump 250 -> 260, endpoint comparison at cycle 500.
- R3J4: native restart at cycle 500, material-state jump 500 -> 510, endpoint comparison at cycle 750.

## Audit Results

1. The jump metrics were not self-compared.
   - R3J3 jump metrics: inode `17858926321`, size `24393`, SHA-256 `cf5895aa90af959363dbaba4468526b9397af9acb5c1219e6b4f9c32457ed6e0`.
   - R3J3 reference metrics: inode `8646437272`, size `57660`, SHA-256 `324bce83fb519b5a306bb1f31cc47d8ca8933e3581b5a3ff7edd56faf83e04d7`.
   - R3J4 jump metrics: inode `19358920300`, size `24409`, SHA-256 `0d9fb35cf4e49d7b288f0f9243d076c29f53e9db40345a3925e5eb7fcdf7012b`.
   - R3J4 reference metrics: inode `34395911545`, size `97338`, SHA-256 `28313ca943cd5089de11155f2874b295aae0d29472bed17fea7f6c0deffd6c92`.

2. The extrapolated state differs from the checkpoint base state.
   - R3J3: `25184` records compared, `25184` records changed; `528728` of `831072` numeric state/stress values changed; max absolute delta `1.0552190144856723`.
   - R3J4: `25184` records compared, `25184` records changed; `521304` of `831072` numeric state/stress values changed; max absolute delta `0.5887457275390595`.

3. The UMAT overwrite fired at the intended restart hook.
   - R3J3 `.dat` file contains the trace marker at `KSTEP=251`.
   - R3J4 `.dat` file contains the trace marker at `KSTEP=501`.
   - Each production `.dat` contains 9 trace lines, matching the deliberately limited trace subset printed by the UMAT.

4. The continuation starts after the restart checkpoint and spans the intended target range.
   - R3J3 cycle metrics contain 250 rows from cycles `251` through `500`.
   - R3J4 cycle metrics contain 250 rows from cycles `501` through `750`.

5. Endpoint cycles are correct.
   - R3J3 comparison target is cycle `500`.
   - R3J4 comparison target is cycle `750`.

## Conclusion

The +10 zero-error result is credible under the current audit checks. The jump files are distinct from the reference files, the generated material-state payload differs from the base restart state at every integration-point record, the UMAT overwrite marker appears at the restart continuation hook, and endpoint cycle accounting is correct.

Scientific caution remains: before claiming broad predictive acceleration, larger jumps should be tested until a nonzero-error boundary is observed. The next controlled escalation is +20:

- R3J5: 250 -> 270 -> 500.
- R3J6: 500 -> 520 -> 750.

No new Abaqus submissions should be made until the `/home` heavy-file offload has completed and the R3J3/R3J4 heavy solver outputs have been moved to `/scratch`.
