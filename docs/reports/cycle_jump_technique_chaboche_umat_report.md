# Cycle-Jump Technique Report for the Chaboche UMAT Workflow

Generated locally: 2026-05-18

## Scope

This report documents the cycle-jump method used in this Abaqus/UMAT study. It covers:

- the theory of cycle-jump acceleration for cyclic inelastic simulations;
- the specific cycle-jump technique implemented in this work;
- the difference between this workflow and the Nesnas-Saanouni cycle-jump scheme;
- the Chaboche-type UMAT used in the simulations;
- the state transfer and re-initialization method using `SDVINI` and `SIGINI`;
- how the correctness of the injected starting state was verified;
- how displacement fields were treated;
- the simulations successfully completed so far.

The partial 4380-cycle / Stage 13 run and the current Stage 14 2000-cycle blockwise work are not counted as completed final results in this report.

## 1. Why Cycle Jumping Is Needed

Direct finite element simulation of cyclic plasticity or viscoplasticity is expensive because every cycle is normally integrated increment by increment. A 1000-cycle or 5000-cycle loading history can require tens of thousands of Abaqus increments, especially when a UMAT is used and the material response is path dependent.

Cycle jumping reduces this cost by exploiting the fact that many cyclic problems contain two time scales:

- a fast time scale inside each loading cycle, where stress, strain, and internal variables vary strongly;
- a slow cycle scale, where accumulated plastic strain, backstress, isotropic hardening, damage, or other state variables evolve gradually from one cycle to the next.

The basic idea is:

1. Run a small number of explicit cycles.
2. Extract cycle-end state variables.
3. Estimate the slow cycle-to-cycle evolution.
4. Predict the material state at a later cycle.
5. Re-initialize Abaqus at the predicted state.
6. Continue with normal finite element integration.
7. Compare against an explicit no-skip reference when available.

In this project, the state variable that most consistently controlled the error was `STATEV1`, interpreted as accumulated viscoplastic strain `p`. Stress and reaction force often recovered strongly after continuation, but accumulated state error remained the limiting metric.

## 2. General Cycle-Jump Theory

Let the material state at the end of cycle `N` be represented as

```text
Y_N = [stress_N, STATEV_N, displacement_N, other history variables_N]
```

For a conventional no-skip cyclic FE analysis, Abaqus computes

```text
Y_0 -> Y_1 -> Y_2 -> ... -> Y_N
```

by solving every loading increment. In a cycle-jump method, the aim is to approximate

```text
Y_N -> Y_{N + DeltaN}
```

without computing all intermediate cycles. If a selected internal variable `q` evolves smoothly over cycles, its cycle-space Taylor approximation is

```text
q(N + DeltaN) = q(N)
              + DeltaN * dq/dN
              + 0.5 * DeltaN^2 * d2q/dN2
              + ...
```

The simplest usable version is first order:

```text
q_pred(N + DeltaN) = q(N) + DeltaN * mean(Delta q / Delta N)
```

where the mean increment is estimated from a stable reference window, for example cycles 2 to 10.

The central numerical risk is that the extrapolated state may not be mechanically consistent with the finite element equilibrium state. Therefore a practical cycle-jump workflow must verify:

- state-variable consistency: injected `STATEV` values appear at the first output frame;
- stress consistency: injected residual stress appears at the first output frame;
- boundary/loading consistency: the continuation step starts at the intended point of the cyclic load;
- final accuracy: the continued result matches a no-skip reference within the chosen tolerance.

## 3. Nesnas-Saanouni Cycle-Jump Technique

The relevant Nesnas-Saanouni reference is:

K. Nesnas and K. Saanouni, "A cycle jumping scheme for numerical integration of coupled damage and viscoplastic models for cyclic loading paths," Revue Europeenne des Elements Finis, 9(8), 865-891, 2000. DOI: https://doi.org/10.1080/12506559.2000.10511493

The paper proposes a two-time-scale method for cyclic viscoplastic and damage models:

- small time scale: implicit integration of constitutive equations inside a loading cycle;
- large time scale: explicit cycle-jump integration over many cycles.

The method stores and restores a reduced but sufficient set of variables that measure how all relevant state variables evolve over cycles. It is not just a scalar postprocessing extrapolation. It is intended as a constitutive-level acceleration strategy for coupled damage and viscoplasticity, with Gauss-point and structural-level applications.

In conceptual form, Nesnas-Saanouni does the following:

