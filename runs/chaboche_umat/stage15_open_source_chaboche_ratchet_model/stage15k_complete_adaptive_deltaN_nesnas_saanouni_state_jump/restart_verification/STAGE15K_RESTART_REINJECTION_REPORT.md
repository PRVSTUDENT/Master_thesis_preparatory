# Stage 15K Restart/Reinjection Verification Report

## Gate
- Gate: `2 exact restart/reinjection verification`
- Status: **PASS**
- `restart_reinjection_pass`: `true`

## Environment
- Real NEML backend used: `true`
- NEML path: `/home/pr21vyci/.local/lib/python3.11/site-packages/neml/__init__.py`
- Python executable: `/cluster/stages/2024.0/spack-0.22/opt/spack/linux-rocky8-cascadelake/gcc-11.4.0/python-3.11.7-qfpdtq2pisspwunkuc4fqloxqo2ltw6j/bin/python`
- Python version: `3.11.7 (main, Jul 24 2024, 09:40:09) [GCC 11.4.0]`
- Platform: `Linux-4.18.0-553.124.1.el8_10.x86_64-x86_64-with-glibc2.28`

## Test Definition
- Direct run: ramp to 250 MPa, then cycles `1 -> 100`.
- Restarted run: ramp to 250 MPa, cycles `1 -> 50`, save complete state, reload complete state, continue cycles `51 -> 100`.
- Case: `B1_stress_m150_to_250`
- Material: `P2_three_backstress_screen`
- Stress range: `-150` to `250` MPa
- Points per cycle: `40`
- Update API: real NEML `SmallStrainRateIndependentPlasticity.update_sd` with explicit prior strain, stress, history, temperature, time, `u`, and `p`.

## Saved State
- Cycle-50 JSON reload reproduced saved state before continuation: `true`
- Saved restart state: `restart_verification/restart_saved_50_cycle_state.json`

## Final State Metrics
| Quantity | Direct cycle 100 | Restarted cycle 100 |
|---|---:|---:|
| stress_11 | 2.50000000000000057e+02 | 2.50000000000000057e+02 |
| strain_11 | 2.26863354477504740e-02 | 2.26863354477504740e-02 |
| accumulated inelastic strain | 4.12619023482160174e-01 | 4.12619023482160174e-01 |
| backstress norm | 5.77580736566827397e+01 | 5.77580736566827397e+01 |
| energy u | 6.35970458430444054e+01 | 6.35970458430444054e+01 |
| plastic dissipation/work p | 6.34407958430447678e+01 | 6.34407958430447678e+01 |

## Error Summary
| Component | Max abs error | Max rel error | Strict pass | Relaxed pass |
|---|---:|---:|---:|---:|
| stress | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| strain | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| history_internal_variables | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| accumulated_inelastic_strain | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| backstress_norm | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| time | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| energy_u | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |
| plastic_dissipation_or_work_p | 0.00000000000000000e+00 | 0.00000000000000000e+00 | true | true |

## Acceptance
- Strict absolute tolerance: `1.0e-08`
- Strict relative tolerance: `1.0e-08`
- Near-roundoff diagnostic tolerance: `1.0e-10`
- Relaxed diagnostic tolerance: `1.0e-06`
- No NaN/inf appeared: `true`

## Stop/Go Decision
**GO TO GATE 3 ONLY.** Gate 2 passed; fixed `Delta N` state-jump smoke testing may be prepared next. Do not run adaptive/full PBS yet.
