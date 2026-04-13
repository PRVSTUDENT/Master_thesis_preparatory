# step_vp2_implicit_cycle_jump_1D.py
# VP-2: implicit (fixed-point) cycle-space update for R over DeltaN cycles.
# No prints; writes vp_cycle_jump_implicit.txt

import os, math

# -------- Material --------
E = 70000.0
sig_y0 = 250.0
H = 1000.0
sig_ref = 250.0
n = 5.0
eta = 5.0e3

# -------- Loading --------
T = 1.0
eps_a = 0.010
steps_per_cycle = 800
dt = T / float(steps_per_cycle)

# -------- Training --------
nTrainCycles = 6

# -------- Jump controls --------
DeltaN_try = 200
DeltaN_min = 1
tol_rate = 0.20

dEpbar_cap_total = 0.05   # allow larger than VP-1
dR_cap_total = 200.0

# Implicit iteration controls
max_fp_iter = 8
fp_tol_rel = 0.02         # 2% relative change in R between iterations

# -------- State --------
eps_p = 0.0
R = 0.0
t_global = 0.0

def one_cycle(eps_p, R, t0):
    dEpbar = 0.0
    dR = 0.0
    sig_max = -1.0e100
    sig_min =  1.0e100
    t = t0
    for k in range(steps_per_cycle):
        eps = eps_a * math.sin(2.0 * math.pi * (t / T))
        sig = E * (eps - eps_p)

        if sig > sig_max: sig_max = sig
        if sig < sig_min: sig_min = sig

        f = abs(sig) - (sig_y0 + R)
        if f > 0.0:
            gamma_dot = ((f / sig_ref) ** n) / eta
            sgn = 1.0 if sig >= 0.0 else -1.0
            eps_p_dot = gamma_dot * sgn
        else:
            eps_p_dot = 0.0

        eps_p += eps_p_dot * dt

        dEpbar += abs(eps_p_dot) * dt
        dR_step = H * abs(eps_p_dot) * dt
        R += dR_step
        dR += dR_step

        t += dt

    return eps_p, R, (dEpbar, dR, sig_min, sig_max), (t0 + T)

# -------- Training cycles --------
train = []
for c in range(nTrainCycles):
    eps_p, R, meas, t_global = one_cycle(eps_p, R, t_global)
    train.append(meas)

dEpbar_last = train[-1][0]
dR_last = train[-1][1]
eps_pN = eps_p
RN = R

# Propose DeltaN with caps
DeltaN = int(DeltaN_try)
if dEpbar_last > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dEpbar_cap_total / dEpbar_last))))
if abs(dR_last) > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dR_cap_total / abs(dR_last)))))

attempts = []
accepted = False

while True:
    if DeltaN < DeltaN_min:
        DeltaN = DeltaN_min

    # --- implicit fixed-point solve for R_jump ---
    Rk = RN + DeltaN * dR_last  # initial guess (explicit)
    fp_hist = []
    for it in range(max_fp_iter):
        # evaluate one-cycle increment at current guess Rk
        eps_p_t, R_t, meas_t, _ = one_cycle(eps_pN, Rk, 0.0)
        dR_at_Rk = meas_t[1]  # hardening gained in one cycle starting from Rk
        Rnext = RN + DeltaN * dR_at_Rk

        fp_hist.append((it+1, Rk, dR_at_Rk, Rnext))

        denom = max(1.0e-12, abs(Rk))
        if abs(Rnext - Rk) / denom <= fp_tol_rel:
            Rk = Rnext
            break
        Rk = Rnext

    R_jump = Rk

    # --- acceptance: compare trial-cycle dEpbar at jumped R to last-cycle dEpbar ---
    eps_p_t2, R_t2, meas_t2, _ = one_cycle(eps_pN, R_jump, 0.0)
    dEpbar_trial = meas_t2[0]
    dR_trial = meas_t2[1]

    denom = max(1.0e-14, dEpbar_last)
    err = abs(dEpbar_trial - dEpbar_last) / denom

    attempts.append((DeltaN, R_jump, dEpbar_last, dEpbar_trial, err, dR_last, dR_trial, fp_hist))

    if err <= tol_rate:
        accepted = True
        break

    if DeltaN <= DeltaN_min:
        break
    DeltaN = max(DeltaN_min, DeltaN // 2)

# -------- write output --------
outPath = os.path.join(os.getcwd(), "vp_cycle_jump_implicit.txt")
f = open(outPath, "w")
f.write("VP-2: implicit (fixed-point) cycle-space jump for R + trial-cycle acceptance\n\n")
f.write("Last-cycle (training): dEpbar_last=%.6e, dR_last=%.6e\n" % (dEpbar_last, dR_last))
f.write("Proposed/accepted DeltaN attempt list below.\n\n")

for a in attempts:
    DeltaN_a, R_jump_a, dEp_last_a, dEp_trial_a, err_a, dR_last_a, dR_trial_a, fp_hist_a = a
    f.write("Attempt DeltaN=%d\n" % DeltaN_a)
    f.write("  R_jump=%.6e\n" % R_jump_a)
    f.write("  dEpbar_last=%.6e  dEpbar_trial=%.6e  err=%.6e\n" % (dEp_last_a, dEp_trial_a, err_a))
    f.write("  dR_last=%.6e      dR_trial=%.6e\n" % (dR_last_a, dR_trial_a))
    f.write("  Fixed-point iterations: it  Rk  dR_at_Rk  Rnext\n")
    for h in fp_hist_a:
        f.write("    %d  %.6e  %.6e  %.6e\n" % h)
    f.write("\n")

f.write("ACCEPTED=%s\n" % str(accepted))
f.write("Final DeltaN=%d\n" % (attempts[-1][0] if attempts else DeltaN))
f.close()

try:
    os.startfile(outPath)
except:
    pass