1. Integrate representative cycles accurately using an implicit constitutive algorithm.
2. Measure the evolution of internal variables between cycles.
3. Use the cycle-scale evolution to estimate a jump over several cycles.
4. Restore the jumped material state.
5. Continue finite element integration.
6. Control accuracy by monitoring how all important state variables change.

This is broader than only extrapolating accumulated plastic strain. It is a complete material-state strategy.

## 4. Technique Used in This Work

The method developed here started as a scalar cycle-jump predictor and evolved into a predicted-state Abaqus continuation workflow.

### 4.1 Level 1: Postprocessing Cycle-Jump Predictor

The first validated cycle-jump method used `STATEV1`, accumulated viscoplastic strain, as the scalar slow variable.

From the 10-cycle baseline:

```text
mean Delta_STATEV1 over cycles 2-10 = 0.007185465191
relative range over cycles 2-10 = about 0.1429%
```

The predictor was:

```text
STATEV1_pred(N) = STATEV1_cycle10
                + (N - 10) * mean(Delta_STATEV1 cycles 2-10)
```

The 20-cycle explicit validation gave:

```text
Predicted STATEV1 at cycle 20 = 0.1421214351
Explicit STATEV1 at cycle 20  = 0.1420256943
Relative error                = 0.06741093536%
```

This validated the cycle-space extrapolation for the selected single-element Chaboche UMAT problem.

### 4.2 Level 2: Predicted-State FE Restart/Continuation

The workflow was then extended beyond postprocessing:

1. Predict a future cycle state from earlier cycles.
2. Generate a UMAT variant containing predicted `STATEV` and stress data.
3. Use Abaqus initial conditions to inject the state.
4. Run a short continuation analysis.
5. Compare the final state against an explicit no-skip reference.

The predicted-state continuation route is written as:

```text
base cycle -> predicted injection cycle -> continued target cycle
```

Example:

```text
cycle 10 -> predicted cycle 49 -> cycle 50
```

This skips cycles 11-48 and computes only the continuation from the injected state to cycle 50.

### 4.3 Long-Horizon Percentage Jump

For the 1000-cycle study, the workflow changed from a one-cycle continuation to a long continuation after a predicted jump:

```text
cycle 10 -> predicted target cycle -> continue normally to cycle 1000
```

The accepted boundary found in Stage 12 was:

```text
cycle 10 -> predicted cycle 373 -> continue to cycle 1000
```

This skipped 362 intermediate FE cycles and remained just inside the 1% `STATEV1` acceptance threshold:

```text
Final STATEV1 error = 0.998969124476%
Final S11 error     = 0.114850661342%
Final RF1 error     = 0.114850661342%
```

The first rejected case was target cycle 374:

```text
Final STATEV1 error = 1.00441013278%
```

So the practical accepted boundary for this problem was approximately:

```text
37.3% accepted < boundary < 37.4% rejected
```

## 5. Difference Between This Work and Nesnas-Saanouni

| Topic | Nesnas-Saanouni scheme | This work |
|---|---|---|
| Main purpose | General cycle-jump integration for coupled damage-viscoplastic models | Abaqus/UMAT demonstration and validation for a Chaboche-type viscoplastic material |
| Time-scale structure | Formal two-time-scale method: implicit within cycle, explicit over cycles | Practical FE workflow: explicit reference cycles, extrapolate selected state, reinject into Abaqus |
| State variables | Restores a limited but sufficient variable set representing all relevant state evolution | Began with scalar `STATEV1`; later injected all 15 `STATEV` entries plus stress for consistency |
| Damage | Includes coupled damage-viscoplasticity in the target methodology | No damage variable in the active UMAT |
| Constitutive integration | Built around constitutive integration strategy | Uses Abaqus/Standard plus a user UMAT; cycle jump is orchestrated externally by scripts |
| Jump control | Based on evolution of internal variables over cycles | Based mainly on `STATEV1` error and reference validation; later percentage sweeps bracketed the practical limit |
| Reinitialization | Material-state restoration is part of the cycle-jump algorithm | Reinitialization performed through Abaqus `SDVINI` and `SIGINI` |
| Validation | Gauss-point and structural examples in the paper | Single-element Abaqus validation against no-skip references at 20, 50, 100, 500, and 1000 cycles |

The important scientific distinction is this: Nesnas-Saanouni is a general material-state cycle-jump framework. This work is a staged implementation study showing how a predicted state can be injected into Abaqus for a specific UMAT and validated against explicit references.

## 6. UMAT Used in This Work

The active UMAT inspected in the repository is:

```text
runs/chaboche_umat/umat/chaboche_vp_v1_working.f
```

