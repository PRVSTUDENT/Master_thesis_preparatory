# Stage 15K Complete Method Plan

Stage 15K implements gated real-NEML state jumping:

1. introspection,
2. exact restart/reinjection,
3. fixed `Delta N` smoke,
4. fixed `Delta N` matrix,
5. adaptive `Delta N` matrix,
6. validation and plots.

The implementation uses full NEML material state extrapolation and reinjection,
then continues the real NEML simulation after the jump.
