# step_vp1_cycle_averaged_jump_1D.py
# Viscoplastic cycle-jump (VP-1): cycle-averaged evolution + adaptive DeltaN + trial-cycle acceptance.
# No prints (avoids encoding issues). Writes: vp_cycle_jump_avg.txt

import os, math

# -------------------------
# 1) Material (1D) settings
# -------------------------
E = 70000.0        # MPa (elastic modulus)

sig_y0 = 250.0     # MPa (initial yield)
H = 1000.0         # MPa (isotropic hardening modulus), R_dot = H * |eps_p_dot|

# Perzyna overstress flow:
# eps_p_dot = ( <|sigma|- (sig_y0+R)| / sig_ref > )^n / eta * sign(sigma)
sig_ref = 250.0    # MPa (reference stress to nondimensionalize overstress)
n = 5.0            # rate sensitivity exponent
eta = 5.0e3        # (time units) viscosity parameter (bigger => slower flow)

# -------------------------
# 2) Cyclic loading
# -------------------------
T = 1.0            # cycle period (time)
eps_a = 0.010      # strain amplitude (fully reversed, mean=0)

steps_per_cycle = 800         # time resolution inside a cycle (increase if unstable)
dt = T / float(steps_per_cycle)

# -------------------------
# 3) Cycle-jump controls
# -------------------------
nTrainCycles = 6              # fully simulate these to estimate cycle-averaged rates
DeltaN_try = 500              # initial jump proposal
DeltaN_min = 1

tol_rate = 0.20               # accept if trial-cycle dEpbar differs <= 20% from last-cycle dEpbar

# caps: do not allow too much evolution in one jump
dEpbar_cap_total = 0.010      # max accumulated plastic strain added in one jump
dR_cap_total = 200.0          # MPa max hardening added in one jump

# -------------------------
# State variables
# -------------------------
eps_p = 0.0     # viscoplastic strain
R = 0.0         # isotropic hardening
t_global = 0.0  # time accumulator (for completeness)

def one_cycle(eps_p, R, t0):
    """Simulate one full cycle and return updated (eps_p, R) plus cycle measures."""
    dEpbar = 0.0   # accumulated plastic strain in this cycle (monotone)
    dR = 0.0       # hardening increment in this cycle
    sig_max = -1.0e100
    sig_min =  1.0e100

    t = t0
    for k in range(steps_per_cycle):
        # strain-controlled sinusoidal cycle
        eps = eps_a * math.sin(2.0 * math.pi * (t / T))

        # stress
        sig = E * (eps - eps_p)
        if sig > sig_max: sig_max = sig
        if sig < sig_min: sig_min = sig

        # overstress
        f = abs(sig) - (sig_y0 + R)
        if f > 0.0:
            gamma_dot = ((f / sig_ref) ** n) / eta   # >=0
            sgn = 1.0 if sig >= 0.0 else -1.0
            eps_p_dot = gamma_dot * sgn
        else:
            eps_p_dot = 0.0

        # integrate
        deps_p = eps_p_dot * dt
        eps_p += deps_p

        dEpbar += abs(eps_p_dot) * dt

        # isotropic hardening driven by accumulated plastic flow
        dR_step = H * abs(eps_p_dot) * dt
        R += dR_step
        dR += dR_step

        t += dt

    # close cycle at t0 + T
    return eps_p, R, (dEpbar, dR, sig_min, sig_max), (t0 + T)

# -------------------------
# Training cycles
# -------------------------
train = []   # list of (dEpbar, dR, sig_min, sig_max)
for c in range(nTrainCycles):
    eps_p, R, meas, t_global = one_cycle(eps_p, R, t_global)
    train.append(meas)

dEpbar_last = train[-1][0]
dR_last = train[-1][1]

# Propose DeltaN with caps (based on last-cycle averages)
DeltaN = int(DeltaN_try)
if dEpbar_last > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dEpbar_cap_total / dEpbar_last))))
if abs(dR_last) > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dR_cap_total / abs(dR_last)))))

# -------------------------
# Cycle-averaged jump + trial-cycle accept/reject
# -------------------------
attempts = []
accepted = False

eps_pN = eps_p
RN = R

while True:
    if DeltaN < DeltaN_min:
        DeltaN = DeltaN_min

    # Cycle-averaged "cycle-space" update (explicit):
    # eps_p is not monotone, so we do NOT jump eps_p directly.
    # We jump only the monotone hardening R using average dR per cycle.
    R_jump = RN + DeltaN * dR_last

    # Trial: run one actual cycle starting from (eps_pN, R_jump)
    eps_p_t, R_t, meas_t, _ = one_cycle(eps_pN, R_jump, 0.0)
    dEpbar_trial = meas_t[0]
    dR_trial = meas_t[1]

    # Acceptance based on monotone measure consistency
    denom = max(1.0e-14, dEpbar_last)
    err = abs(dEpbar_trial - dEpbar_last) / denom

    attempts.append((DeltaN, dEpbar_last, dEpbar_trial, err, dR_last, dR_trial, R_jump))

    if err <= tol_rate:
        accepted = True
        break

    if DeltaN <= DeltaN_min:
        break
    DeltaN = max(DeltaN_min, DeltaN // 2)

# -------------------------
# Write output (no prints)
# -------------------------
outPath = os.path.join(os.getcwd(), "vp_cycle_jump_avg.txt")
f = open(outPath, "w")
f.write("VP-1: Viscoplastic cycle-jump via cycle-averaged update + trial-cycle acceptance\n")
f.write("Model: 1D Perzyna overstress + isotropic hardening\n\n")

f.write("Material:\n")
f.write("  E = %.6e MPa\n" % E)
f.write("  sig_y0 = %.6e MPa\n" % sig_y0)
f.write("  H = %.6e MPa\n" % H)
f.write("  sig_ref = %.6e MPa, n = %.6f, eta = %.6e\n\n" % (sig_ref, n, eta))

f.write("Loading:\n")
f.write("  T = %.6e, eps_a = %.6e, steps_per_cycle = %d, dt = %.6e\n\n" % (T, eps_a, steps_per_cycle, dt))

f.write("Training cycles (dEpbar, dR, sig_min, sig_max):\n")
for i, m in enumerate(train):
    f.write("  N=%d  dEpbar=%.6e  dR=%.6e  sig_min=%.6e  sig_max=%.6e\n" % (i+1, m[0], m[1], m[2], m[3]))

f.write("\nLast-cycle averages used:\n")
f.write("  dEpbar_last = %.6e\n" % dEpbar_last)
f.write("  dR_last     = %.6e\n" % dR_last)

f.write("\nJump control:\n")
f.write("  DeltaN_try=%d, tol_rate=%.3f\n" % (DeltaN_try, tol_rate))
f.write("  caps: dEpbar_cap_total=%.6e, dR_cap_total=%.6e\n" % (dEpbar_cap_total, dR_cap_total))

f.write("\nAttempts: DeltaN  dEpbar_last  dEpbar_trial  err  dR_last  dR_trial  R_jump\n")
for a in attempts:
    f.write("  %d  %.6e  %.6e  %.6e  %.6e  %.6e  %.6e\n" % a)

f.write("\nACCEPTED = %s\n" % str(accepted))
f.write("Final DeltaN = %d\n" % int(attempts[-1][0] if attempts else DeltaN))

f.close()

# try to open the file (Windows)
try:
    os.startfile(outPath)
except:
    pass