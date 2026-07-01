# Adaptive Cycle-Jump Prediction in Abaqus

## Problem

Cyclic Abaqus simulations with history-dependent material models are expensive because every cycle updates internal state variables that control the later stress-strain response. For a Chaboche UMAT, skipping cycles is attractive, but unsafe if the extrapolated state no longer matches the state that a native continuation would have produced.

The practical question for the Stage 16N benchmark was therefore narrow and measurable: from a validated source cycle, how far can the simulation jump while preserving the relevant global and local response?

## Method

This project packages the Stage 16N restart-based cycle-jump work into a lightweight adaptive workflow:

1. Use Abaqus restart mechanics to build controlled source and continuation cases.
2. Compare extrapolated true-jump continuations against the 1000-cycle reference evidence.
3. Classify candidate targets as pass, fail, or control evidence using global and local error metrics.
4. Run a lightweight Python selector over the classified CSV evidence.
5. Accept the largest target where all true-jump evidence passes.
6. Reject the first higher target where true-jump evidence fails.
7. Use exact/native restart controls to separate extrapolated state-prediction error from Abaqus restart-continuity error.

The Abaqus/PBS runs are the evidence layer. The Python selector is the adaptive decision layer. The plotting script turns the accepted/rejected boundary into GitHub-ready figures.

## Evidence

The decisive 250-branch evidence came from the R4M, R4O, and R4P result sequence:

- R4M regenerated the complete cycle-250 source package and showed that target270 passes.
- R4O tightened the boundary and showed that target271 passes while target272 fails.
- R4P reproduced the boundary with repeat, diagnostic, and 8-core calibration runs.
- R4P showed target271 passes reproducibly.
- R4P showed target272 fails reproducibly.
- R4P exact/native target272 restart control passed with zero global, primary-local, and S11 comparison error.

The adaptive selector was then smoke-tested through PBS without launching Abaqus. The HPC test passed with the expected decision:

```text
Accepted boundary: target271
First rejected extrapolated target: target272
Exact/native restart at target272: pass
```

## Nesnas-Saanouni-Style Adaptive Jump Model

A second adaptive layer implements a Nesnas-Saanouni-style bounded monitor increment model. The monitored quantities are the available comparison metrics:

```text
global error
primary-local error
S11 error
```

The normalized monitor ratio is:

```text
R = max(
    global_error / global_tolerance,
    primary_local_error / primary_local_tolerance,
    S11_error / S11_tolerance
)
```

The tested tolerances are 1% global error, 5% primary-local error, and 1% S11 error. A candidate target is admissible only when all true-jump records at that target pass and remain below tolerance (`R <= 1`).

```text
target270: R = 0.796601, pass
target271: R = 0.835717, pass
target272: R = 9.42718, fail
```

The first-order monitor trend proposes target274 before validation capping, but target272 is already rejected by direct validation evidence. The safety cap therefore returns the final recommendation to target271:

```text
Final recommended jump:
  target cycle: 271
  skipped cycles: 21
```

This model was smoke-tested through PBS job `1362113.mmaster02` without launching Abaqus. The job finished with `Exit_status=0` and the expected recommendation.

This implementation is Nesnas-Saanouni-style rather than a full constitutive-level reproduction, because the current lightweight evidence contains comparison metrics rather than complete per-integration-point internal-variable histories.

## Conclusion

The safe adaptive boundary from source cycle 250 is target271. Target272 is the first reproducibly rejected extrapolated true-jump target.

Because the exact/native target272 restart control passes with zero comparison error, the target272 rejection is not caused by Abaqus restart mechanics. The limiting factor is extrapolated internal-state prediction. Further widening should remain blocked until the predictor is redesigned or diagnosed.

The project is now packaged as a compact GitHub minor project with:

- classified boundary evidence,
- an adaptive selector,
- an HPC smoke-test record,
- boundary figures,
- README documentation,
- project-summary and resume-ready documentation.
