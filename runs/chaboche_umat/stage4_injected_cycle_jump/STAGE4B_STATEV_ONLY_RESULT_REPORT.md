# Stage 4B STATEV-Only Injection Result

## Input

- ODB: `chaboche_stage4b_cycle19_exact_to_cycle20_statev_only.odb`
- Reference STATEV: `stage4_injected_cycle_jump\cycle20_reference_statev.csv`
- Reference stress: `stage4_injected_cycle_jump\cycle20_reference_stress.csv`
- Step: `CYCLIC_CONT_STATEV_ONLY`
- Final frame value: `1`

## Key Comparison

| Quantity | STATEV-only value | Explicit cycle-20 reference | Absolute error | Relative error |
|---|---:|---:|---:|---:|
| STATEV1 | 0.00559759652242 | 0.142025694251 | 0.136428097729 | 96.0587437703% |
| S11 (MPa) | 374.138793945 | 376.434143066 | 2.29534912109 | 0.60976113973% |

## Boundary Output

- RIGHT_FACE node set resolved as: `RIGHT_FACE`
- RIGHT_FACE average U1: `0`
- RIGHT_FACE summed RF1: `1496.55517578`

## Corrected Interpretation

- This original STATEV-only job completed and produced final-frame STATEV and stress outputs.
- However, this run does **not** numerically confirm SDVINI initialization.
- The final STATEV1 value is close to a fresh one-cycle result, which indicates that the injected cycle-19 STATEV was not active in this run.
- Subsequent debug work found that the original input deck omitted `*INITIAL CONDITIONS, TYPE=SOLUTION, USER`.
- A copied debug deck with that keyword and a standard SDVINI signature proved STATEV injection numerically; see `STAGE4B_SDVINI_DEBUG_REPORT.md`.
- This original result should therefore be interpreted as a control/check run, not a successful injected continuation.

## Output

- Result CSV: `stage4_injected_cycle_jump\stage4b_statev_only_result.csv`
