# Chaboche-v1 eps005 10-cycle diagnostics

## Key diagnostics

- Total SDV1 is cumulative accumulated viscoplastic strain p and should not be expected to decrease.
- Total SDV1 monotonic: yes.
- Delta SDV1 per cycle stabilizes in rate form: cycles 2-10 average 0.007185465191 with range 1.026829705e-05, relative range 0.001429.
- Residual stress at zero strain is nearly steady after cycle 2: cycle 2 336.5193787 MPa, cycle 10 377.0350647 MPa, change 40.51568604 MPa.
- Stress amplitude is essentially stable after cycle 2: cycle 2 671.130188 MPa, cycle 10 671.8389282 MPa, change 0.7087402344 MPa.
- Mean stress drifts only mildly after cycle 2: cycle 2 -0.3223266602 MPa, cycle 10 -0.01507568359 MPa, change 0.3072509766 MPa.
- Selected cycles 1, 2, 5, and 10 form a stable hysteresis family after the initial transient, based on nearly constant stress amplitude and Delta SDV1.

## Cycle increments

| cycle | SDV1_start | SDV1_end | Delta_SDV1 | S11_zero_end | Stress_Amplitude | Mean_Stress |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0.005597596522 | 0.005597596522 | 333.2216187 | 661.4812012 | -13.26873779 |
| 2 | 0.005597596522 | 0.01277730055 | 0.007179704029 | 336.5193787 | 671.130188 | -0.3223266602 |
| 3 | 0.01277730055 | 0.01996727288 | 0.007189972326 | 336.5388184 | 671.410614 | -0.02243041992 |
| 4 | 0.01996727288 | 0.02715636604 | 0.007189093158 | 336.4801941 | 671.4763794 | -0.01531982422 |
| 5 | 0.02715636604 | 0.0343443118 | 0.007187945768 | 336.4197388 | 671.5369873 | -0.01513671875 |
| 6 | 0.0343443118 | 0.04153110832 | 0.007186796516 | 336.359314 | 671.5974731 | -0.01513671875 |
| 7 | 0.04153110832 | 0.04871675 | 0.007185641676 | 336.2988892 | 671.6578979 | -0.01507568359 |
| 8 | 0.04871675 | 0.05590124428 | 0.007184494287 | 336.2384949 | 671.7182922 | -0.01510620117 |
| 9 | 0.05590124428 | 0.06308458745 | 0.007183343172 | 336.1781616 | 671.7786255 | -0.01507568359 |
| 10 | 0.06308458745 | 0.07026678324 | 0.007182195783 | 377.0350647 | 671.8389282 | -0.01507568359 |

## Generated files

- chaboche_vp_v1_cyclic_eps005_10cycles_diagnostics_full.csv
- chaboche_vp_v1_cyclic_eps005_10cycles_quarter_points.csv
- chaboche_vp_v1_cyclic_eps005_10cycles_cycle_increments.csv
- chaboche_eps005_10cycles_delta_sdv1_per_cycle.svg
- chaboche_eps005_10cycles_residual_stress_per_cycle.svg
- chaboche_eps005_10cycles_stress_amplitude_per_cycle.svg
- chaboche_eps005_10cycles_mean_stress_per_cycle.svg
- CHABOCHE_EPS005_10CYCLE_DIAGNOSTICS_REPORT.md