It is a simplified Chaboche-type unified viscoplastic UMAT with:

- isotropic elasticity;
- von Mises-type overstress;
- isotropic hardening through accumulated viscoplastic strain;
- nonlinear kinematic hardening using backstress components;
- Perzyna-type rate dependence;
- 15 solution-dependent state variables.

The material parameters are read as:

```text
PROPS(1) = E
PROPS(2) = NU
PROPS(3) = SIGY
PROPS(4) = QISO
PROPS(5) = BISO
PROPS(6) = CKIN
PROPS(7) = GKIN
PROPS(8) = KVIS
PROPS(9) = MVIS
```

The yield/overstress measure is:

```text
F = q_eq - SIGY - RISO
```

where `q_eq` is computed from the deviatoric trial stress minus the backstress. The isotropic hardening variable is:

```text
RISO = QISO * (1 - exp(-BISO * STATEV(1)))
```

The viscoplastic increment is limited by:

```text
DP = min(DPALG, DPRATE, DPMAX)
```

with:

```text
DPALG  = F / HARD
DPRATE = DTIME * (F / KVIS)^MVIS
DPMAX  = 1.0e-3
```

The active `STATEV` layout is:

| STATEV | Meaning |
|---:|---|
| 1 | accumulated viscoplastic strain `p` |
| 2-7 | backstress tensor components `X11, X22, X33, X12, X13, X23` |
| 8-13 | viscoplastic strain tensor components `Evp11, Evp22, Evp33, Evp12, Evp13, Evp23` |
| 14 | isotropic hardening stress `RISO`, recomputable from `STATEV1` |
| 15 | last viscoplastic multiplier increment `DP`, diagnostic |

### Open-source status of the UMAT

No open-source URL, license header, GitHub link, or external provenance was found in the local UMAT file. Based on the repository evidence, the UMAT should be treated as a local/custom research implementation, not as a directly copied open-source UMAT.

Open references useful for context, but not identified as the source of this UMAT, include:

- Nesnas and Saanouni cycle-jump paper: https://doi.org/10.1080/12506559.2000.10511493
- Open-access cyclic elastoplasticity FE implementation overview: https://link.springer.com/article/10.1007/s00707-021-03069-3

## 7. State Transfer, Reinitialization, and Reinjection

The reinjection workflow used two Abaqus user initialization mechanisms:

- `SDVINI` for solution-dependent state variables;
- `SIGINI` for initial stress.

The user wrote "SIGNI"; in Abaqus terminology and in the repository files, the subroutine used is `SIGINI`.

### 7.1 Why SDVINI Alone Was Not Enough

An early STATEV-only continuation was used as a control/check run. It completed, but it did not reproduce the intended cycle-19 accumulated state. The report states that the original input deck omitted:

```text
*INITIAL CONDITIONS, TYPE=SOLUTION, USER
```

That run therefore behaved close to a fresh one-cycle result and was not considered a valid injected continuation.

### 7.2 Corrected SDVINI + SIGINI Branch

The corrected branch activated:

```text
*INITIAL CONDITIONS, TYPE=SOLUTION, USER
*INITIAL CONDITIONS, TYPE=STRESS, USER
```

The successful exact-state SIGINI result showed:

```text
Expected injected STATEV1 = 0.13485494256
First-frame STATEV1       = 0.13485494256
First-frame STATEV1 error = 0

Expected initial S11      = 335.576873779 MPa
First-frame S11           = 335.576873779 MPa
First-frame S11 error     = 0
```

This confirmed that both material memory and residual stress were being imposed at the beginning of the continuation simulation.

### 7.3 Predicted-State Injection Verification

For the predicted cycle-19 to cycle-20 jump:

```text
Expected injected STATEV1 = 0.134935969953
First-frame STATEV1       = 0.134935975075
First-frame error         = 5.12176806522e-09

Expected injected S11     = 339.014099121 MPa
First-frame S11 error     = 9.37347977015e-11 MPa
```

For the cycle-49 to cycle-50 jump:

```text
Expected injected STATEV1 = 0.350499925669
First-frame error         = 2.32824909352e-09

Expected injected S11     = 348.668233236 MPa
First-frame error         = 1.01722257e-05 MPa
```

For the cycle-99 to cycle-100 jump:

```text
First-frame STATEV1 absolute error = 2.32838248682e-09
First-frame S11 absolute error     = 3.3911667856e-06 MPa
```

These first-frame checks are the key evidence that the simulation starts from the intended injected material state.

## 8. What About the Displacement Field?

