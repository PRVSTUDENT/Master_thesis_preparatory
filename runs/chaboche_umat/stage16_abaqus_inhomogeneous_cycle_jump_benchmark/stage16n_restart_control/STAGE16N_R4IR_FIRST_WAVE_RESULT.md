# Stage 16N R4I-R First-Wave Result

Updated: 2026-06-21.

## Job status

The R4I-R first wave is no longer in the live PBS queue as of `Sun Jun 21 05:47:55 CEST 2026`. PBS history no longer returns records for `1350601` or `1350602`, so final classification uses the scratch case status files, PBS stdout, Abaqus completion messages, and copied comparison CSVs.

| Case | PBS job | Source solve | Restart | Final cycle | Result | Max global error | Max primary local error | Diagnostic S11 error |
|---|---:|---|---|---:|---|---:|---:|---:|
| R4I-R1 | 1350601.mmaster02 | deck-clone 250--281 | 280 -> 281--500 | 500 | pass | 0 | 0 | 0 |
| R4I-R2 | 1350602.mmaster02 | buffered 250--300 | 280 -> 281--500 | 500 | fail | 1.1887403% | 11.83033% | 0.92936729% |

## Interpretation

R4I-R1 exactly reproduces the cycle-500 reference, so cloning/truncating the clean direct replay deck shape fixes the branch that failed in R4H2/R4I1. R4I-R2, despite the longer 250--300 source buffer, reproduces the same failing source-split signature seen earlier: the dominant mismatch is `HOLE_RING_SDV8_MAX` at `11.83033%`.

This separates the failure mode from mere post-target source length. The deck/source-generation shape matters; a larger buffered generated source is not enough to repair restart from cycle 280.

## Evidence uploaded

Lightweight evidence was copied from `/scratch/pr21vyci/stage16n_r4ir/...` into the two R4I-R case folders:

- `STAGE16N_R4I_CASE_STATUS.md`
- `*_comparison_summary.csv`
- `*_comparison_details.csv`
- `*_cycle_metrics.csv`
- `*_selected_cycle_loops.csv`
- `*_selected_cycle_local_states.csv`
- `*_source_*_cycle_metrics.csv`
- `*.pbs.out`

No heavy Abaqus files were copied into the repository.

## Second-wave gate

R4I-R3 and R4I-R4 were submitted on 2026-06-21 through the guarded storage-gated workflow:

| Case | PBS job | Source solve | Restart | Purpose |
|---|---:|---|---|---|
| R4I-R3 | 1350673.mmaster02 | generated buffered 250--300 | 270 -> 271--500 | Test whether generated-buffer mismatch also appears at restart 270. |
| R4I-R4 | 1350674.mmaster02 | generated buffered 500--525 | 505 -> 506--750 | Test whether generated-buffer mismatch also appears on the 500 -> 505 branch. |

Both were running by `Sun Jun 21 05:59 CEST` with 16 cores, 90 GB memory, and 24 h walltime. PBS stdout is under `/scratch/pr21vyci/stage16n_r4ir_pbs/`.

## Prepared deck-clone confirmations

R4I-R5 and R4I-R6 are prepared but not submitted:

| Case | Source solve | Restart | Expected first solved cycle | Purpose |
|---|---|---|---|---|
| R4I-R5 | deck-clone 250--271 | 270 -> 271--500 | `CYCLE_0271` | Confirm deck-clone/truncate fixes the cycle-270 branch. |
| R4I-R6 | deck-clone 500--506 | 505 -> 506--750 | `CYCLE_0506` | Confirm deck-clone/truncate fixes the 500 -> 505 branch. |

R4J9/R4J10 remain blocked. If R4I-R5/R4I-R6 pass, the next implementation step is to refactor future source generation to deck-clone/truncate and then rerun exact controls before any new extrapolated true jump.
