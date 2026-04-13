# step_ep2_adaptive_cycle_jump_ep_1D.py
# Elastic-plastic cycle-jump technique: quadratic extrapolation + trial-cycle accept/reject + caps.
# Writes ep_cycle_jump_adaptive.txt in current working directory. No prints.

import os, math

# -----------------------
# Material (1D) settings
# -----------------------
E  = 70000.0      # MPa
sig_y0 = 250.0    # MPa
H  = 1000.0       # MPa isotropic hardening modulus

# -----------------------
# Loading per cycle (strain-controlled)
# -----------------------
eps_a = 0.010
nStepsPerCycle = 40

# -----------------------
# Training cycles
# -----------------------
nTrainCycles = 4     # need >=3 for quadratic derivatives (use 4 for safety)

# -----------------------
# Jump control knobs (EDIT THESE)
# -----------------------
DeltaN_try   = 1000   # starting proposal
DeltaN_min   = 1      # smallest allowed
tol_rate     = 0.20   # accept if trial-cycle rate change <= 20%

# Caps: do not allow the jump to change state too much in one go
dR_cap_total     = 200.0    # MPa max increase of R per jump
deps_p_cap_total = 0.005    # max change of eps_p per jump (absolute)

# -----------------------
# State variables
# -----------------------
eps_p = 0.0
R = 0.0
sig = 0.0

def return_map_1D(eps_total, eps_p, R):
    sig_trial = E * (eps_total - eps_p)
    f = abs(sig_trial) - (sig_y0 + R)
    if f <= 0.0:
        return sig_trial, eps_p, R
    dgamma = f / (E + H)
    sgn = 1.0 if sig_trial >= 0.0 else -1.0
    eps_p_new = eps_p + dgamma * sgn
    R_new = R + H * dgamma
    sig_new = E * (eps_total - eps_p_new)
    return sig_new, eps_p_new, R_new

def one_cycle_strain_path(eps_a, nSteps):
    pts = [0.0, eps_a, 0.0, -eps_a, 0.0]
    path = []
    segN = max(1, nSteps // 4)
    for i in range(4):
        a = pts[i]; b = pts[i+1]
        for k in range(segN):
            t = float(k) / float(segN)
            path.append(a + (b-a)*t)
    path.append(0.0)
    return path

def run_one_cycle(eps_p, R):
    sig = 0.0
    for eps in one_cycle_strain_path(eps_a, nStepsPerCycle):
        sig, eps_p, R = return_map_1D(eps, eps_p, R)
    return sig, eps_p, R

# ---- Training: simulate nTrainCycles and store end-of-cycle states
cycle_end = []  # list of (sig, eps_p, R)
for c in range(1, nTrainCycles+1):
    sig, eps_p, R = run_one_cycle(eps_p, R)
    cycle_end.append((sig, eps_p, R))

# Use last 3 endpoints for quadratic derivatives wrt cycle number
(sigNm2, epspNm2, RNm2) = cycle_end[-3]
(sigNm1, epspNm1, RNm1) = cycle_end[-2]
(sigN,   epspN,   RN)   = cycle_end[-1]

# First and second differences (per cycle)
depsp_1 = epspN - epspNm1
dR_1    = RN    - RNm1

depsp_2 = epspN - 2.0*epspNm1 + epspNm2
dR_2    = RN    - 2.0*RNm1    + RNm2

# ---- Propose DeltaN with caps
DeltaN = int(DeltaN_try)

# cap by total allowed change (avoid huge jumps)
if abs(dR_1) > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dR_cap_total / abs(dR_1)))))
if abs(depsp_1) > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(deps_p_cap_total / abs(depsp_1)))))

# ---- Adaptive accept/reject using a trial cycle
accepted = False
history = []

while True:
    if DeltaN < DeltaN_min:
        DeltaN = DeltaN_min

    # Quadratic extrapolation: q(N+DN) = qN + DN*q' + 0.5*DN^2*q''
    epsp_jump = epspN + DeltaN*depsp_1 + 0.5*(DeltaN**2)*depsp_2
    R_jump    = RN    + DeltaN*dR_1    + 0.5*(DeltaN**2)*dR_2

    # Trial: run exactly 1 cycle starting from jumped state, measure per-cycle increments there
    sig_t, epsp_t, R_t = run_one_cycle(epsp_jump, R_jump)
    depsp_trial = epsp_t - epsp_jump
    dR_trial    = R_t    - R_jump

    # Compare trial-cycle rates to the last observed rates (depsp_1, dR_1)
    # Accept if relative change is small
    def rel_change(a, b):
        denom = max(1.0e-14, abs(a))
        return abs(b - a) / denom

    err_epsp = rel_change(depsp_1, depsp_trial)
    err_R    = rel_change(dR_1, dR_trial)

    history.append((DeltaN, epsp_jump, R_jump, depsp_trial, dR_trial, err_epsp, err_R))

    if (err_epsp <= tol_rate) and (err_R <= tol_rate):
        accepted = True
        break

    # reject -> reduce jump
    if DeltaN <= DeltaN_min:
        break
    DeltaN = max(DeltaN_min, DeltaN // 2)

# ---- Write results
outPath = os.path.join(os.getcwd(), "ep_cycle_jump_adaptive.txt")
f = open(outPath, "w")
f.write("EP cycle-jump (1D iso hardening): quadratic + trial accept/reject + caps\n")
f.write("E=%.6e, sig_y0=%.6e, H=%.6e\n" % (E, sig_y0, H))
f.write("eps_a=%.6e, nTrainCycles=%d\n" % (eps_a, nTrainCycles))
f.write("Initial proposal DeltaN_try=%d, tol_rate=%.3f\n" % (DeltaN_try, tol_rate))
f.write("Caps: dR_cap_total=%.6e, deps_p_cap_total=%.6e\n" % (dR_cap_total, deps_p_cap_total))

f.write("\nLast-cycle rates (from training):\n")
f.write("depsp_1=%.6e, dR_1=%.6e\n" % (depsp_1, dR_1))
f.write("depsp_2=%.6e, dR_2=%.6e\n" % (depsp_2, dR_2))

f.write("\nAttempts (DeltaN, epsp_jump, R_jump, depsp_trial, dR_trial, err_epsp, err_R):\n")
for h in history:
    f.write("%d  %.6e  %.6e  %.6e  %.6e  %.6e  %.6e\n" % h)

f.write("\nACCEPTED = %s\n" % str(accepted))
f.write("Final DeltaN = %d\n" % DeltaN)
if accepted:
    f.write("Final jumped state: epsp_jump=%.6e, R_jump=%.6e\n" % (history[-1][1], history[-1][2]))
f.close()
