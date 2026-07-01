# Adaptive Cycle-Jump Prediction in Abaqus

This minor project packages the Stage 16N restart-based fatigue simulation results into a lightweight adaptive cycle-jump workflow.

The Abaqus/PBS runs provide the classified evidence. The adaptive selector script reads that evidence and identifies the largest accepted jump target and the first rejected target.

## Main result

For the investigated Chaboche UMAT benchmark, the accepted 250-branch extrapolated true-jump boundary is:

```text
source cycle 250 -> target cycle 271 = accepted
source cycle 250 -> target cycle 272 = rejected
```

The exact/native restart control at target272 passed with zero error. Therefore, the target272 failure is localized to extrapolated internal-state prediction, not Abaqus native restart continuity.

## Files

```text
data/stage16n_boundary_summary.csv
scripts/adaptive_jump_selector.py
```

## Run

From this folder:

```bash
python scripts/adaptive_jump_selector.py
```

Expected decision:

```text
Accepted boundary: target271
First rejected extrapolated target: target272
Exact/native restart at target272: pass
```

## Interpretation

The adaptive decision rule is:

1. Collect classified jump results for each candidate target.
2. Accept a target only when all true-jump evidence at that target passes.
3. Reject the first higher target with reproducible true-jump failure.
4. Use exact/native restart control to separate Abaqus restart-continuity error from extrapolated state-prediction error.
5. If exact/native control passes but extrapolated true-jump fails, stop widening targets and redesign the state predictor.

## Project conclusion

Target271 is the accepted adaptive cycle-jump boundary from source cycle 250. Target272 is the first rejected extrapolated true-jump target. Since exact/native target272 restart passes with zero error, the limiting factor is the extrapolated internal-state prediction, not the Abaqus restart path.
