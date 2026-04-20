# Cycle‑Jump Strategies in Abaqus/CAE 2021 — What We Did (Linear‑Elastic → Elastic‑Plastic)

This note documents the end‑to‑end workflow we built in Abaqus/CAE 2021 to demonstrate **cycle‑jump** ideas with **small, runnable scripts**, starting from a **1‑cycle ODB** and moving toward **elastic‑plastic (history‑dependent) cycle‑jump logic**.

> Scope: demonstration + scaffolding. For real fatigue life prediction you must use *material‑calibrated* S–N / damage parameters (or a validated EP/VP constitutive model).

---

## 1) Goal and core idea

A fatigue simulation may require **very many cycles**. Cycle‑jump (cycle skipping) accelerates this by:

1. computing a few **training cycles**,
2. estimating how slow variables evolve with cycle number \(N\),
3. **jumping** a block of cycles \(\Delta N\),
4. re‑equilibrating / verifying with a **trial cycle**, and
5. adapting \(\Delta N\) until acceptable.

Two important cases:

- **Linear elastic** (no constitutive memory): stresses repeat each cycle; cycle‑jump is about *damage accumulation* / *crack growth* outside elasticity.
- **Elastic‑plastic / viscoplastic**: response depends on internal state \(\mathbf{q}\) (plastic strain, hardening, etc.), so cycle‑jump must update those **internal variables**.

---

## 2) Linear‑Elastic: One‑cycle ODB → Stress range extraction

### 2.1 Model used
We created a tiny 3D block model, applied a **cyclic displacement** over a single step (time period 1.0), and ran one analysis job. The analysis produced an **ODB** file:

- `one-cycle.odb`

### 2.2 Script: stress range from the ODB (whole model, no sets)
**Purpose:** compute per‑frame min/max and global \(\Delta\sigma = \sigma_{max} - \sigma_{min}\) for a chosen component (we used `S11`) over the entire cycle.

**Key implementation note:** Abaqus/CAE’s console can fail on Unicode output, so we used ASCII output and wrote CSV to disk. (We also fixed the CSV writing for Python 3 using `newline=""`.)

Result used later (from the Miner script output):

- `stress_range = 1.352911e+03`

(Units are whatever your model uses; typically MPa if you used a consistent mm‑N‑MPa system.)

---

## 3) Linear‑Elastic cycle‑jump technique #1: Miner block update (Basquin S–N)

### 3.1 Theory (minimal)
For a constant amplitude block of \(\Delta N\) cycles:

- compute stress amplitude: \(\sigma_a = \Delta\sigma/2\)
- estimate fatigue life from Basquin:
\[
\sigma_a = \sigma_f' (2N_f)^b
\]
- Miner damage increment:
\[
\Delta D = \frac{\Delta N}{N_f}
\]

### 3.2 Script: `step2_miner_block_noprint.py` (file output, no console prints)
We used demo parameters (you must calibrate for real materials):

- `sigma_f_prime = 1.0e4`
- `b = -0.10`
- `DeltaN = 1000`

**Results (written to `miner_block_results.txt`):**
```text
Miner + Basquin block update (linear elastic)
stress_range = 1.352911e+03
sigma_a = 6.764555e+02
sigma_a_eq = 6.764555e+02
sigma_f_prime = 1.000000e+04
b = -0.100000
Nf = 2.492170e+11
DeltaN = 1000
dD = 4.012567e-09
```

Interpretation:

- The estimated life is huge because the Basquin constants are placeholders.
- The block damage for 1000 cycles is small (order \(10^{-9}\)).

---

## 4) Linear‑Elastic cycle‑jump technique #2: Variable‑amplitude spectrum block (Miner)

### 4.1 Theory
For multiple blocks \(i\) with different ranges and counts:
\[
D_{total} = \sum_i \frac{n_i}{N_{f,i}}
\]

### 4.2 Script: `step3_linear_elastic_variable_blocks_noprint.py`
We provided a list of blocks:

- \((\Delta\sigma=1.352911e3, n=1000)\)
- \((\Delta\sigma=1.0e3, n=2000)\)
- \((\Delta\sigma=8.0e2, n=5000)\)

**Results (written to `miner_variable_blocks_results.txt`):**
```text
Variable-amplitude Miner + Basquin (linear elastic)
cwd = D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run
sigma_f_prime = 1.000000e+04
b = -0.100000
use_goodman = False

Blocks: (stress_range, cycles, Nf, dD)
1.352911e+03  1000  2.492170e+11  4.012567e-09
1.000000e+03  2000  5.120000e+12  3.906250e-10
8.000000e+02  5000  4.768372e+13  1.048576e-10

Total damage D = 4.508050e-09
```

---

## 5) Elastic‑Plastic: why cycle‑jump is harder (history variables)

### 5.1 Internal variables (what must be “jumped”)
For EP models, the constitutive response depends on internal state \(\mathbf{q}\), e.g.

