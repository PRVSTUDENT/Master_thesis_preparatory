# Chaboche-v1 eps005 10-cycle report

## Run status

- Datacheck status: passed
- Full analysis status: completed
- Number of increments: 507
- Cutbacks: 0
- Warnings: 0
- Errors: 0

## Summary values

- Max S11: 671.8238525 MPa
- Min S11: -674.749939 MPa
- Max RF1: 2687.29541 N
- Min RF1: -2698.999756 N
- Final SDV1: 0.07026678324
- Max SDV1: 0.07026678324

## Cycle-end SDV1

| cycle | time | U1 | Avg_S11 | Avg_SDV1 | Avg_SDV15 |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.9902578 | -0.001948437537 | 333.2216187 | 0.005597596522 | 0 |
| 2 | 1.9902579 | -0.001948437537 | 336.5193787 | 0.01277730055 | 0 |
| 3 | 2.9902577 | -0.001948437537 | 336.5388184 | 0.01996727288 | 0 |
| 4 | 3.9902577 | -0.001948437537 | 336.4801941 | 0.02715636604 | 0 |
| 5 | 4.9902577 | -0.001948437537 | 336.4197388 | 0.0343443118 | 0 |
| 6 | 5.9902577 | -0.001948437537 | 336.359314 | 0.04153110832 | 0 |
| 7 | 6.9902577 | -0.001948437537 | 336.2988892 | 0.04871675 | 0 |
| 8 | 7.9902577 | -0.001948437537 | 336.2384949 | 0.05590124428 | 0 |
| 9 | 8.9902582 | -0.001948437537 | 336.1781616 | 0.06308458745 | 0 |
| 10 | 10 | 0 | 377.0350647 | 0.07026678324 | 0 |

## Interpretation

The 10-cycle eps005 run keeps accumulating: SDV1 increases at every cycle end and reaches 0.07026678324 by the end of cycle 10.
The selected-loop overlay should be used to judge whether the hysteresis shape has stabilized; the cycle-end SDV1 trend indicates continued accumulated viscoplastic strain rather than a fully saturated state within 10 cycles.

## Generated files

- chaboche_vp_v1_cyclic_eps005_10cycles.inp
- chaboche_vp_v1_cyclic_eps005_10cycles_summary.csv
- chaboche_vp_v1_cyclic_eps005_10cycles_cycle_end.csv
- chaboche_vp_v1_cyclic_eps005_10cycles_stress_strain.svg
- chaboche_vp_v1_cyclic_eps005_10cycles_force_displacement.svg
- chaboche_vp_v1_cyclic_eps005_10cycles_sdv1_time.svg
- chaboche_vp_v1_cyclic_eps005_10cycles_cycle_end_sdv1.svg
- chaboche_vp_v1_cyclic_eps005_10cycles_selected_loops.svg
- CHABOCHE_EPS005_10CYCLE_REPORT.md
