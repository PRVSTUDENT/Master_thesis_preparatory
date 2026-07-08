# Stage 16N-R3J Extrapolated State

- Previous cycle: `250`
- Base cycle: `500`
- Slope pair: `250 -> 500`
- Jump cycles: `21`
- Extrapolated material-state cycle: `521`
- Formula: `STATEV_jump = STATEV_base + jump_cycles * dSTATEV/dN`
- Overwrite payload includes `SDV1-SDV27`; the R3J UMAT overwrites only `STATEV(1:25)`.
- Stress columns are copied from the base cycle and are not used by the R3J UMAT overwrite.
- Element/IP records: `25184`
- State CSV: `state.csv`
- State binary: `state.bin`
