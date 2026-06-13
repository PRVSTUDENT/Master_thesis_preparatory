# Stage 16N-R4J True +50 Cycle-Skip Result

Checked on 2026-06-13 after the scratch-based R4J jobs completed.

## Job outcome

Both R4J jobs finished in PBS with `Exit_status=0`. The Abaqus `.sta` files for both cases end with `THE ANALYSIS HAS COMPLETED SUCCESSFULLY`.

| Case | PBS job | Restart | Material-state jump | Solved cycles | Endpoint | Walltime | Host |
|---|---:|---:|---:|---:|---:|---:|---|
| R4J1 | 1344946 | 250 | 250 -> 300 | 301--500 | 500 | 04:19:28 | mnode100 |
| R4J2 | 1344947 | 500 | 500 -> 550 | 551--750 | 750 | 04:11:10 | mnode101 |

PBS accounting:

- R4J1 used `17:56:39` CPU time, `571` CPU percent, and `94377788kb` memory.
- R4J2 used `17:28:03` CPU time, `568` CPU percent, and `94372048kb` memory.
- Both jobs requested `select=1:ncpus=16:mpiprocs=1:ompthreads=16:mem=90gb`, `walltime=24:00:00`, and ran in `teachingq`.

## Comparison result

The true +50 cycle-skip tests did not satisfy the existing Stage 16N pass threshold. This is not a solver failure; it is the first nonzero cycle-skip accuracy boundary observed after the restart-preserved overwrite route was repaired.

| Case | Compared cycle | Status | Max global error | Max primary local error | Diagnostic S11 error |
|---|---:|---|---:|---:|---:|
| R4J1 | 500 | fail | 1.8127809% | 14.384123% | 9.4269674% |
| R4J2 | 750 | fail | 1.7938482% | 14.426805% | 11.71291% |

Largest primary-local contributors:

- R4J1: `HOLE_RING_SDV8_MAX` reached `14.384123%`; `HOLE_RING_MISES_MAX` reached `10.455008%`; `HOLE_RING_SDV11_MAX` reached `11.750774%`.
- R4J2: `HOLE_RING_MISES_MAX` reached `14.426805%`; `HOLE_RING_SDV8_MAX` reached `9.4496575%`.

## Interpretation

R3J +5, +10, and +20 validated stable restart-preserved UMAT material-state overwrite, but the audited R3J decks still solved all continuation cycles. R4J fixed that by solving only cycles 301--500 and 551--750 after applying a +50 material-state jump.

Therefore the thesis-safe conclusion is:

> Native Abaqus restart plus UMAT-side material-memory overwrite solves the mechanical reinjection instability of the SDVINI/SIGINI scratch route, but a true +50 skipped-cycle acceleration is outside the current safe accuracy range for the inhomogeneous plate-with-hole benchmark and linear state extrapolation.

The next scientific step is a bracketed true-skip study between +20 and +50, for example +30 or +40, using the R4J deck pattern where the solved continuation starts after the jumped cycle target.

## Lightweight evidence uploaded

Heavy Abaqus files remain excluded from GitHub. The uploaded evidence is limited to PBS accounting, `.sta` completion files, comparison CSVs, selected loop/local-state CSVs, small wrapper logs, and overwrite/parallelism traces under:

- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4J1_250_to_300_solve_301_to_500/`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_restart_control/restart_jump_cases/R4J2_500_to_550_solve_551_to_750/`