- plastic strain \(arepsilon^p\),
- hardening variables (isotropic \(R\), kinematic backstress \(lpha\)),
- accumulated plastic strain \(ararepsilon^p_{acc}\),
- damage variables \(D\) (if present).

Cycle‑jump must update these internal variables across \(\Delta N\) cycles — not just a Miner counter.

---

## 6) Elastic‑Plastic technique #1 (demo): naive cycle‑end extrapolation

### 6.1 What we implemented
A small **1D return‑mapping** EP material point model with isotropic hardening:

- \(E = 70000\) MPa
- \(\sigma_{y0}=250\) MPa
- \(H = 1000\) MPa
- strain‑controlled fully reversed cycle with amplitude `eps_a = 0.01`

We simulated a few training cycles, then did a **1st‑order jump** using end‑of‑cycle increments of \(arepsilon^p\) and \(R\).

**Output (from `ep_cycle_jump_demo.txt`):**
```text
Elastic-plastic cycle-jump demo (1D isotropic hardening)
E = 7.000000e+04 MPa, sig_y0 = 2.500000e+02 MPa, H = 1.000000e+03 MPa
eps_a = 1.000000e-02, nTrainCycles = 3, DeltaN = 1000

Cycle end states (sig, eps_p, R):
N=1  sig=2.711219e+02  eps_p=-3.873170e-03  R=2.112187e+01
N=2  sig=2.943961e+02  eps_p=-4.205658e-03  R=4.439609e+01
N=3  sig=3.163775e+02  eps_p=-4.519679e-03  R=6.637754e+01

Estimated per-cycle increments (from last two cycles):
deps_p_per_cycle = -3.140208e-04
dR_per_cycle     = 2.198146e+01

Jumped state after DeltaN cycles (1st-order):
eps_p_jump = -3.185405e-01
R_jump     = 2.204784e+04
```

### 6.2 Key lesson
The naive jump predicts a massive hardening increase (`R_jump ~ 2.2e4 MPa`) because the model is still in **transient cyclic hardening** and end‑of‑cycle rates are not stable.

---

## 7) Elastic‑Plastic technique #2: quadratic extrapolation + trial‑cycle accept/reject + caps

### 7.1 What we tried
- Quadratic (2nd order) extrapolation using last 3 cycle endpoints
- Cap total changes per jump (limits on total \(\Delta R\) and \(\Deltaarepsilon^p\))
- Trial cycle starting from the jumped state
- Accept only if trial‑cycle “rate” matches last‑cycle rate within tolerance

**Output (from `ep_cycle_jump_adaptive.txt`):**
```text
EP cycle-jump (1D iso hardening): quadratic + trial accept/reject + caps
E=7.000000e+04, sig_y0=2.500000e+02, H=1.000000e+03
eps_a=1.000000e-02, nTrainCycles=4
Initial proposal DeltaN_try=1000, tol_rate=0.200
Caps: dR_cap_total=2.000000e+02, deps_p_cap_total=5.000000e-03

Last-cycle rates (from training):
depsp_1=-2.965787e-04, dR_1=2.076051e+01
depsp_2=1.744214e-05, dR_2=-1.220950e+00

Attempts (DeltaN, epsp_jump, R_jump, depsp_trial, dR_trial, err_epsp, err_R):
9  -6.779059e-03  2.245342e+02  3.785727e-03  1.593258e+01  1.376466e+01  2.325534e-01
4  -5.863036e-03  1.604125e+02  1.979483e-03  1.773883e+01  7.674393e+00  1.455495e-01
2  -5.374531e-03  1.262172e+02  1.016235e-03  1.870208e+01  4.426526e+00  9.915139e-02
1  -5.104116e-03  1.072881e+02  4.830209e-04  1.923529e+01  2.628643e+00  7.346736e-02

ACCEPTED = False
Final DeltaN = 1
```

### 7.2 Key lesson
Even after shrinking the proposed jump, it did **not** accept (ended effectively at \(\Delta N=1\)) because:

- end‑of‑cycle \(arepsilon^p\) is **not monotone** in fully reversed plasticity, and
- the cyclic response was still evolving, so “rate consistency” checks fail.

---

## 8) Elastic‑Plastic technique #3: use a monotone slow variable (accumulated plastic strain)

### 8.1 Why
A standard robust trick is to control jumps using a **monotone** measure such as:

- accumulated plastic strain per cycle \(\Deltaararepsilon^p_{acc} \ge 0\), or
- plastic dissipation per cycle \(\Delta W_p \ge 0\).

### 8.2 What we implemented
We switched the acceptance logic to use per‑cycle accumulated plastic increment `dEpbar` (sum of absolute plastic multipliers) as the slow variable.

