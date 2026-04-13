# step_vp3_controller_autogrow.py
# VP-3: cycle-jump controller (implicit VP-2 jump inside) that runs multiple jumps and auto-grows DeltaN.
# No prints; writes vp_cycle_jump_controller.txt

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

# -------- Controller settings --------
nTrainCycles = 6

N_target_total = 5000      # total cycles to advance in "cycle space" (demo)
max_jumps = 30             # max number of jump events

DeltaN = 10                # starting jump size
DeltaN_min = 1
DeltaN_max = 500

tol_rate = 0.20            # accept if trial-cycle dEpbar differs <= 20%

# caps per jump (keeps physics reasonable)
dEpbar_cap_total = 0.05
dR_cap_total = 200.0

# implicit iteration (VP-2)
max_fp_iter = 8
fp_tol_rel = 0.02

# auto-grow/shrink
grow_factor = 1.5          # if stable+accepted, multiply DeltaN by this
shrink_factor = 0.5        # if rejected, multiply DeltaN by this
stable_window = 3          # require last 3 dEpbar values to be "stable" to grow
stable_tol = 0.05          # 5% variability tolerance in that window

# -------- State --------
eps_p = 0.0
R = 0.0
t_global = 0.0
N_advanced = 0

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

def is_stable(dEpbar_hist):
    # check last stable_window values within +/- stable_tol
    if len(dEpbar_hist) < stable_window:
        return False
    w = dEpbar_hist[-stable_window:]
    m = sum(w) / float(len(w))
    if m <= 0.0:
        return False
    for v in w:
        if abs(v - m) / m > stable_tol:
            return False
    return True

# -------- Training --------
train = []
dEpbar_hist = []
for c in range(nTrainCycles):
    eps_p, R, meas, t_global = one_cycle(eps_p, R, t_global)
    train.append(meas)
    dEpbar_hist.append(meas[0])

dEpbar_last = train[-1][0]
dR_last = train[-1][1]
eps_pN = eps_p
RN = R

# -------- Jump loop --------
log = []
for j in range(max_jumps):
    if N_advanced >= N_target_total:
        break

    # enforce caps-based maximum DeltaN for this step
    DeltaN_cap = DeltaN
    if dEpbar_last > 0.0:
        DeltaN_cap = min(DeltaN_cap, int(max(1, math.floor(dEpbar_cap_total / dEpbar_last))))
    if abs(dR_last) > 0.0:
        DeltaN_cap = min(DeltaN_cap, int(max(1, math.floor(dR_cap_total / abs(dR_last)))))

    DeltaN_use = max(DeltaN_min, min(DeltaN_cap, DeltaN_max, N_target_total - N_advanced))

    # --- VP-2 implicit fixed-point solve for R_jump ---
    Rk = RN + DeltaN_use * dR_last
    for it in range(max_fp_iter):
        eps_p_tmp, R_tmp, meas_tmp, _ = one_cycle(eps_pN, Rk, 0.0)
        dR_at_Rk = meas_tmp[1]
        Rnext = RN + DeltaN_use * dR_at_Rk
        denom = max(1.0e-12, abs(Rk))
        if abs(Rnext - Rk) / denom <= fp_tol_rel:
            Rk = Rnext
            break
        Rk = Rnext
    R_jump = Rk

    # trial cycle for acceptance
    eps_p_t, R_t, meas_t, _ = one_cycle(eps_pN, R_jump, 0.0)
    dEpbar_trial = meas_t[0]
    dR_trial = meas_t[1]

    denom = max(1.0e-14, dEpbar_last)
    err = abs(dEpbar_trial - dEpbar_last) / denom
    accepted = (err <= tol_rate)

    log.append((j+1, N_advanced, DeltaN_use, RN, R_jump, dEpbar_last, dEpbar_trial, err, accepted))

    if accepted:
        # advance cycle count and update state for next jump
        N_advanced += DeltaN_use
        RN = R_jump
        # refresh "last-cycle" averages by running one real cycle at new state
        eps_pN, RN, meas_new, _ = one_cycle(eps_pN, RN, 0.0)
        dEpbar_last = meas_new[0]
        dR_last = meas_new[1]
        dEpbar_hist.append(dEpbar_last)

        # auto-grow if stable
        if is_stable(dEpbar_hist):
            DeltaN = int(max(DeltaN_min, min(DeltaN_max, math.floor(DeltaN * grow_factor))))
    else:
        # shrink and retry next loop
        DeltaN = int(max(DeltaN_min, math.floor(DeltaN * shrink_factor)))

# -------- write output --------
outPath = os.path.join(os.getcwd(), "vp_cycle_jump_controller.txt")
f = open(outPath, "w")
f.write("VP-3 controller: implicit cycle-jump + auto-grow DeltaN\n\n")
f.write("Target total cycles to advance: %d\n" % N_target_total)
f.write("Final cycles advanced: %d\n" % N_advanced)
f.write("Final DeltaN (controller state): %d\n\n" % DeltaN)

f.write("Columns:\n")
f.write("jump_id  N_advanced_before  DeltaN_use  R_before  R_jump  dEpbar_last  dEpbar_trial  err  accepted\n\n")
for r in log:
    f.write("%d  %d  %d  %.6e  %.6e  %.6e  %.6e  %.6e  %s\n" % r)

f.close()

try:
    os.startfile(outPath)
except:
    pass