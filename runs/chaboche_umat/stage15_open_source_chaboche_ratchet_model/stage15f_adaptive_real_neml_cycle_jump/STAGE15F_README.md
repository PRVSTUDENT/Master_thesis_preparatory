# Stage 15F Adaptive Real NEML Cycle-Jump Refinement

Stage 15F is still reference-data based. It does not run long NEML simulations and does not attempt internal-state reinjection.

Inputs:

- `docs/stage15_real_neml_cycle_jump_package/baseline/B1_stress_m150_to_250_cycle_summary.csv`
- `docs/stage15_real_neml_cycle_jump_package/stage15e_results/STAGE15E_ACCEPTANCE_TABLE.csv`

Outputs:

- `STAGE15E_BEST_ACCEPTED_METHODS_BY_TARGET.csv`
- `STAGE15F_ADAPTIVE_JUMP_ROUTES.csv`
- `STAGE15F_ADAPTIVE_JUMP_ERRORS.csv`
- `STAGE15F_ACCEPTED_ROUTE_SUMMARY.csv`
- `STAGE15F_MASTER_SUMMARY.md`
- `plots/B1_adaptive_route_prediction.svg`
- `plots/B1_error_vs_jump_size.svg`
- `plots/B1_accepted_jump_map.svg`

Run:

```bash
bash run_stage15f_smoke_hpc.sh
qsub submit_stage15f_adaptive_jump.pbs
```