The displacement field was not transferred from a previous Abaqus ODB as a full nodal displacement initial condition. Instead, the continuation problem was formulated so that the imposed boundary displacement at the first continuation frame corresponded to the intended point of the loading cycle.

This is acceptable for the present single-element, prescribed-displacement test because:

- the geometry is simple;
- the loading is displacement controlled;
- the relevant path memory is stored mainly in `STATEV` and residual stress;
- the right-face displacement boundary condition can be restarted at the intended cycle phase;
- the first-frame output verifies the mechanical state through stress and reaction force checks.

The reports consistently inspected the `RIGHT_FACE` boundary output. For example:

```text
RIGHT_FACE average U1 = 0
RIGHT_FACE summed RF1 = reported for each continuation
```

This means the restart point was at the zero-displacement cycle phase for the tested continuations. The internal memory and residual stress carried the cyclic history; the displacement boundary condition supplied the continuation kinematics.

For a more general structure, especially with nonuniform deformation, contact, crack growth, or a large displacement field, this would not be sufficient. A full restart-like method would need a mechanically compatible displacement/strain field, not only `STATEV` and stress. In the present single-element benchmark, the displacement field issue is controlled by the simple prescribed-displacement setup and by first-frame state verification.

## 9. Acceptance Criteria

The working acceptance rule became:

```text
accepted_clean_success:
    STATEV1 error <= 1%
    S11 error     <= 1%
    RF1 error     <= 1%

accepted_exploratory_success:
    STATEV1 error <= 1%
    but S11 or RF1 > 1%

not_accepted:
    STATEV1 error > 1%
```

The main scientific reason for using `STATEV1` as the controlling metric is that it is accumulated viscoplastic strain and therefore stores irreversible history. Stress and reaction force can recover during subsequent continuation, but accumulated state error persists and controls long-horizon validity.

## 10. Successfully Completed Simulations and Results

The following completed items are included. The partial 4380-cycle run and current 2000-cycle Stage 14 work are excluded.

| Stage / case | Status | Route / purpose | Key result |
|---|---|---|---|
| 1-cycle smoke / validation | completed | UMAT compile and basic Abaqus run | UMAT compiled, linked, and ran |
| 10-cycle baseline | completed | explicit baseline at +/-0.5% strain | stable `Delta_STATEV1`; mean cycles 2-10 = 0.007185465191 |
| 20-cycle explicit validation | completed | no-skip reference and scalar prediction check | predicted cycle-20 `STATEV1` error = 0.06741093536% |
| 50-cycle reference | completed | longer no-skip reference | used for cycle-28, cycle-30, cycle-40, and cycle-50 comparisons |
| Stage 4 STATEV-only control | completed but not valid as injection | checked missing solution initialization | not interpreted as successful injected continuation |
| Stage 4 SDVINI + SIGINI exact-state injection | completed | exact cycle-19 state to cycle 20 | first-frame `STATEV1` and `S11` matched injected values exactly/within tolerance |
| Stage 5B predicted cycle-19 to cycle-20 jump | completed | cycle 10 -> predicted 19 -> 20 | `STATEV1` error = 0.049427232695%, `S11` error = 0.127012627651%; successful by 1% criteria |
| Stage 6D predicted cycle-29 to cycle-30 jump | completed | skips cycles 11-28 | `STATEV1` error = 0.0458269043313%; exploratory success because `S11` error = 2.34365652874% |
| Stage 7C predicted cycle-27 to cycle-28 adaptive jump | completed | grouped adaptive recommendation | `STATEV1` error = 0.0231584782019%; accepted exploratory success |
| Stage 9B predicted cycle-49 to cycle-50 jump | completed | skips cycles 11-48 | `STATEV1` error = 0.253071065812%, `S11` error = 0.0522291978811%; accepted clean success |
| Stage 10A 100-cycle no-skip reference | completed | explicit reference | cycle-100 `STATEV1` = 0.712048649788 |
| Stage 10B predicted cycle-99 to cycle-100 jump | completed | skips 88 intermediate FE cycles | `STATEV1` error = 0.667869616047%, `S11` error = 0.0713767788476%; accepted clean success |
| Stage 11A 500-cycle no-skip reference | completed | explicit reference | cycle-500 `STATEV1` = 3.463043212890625 |
| Stage 11B predicted cycle-499 to cycle-500 limit test | completed but not accepted | skips 488 intermediate FE cycles | stable run, but `STATEV1` error = 3.69823703261%; not accepted |
| Stage 12A 1000-cycle no-skip reference | completed | explicit reference | cycle-1000 `STATEV1` = 6.7042798996 |
| Stage 12 percentage sweep | completed | 35%, 40%, 50% jumps to cycle 1000 | 35% accepted; 40% and 50% rejected by `STATEV1` |
| Stage 12 refinement | completed | target cycles 371-379 | target 373 accepted; target 374 rejected |

