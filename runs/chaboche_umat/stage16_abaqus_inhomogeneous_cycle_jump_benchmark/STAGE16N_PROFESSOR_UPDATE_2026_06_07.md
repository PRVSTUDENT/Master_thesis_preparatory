# Stage 16N Professor Update - 2026-06-07

The Stage 16N plate-with-hole benchmark confirms that cycle jumping is meaningful but difficult in an inhomogeneous Abaqus model. A full 1000-cycle reference was completed, and the best accepted fixed jump is a small cycle-100 jump from 100 to 105 followed by normal continuation to 250. This case, `B1D5`/`B1D5_EQ`, passed the 5% primary scalar-metric gate with 2.34986% maximum primary error.

The adaptive table estimated a cycle-100 jump of about 24 cycles, while the observed accepted jump is only 5 cycles. This gives an effective safety factor of about 0.21. The result suggests that local hole-ring variables, especially local stress and STATEV extrema, are much more restrictive than the global hysteresis response.

Larger cycle-100 jumps and later-cycle reinjection showed strong local sensitivity. The manual `SDVINI`/`SIGINI` state-initialization route failed to robustly equilibrate at cycle 250, including exact, `SDVINI`-only, `SIGINI`-only, and combined diagnostic variants. Therefore the current Abaqus result is best interpreted as a validated small-jump demonstration plus a limitation study of manual state reinjection in an inhomogeneous finite-element model.

The next path is not to repeat B2/B3 with the same scratch state-initialization route. Instead, Stage 16N-R will repair the reinjection strategy by preserving the Abaqus finite-element state through native restart or in-analysis continuation, then applying cycle jumps only to independent material memory variables in the UMAT.
