# Chaboche-v1 amplitude sweep report

## Purpose

The previous cyclic validation used Umax = +/-0.5 mm over L0 = 10 mm, i.e. +/-5% engineering strain. For a first steel validation this is too aggressive, so the response reached stresses of several GPa and accumulated about 0.047 plastic strain. That run proved the pipeline, but it was not a good first physical calibration target.

## Run status

All four lower-amplitude Abaqus jobs passed datacheck and completed the full analysis with 57 increments, 0 cutbacks, 0 warnings, and 0 errors.

## Comparison

| eps_amp | U_amp mm | max S11 MPa | min S11 MPa | max RF1 N | min RF1 N | final SDV1 | max SDV1 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.001 | 0.01 | 209.7834 | -209.7834 | 839.1337 | -839.1337 | 0 | 0 |
| 0.002 | 0.02 | 419.5669 | -419.5669 | 1678.2675 | -1678.2675 | 0 | 0 |
| 0.005 | 0.05 | 648.2125 | -674.7499 | 2592.8499 | -2698.9998 | 0.005597596522 | 0.005597596522 |
| 0.01 | 0.1 | 727.8698 | -733.9141 | 2911.4790 | -2935.6565 | 0.02290419675 | 0.02290419675 |

## Interpretation

+/-0.1% and +/-0.2% are essentially elastic for this parameter set: stress scales linearly and SDV1 remains zero. +/-0.5% is the best first cyclic validation amplitude because it activates plasticity while keeping stresses in a much more plausible range than the old +/-5% case. +/-1.0% gives a stronger plastic response and may be useful after the first loop shape is accepted.

SDV1 remains reasonable in the lower sweep: it is zero below first yield, about 0.0056 at +/-0.5%, and about 0.0229 at +/-1.0%. The hysteresis shape is physically plausible as a first numerical check: elastic at small amplitudes, then open loops with plastic accumulation once the imposed strain exceeds the yield threshold.

## Generated files

- chaboche_vp_v1_amplitude_sweep_summary.csv
- chaboche_vp_v1_amplitude_sweep_stress_strain.svg
- chaboche_vp_v1_cyclic_eps001.inp
- chaboche_vp_v1_cyclic_eps001_summary.csv
- chaboche_vp_v1_cyclic_eps001_stress_strain.svg
- chaboche_vp_v1_cyclic_eps001_force_displacement.svg
- chaboche_vp_v1_cyclic_eps001_sdv1_time.svg
- chaboche_vp_v1_cyclic_eps002.inp
- chaboche_vp_v1_cyclic_eps002_summary.csv
- chaboche_vp_v1_cyclic_eps002_stress_strain.svg
- chaboche_vp_v1_cyclic_eps002_force_displacement.svg
- chaboche_vp_v1_cyclic_eps002_sdv1_time.svg
- chaboche_vp_v1_cyclic_eps005.inp
- chaboche_vp_v1_cyclic_eps005_summary.csv
- chaboche_vp_v1_cyclic_eps005_stress_strain.svg
- chaboche_vp_v1_cyclic_eps005_force_displacement.svg
- chaboche_vp_v1_cyclic_eps005_sdv1_time.svg
- chaboche_vp_v1_cyclic_eps010.inp
- chaboche_vp_v1_cyclic_eps010_summary.csv
- chaboche_vp_v1_cyclic_eps010_stress_strain.svg
- chaboche_vp_v1_cyclic_eps010_force_displacement.svg
- chaboche_vp_v1_cyclic_eps010_sdv1_time.svg