**Output (from `ep_cycle_jump_accumulated.txt`):**
```text
EP cycle-jump using accumulated plastic strain (monotone)
E=7.000000e+04, sig_y0=2.500000e+02, H=1.000000e+03
eps_a=1.000000e-02, nTrainCycles=4
DeltaN_try=200, tol_rate=0.200
Caps: dEpbar_cap_total=1.000000e-02, dR_cap_total=2.000000e+02

Training per-cycle dEpbar:
N=1  dEpbar=2.112187e-02
N=2  dEpbar=2.327421e-02
N=3  dEpbar=2.198146e-02
N=4  dEpbar=2.076051e-02

Attempts: DeltaN  dEpbar_last  dEpbar_pred  dEpbar_trial  err  R_pred
1  2.076051e-02  1.957546e-02  1.895948e-02  8.675262e-02  1.072881e+02

ACCEPTED = True
Final DeltaN = 1
```

### 8.3 Key lesson
The scheme became well‑posed (monotone variable) and the trial check passed, but the final accepted jump was still **\(\Delta N=1\)** because the training cycles are not stabilized and the caps/tolerance are conservative.

---

## 9) What to do next (recommended, practical)

For **real** EP/VP cycle‑jump in Abaqus:

1. **Stabilize first** (or use stabilized-cycle methods)  
   - For LCF stabilized loops, Abaqus/Standard has *Direct Cyclic*; it can be better than manual skipping.

2. Track **monotone** progress variables for jump control  
   - accumulated plastic strain, dissipation, damage, crack length, etc.

3. Use **adaptive \(\Delta N\)** + trial cycle acceptance  
   - start small; grow \(\Delta N\) only when the evolution rate becomes smooth/stable.

4. For viscoplasticity, prefer **cycle‑averaged evolution** or **implicit (cycle‑domain) stepping** because rate effects can be stiff.

---

## Appendix: Scripts we created (conceptual list)
- ODB → stress range:
  - `step1_extract_stress_range_NOSET_FIXEDCSV.py`
- Linear elastic Miner block jump:
  - `step2_miner_block_noprint.py` → `miner_block_results.txt`
- Linear elastic variable‑amplitude Miner:
  - `step3_linear_elastic_variable_blocks_noprint.py` → `miner_variable_blocks_results.txt`
- Elastic‑plastic demo (material-point):
  - `step_ep1_1D_ep_cycle_jump_demo.py` → `ep_cycle_jump_demo.txt`
  - `step_ep2_adaptive_cycle_jump_ep_1D.py` → `ep_cycle_jump_adaptive.txt`
  - `step_ep3_cycle_jump_accumulated_ep_1D.py` → `ep_cycle_jump_accumulated.txt`

  ---

  ## 10) Benchmark note for the 2-cycle hysteresis comparison

  The 2-cycle hysteresis comparison shows a clear progression from the linear kinematic model to the combined hardening model. The linear kinematic case produces a stable, nearly repeating symmetric loop in the second cycle, which is consistent with the expected benchmark response and indicates no ratcheting. The first combined-hardening trial produces a much wider and stronger loop, with substantially higher reaction-force levels, showing that the chosen combined-hardening parameters were too aggressive for a like-for-like comparison.

  After tuning the combined-hardening parameters, the hysteresis loop moves closer to the linear kinematic reference while still remaining distinctly stronger and more rounded. This tuned response is more suitable for benchmark comparison because it preserves the qualitative effect of combined hardening without excessively overpredicting the force level. Therefore, the tuned combined-hardening case is the most appropriate version to carry forward for further discussion, plotting, and thesis interpretation.

## Built ratcheting-style combined-hardening deck

### Objective
- prepare the next Phase 3 benchmark by creating a ratcheting-style loading case from the asymmetric combined-hardening deck

### Files created or modified
- combined_ratcheting_2cycle.inp

### Commands run
```powershell
Set-Location 'D:\TUBAF\Master_Thesis\Abaqus_trial'
Copy-Item 'combined_asym_2cycle.inp' 'combined_ratcheting_2cycle.inp' -Force
Get-Content 'combined_ratcheting_2cycle.inp' | Select-String -Pattern '^\*Amplitude','^\*Step','^\*Boundary'
```

### Key results

| Quantity                      |                          Value |
| ----------------------------- | -----------------------------: |
| Base deck copied from         |       combined_asym_2cycle.inp |
| New deck                      | combined_ratcheting_2cycle.inp |
| Planned amplitude max         |                           1.00 |
| Planned amplitude minimum     |                          -0.20 |
| Planned amplitude final value |                           0.40 |

### Interpretation

* the ratcheting-style case is being built from the asymmetric benchmark because it already has a non-zero mean load history
* the new target loading increases the positive mean further and should help reveal progressive shift / residual strain behavior more clearly than the previous asymmetric case

### Next step

* edit the amplitude block in combined_ratcheting_2cycle.inp and run an Abaqus datacheck