## 11. Main Scientific Conclusions

1. The Chaboche UMAT response at +/-0.5% strain develops a stable accumulated viscoplastic strain increment after the first few cycles.

2. A simple first-order cycle-space extrapolation of `STATEV1` predicted the 20-cycle explicit result with very small error.

3. Abaqus continuation from a jumped state is possible when both material state and residual stress are initialized:

```text
STATEV -> SDVINI
stress -> SIGINI
```

4. First-frame checks are essential. The injected state is only trusted when the first output frame reproduces the expected `STATEV1` and `S11`.

5. For this single-element displacement-controlled benchmark, the full displacement field was not separately transferred. The continuation phase was controlled by the imposed boundary displacement, while history was carried by `STATEV` and stress.

6. Stress and reaction force often recover during the continuation cycle, even from a poor injected stress prediction. Accumulated viscoplastic strain does not recover as easily and is the controlling accuracy measure.

7. The largest accepted one-cycle continuation jump so far was Stage 10B:

```text
cycle 10 -> predicted cycle 99 -> cycle 100
skipped intermediate FE cycles = 88
final STATEV1 error = 0.667869616047%
```

8. The 500-cycle extreme limit test completed numerically but was rejected:

```text
cycle 10 -> predicted cycle 499 -> cycle 500
STATEV1 error = 3.69823703261%
```

9. The best accepted 1000-cycle percentage jump was:

```text
cycle 10 -> predicted cycle 373 -> continue to cycle 1000
skipped intermediate FE cycles = 362
final STATEV1 error = 0.998969124476%
```

10. Compared with Nesnas-Saanouni, this work is a practical Abaqus/UMAT implementation study rather than a complete general cycle-jump constitutive framework. Its strength is the staged verification of predicted-state reinjection against explicit Abaqus references.

## 12. Files Used as Evidence

Key local evidence files include:

```text
runs/chaboche_umat/umat/chaboche_vp_v1_working.f
runs/chaboche_umat/CHABOCHE_CYCLE_JUMP_20CYCLE_VALIDATION_REPORT.md
runs/chaboche_umat/NESNAS_SDV1_CYCLE_JUMP_ANALYZER_REPORT.md
runs/chaboche_umat/CHABOCHE_V1_STATEV_INVENTORY_REPORT.md
runs/chaboche_umat/stage4_injected_cycle_jump/STAGE4B_SIGINI_RESULT_REPORT.md
runs/chaboche_umat/stage5_predicted_cycle_jump/STAGE5B_PREDICTED_CYCLE_JUMP_RESULT_REPORT.md
runs/chaboche_umat/stage6_cycle29_jump/STAGE6D_PREDICTED_CYCLE29_JUMP_RESULT_REPORT.md
runs/chaboche_umat/stage7c_cycle27_validation/STAGE7C_PREDICTED_CYCLE27_JUMP_RESULT_REPORT.md
runs/chaboche_umat/stage9_longer_jump_error_accumulation/target49_cycle50/STAGE9B_PREDICTED_CYCLE49_JUMP_RESULT_REPORT.md
runs/chaboche_umat/stage10_100cycle_reference/STAGE10_100CYCLE_REFERENCE_AND_JUMP_SUMMARY.md
runs/chaboche_umat/stage11_500cycle_reference/STAGE11_500CYCLE_REFERENCE_AND_LIMIT_TEST_SUMMARY.md
runs/chaboche_umat/stage12_percentage_jump_1000cycles/STAGE12_FINAL_PERCENTAGE_BOUNDARY_INTERPRETATION.md
```

## 13. External References

- K. Nesnas and K. Saanouni, "A cycle jumping scheme for numerical integration of coupled damage and viscoplastic models for cyclic loading paths," Revue Europeenne des Elements Finis, 9(8), 865-891, 2000. DOI: https://doi.org/10.1080/12506559.2000.10511493
- C. Suchocki, "On finite element implementation of cyclic elastoplasticity: theory, coding, and exemplary problems," Acta Mechanica, 233, 83-120, 2022. Open access: https://link.springer.com/article/10.1007/s00707-021-03069-3
- Stage-specific local reports listed above.
