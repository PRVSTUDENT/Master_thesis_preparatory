# Stage 15D Baseline Status

Stage 15D produced useful walltime-limited real NEML baseline data, but the PBS job ended by memory cgroup kill near the end of the allocation.

## Primary References

| Case | Available cycles | Final mean strain | Final ratcheting strain |
|---|---:|---:|---:|
| B1_stress_m150_to_250 | 279725 | 10.41562762490873 | 10.401657666498515 |
| B2_stress_0_to_300 | 183632 | 0.10936805050368814 | 0.07868953340165502 |

## Interpretation

These baselines are valid for Stage 15E targets inside the available range. They should be described as walltime-limited reference baselines, not completed infinite-life baselines.

The Stage 15E first run intentionally avoids targets beyond:

- B1: 250000 cycles
- B2: 180000 cycles

