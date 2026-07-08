# Stage 15K Nesnas-Saanouni-Style Formulation

For each state or control variable `q_i`, estimate `dq_i/dN` from recent
cycle-boundary states. The adaptive cycle increment is

`DeltaN_i = floor(epsilon_i * max(abs(q_i), q_min_scale_i) / max(abs(dq_i/dN), tiny))`.

The accepted candidate is the minimum variable-wise increment, capped by the
requested target, `DeltaN_max`, and the growth factor. The full NEML state
vector includes stress, strain, all internal history variables, time,
temperature, energy `u`, and plastic dissipation/work `p`.
