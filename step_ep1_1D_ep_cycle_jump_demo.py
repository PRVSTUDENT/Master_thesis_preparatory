# step_ep1_1D_ep_cycle_jump_demo.py
# Elastic-plastic cycle-jump demo (1D, isotropic hardening).
# Shows: run "training" cycles -> estimate per-cycle increments -> jump DeltaN cycles.
# No prints; writes ep_cycle_jump_demo.txt

import os, math

# -----------------------
# Material (1D) settings
# -----------------------
E  = 70000.0      # MPa
sig_y0 = 250.0    # MPa initial yield
H  = 1000.0       # MPa isotropic hardening modulus

# -----------------------
# Loading per cycle (strain-controlled, fully reversed)
# We simulate a few cycles explicitly with a simple return mapping.
# -----------------------
eps_a = 0.010     # strain amplitude (EDIT)
nStepsPerCycle = 40  # resolution inside one cycle for the "training" simulation

# -----------------------
# Cycle jump controls
# -----------------------
nTrainCycles = 3   # fully simulate these
DeltaN = 1000      # jump size (cycles)

# -----------------------
# State variables (material point)
# -----------------------
eps_p = 0.0     # plastic strain
R = 0.0         # isotropic hardening variable (scalar)
sig = 0.0       # stress

def return_map_1D(eps_total, eps_p, R):
    """1D elastoplastic with isotropic hardening: sigma = E*(eps - eps_p)
       Yield: |sigma| - (sig_y0 + R) <= 0
       Flow: d eps_p = dgamma * sign(sigma_trial)
       Hardening: dR = H * dgamma
    """
    sig_trial = E * (eps_total - eps_p)
    f = abs(sig_trial) - (sig_y0 + R)
    if f <= 0.0:
        return sig_trial, eps_p, R, 0.0  # elastic step
    # plastic correction
    dgamma = f / (E + H)
    sgn = 1.0 if sig_trial >= 0.0 else -1.0
    eps_p_new = eps_p + dgamma * sgn
    R_new = R + H * dgamma
    sig_new = E * (eps_total - eps_p_new)
    return sig_new, eps_p_new, R_new, dgamma

def one_cycle_strain_path(eps_a, nSteps):
    """Triangle-ish path: 0 -> +eps_a -> 0 -> -eps_a -> 0"""
    pts = [0.0, eps_a, 0.0, -eps_a, 0.0]
    # piecewise linear interpolation
    path = []
    segN = nSteps // 4
    for i in range(4):
        a = pts[i]; b = pts[i+1]
        for k in range(segN):
            t = float(k)/float(segN)
            path.append(a + (b-a)*t)
    path.append(0.0)
    return path

# ---- Training: simulate nTrainCycles fully and record end-of-cycle states
cycle_end = []  # list of (sig, eps_p, R)
for c in range(1, nTrainCycles+1):
    for eps in one_cycle_strain_path(eps_a, nStepsPerCycle):
        sig, eps_p, R, dgam = return_map_1D(eps, eps_p, R)
    cycle_end.append((sig, eps_p, R))

# Need at least 2 cycle endpoints for first-order jump
(sigN, epspN, RN) = cycle_end[-1]
(sigNm1, epspNm1, RNm1) = cycle_end[-2]

depsp_per_cycle = epspN - epspNm1
dR_per_cycle    = RN - RNm1

# ---- Cycle jump (1st-order)
epsp_jump = epspN + DeltaN * depsp_per_cycle
R_jump    = RN    + DeltaN * dR_per_cycle

# ---- Write results
outPath = os.path.join(os.getcwd(), "ep_cycle_jump_demo.txt")
f = open(outPath, "w")
f.write("Elastic-plastic cycle-jump demo (1D isotropic hardening)\n")
f.write("E = %.6e MPa, sig_y0 = %.6e MPa, H = %.6e MPa\n" % (E, sig_y0, H))
f.write("eps_a = %.6e, nTrainCycles = %d, DeltaN = %d\n" % (eps_a, nTrainCycles, DeltaN))
f.write("\nCycle end states (sig, eps_p, R):\n")
for i, st in enumerate(cycle_end):
    f.write("N=%d  sig=%.6e  eps_p=%.6e  R=%.6e\n" % (i+1, st[0], st[1], st[2]))
f.write("\nEstimated per-cycle increments (from last two cycles):\n")
f.write("deps_p_per_cycle = %.6e\n" % depsp_per_cycle)
f.write("dR_per_cycle     = %.6e\n" % dR_per_cycle)
f.write("\nJumped state after DeltaN cycles (1st-order):\n")
f.write("eps_p_jump = %.6e\n" % epsp_jump)
f.write("R_jump     = %.6e\n" % R_jump)
f.close()
