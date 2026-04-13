# step_ep3_cycle_jump_accumulated_ep_1D.py
# Elastic-plastic cycle jump using monotone accumulated plastic strain as the slow variable.
# Quadratic prediction + trial-cycle accept/reject based on relative change of (dEpbar/dN).
# No prints; writes ep_cycle_jump_accumulated.txt

import os, math

E  = 70000.0
sig_y0 = 250.0
H  = 1000.0

eps_a = 0.010
nStepsPerCycle = 80
nTrainCycles = 4

DeltaN_try = 200
DeltaN_min = 1

tol_rate = 0.20  # accept if trial-cycle rate change <= 20%
dEpbar_cap_total = 0.010  # cap total accumulated plastic strain added in one jump
dR_cap_total     = 200.0

# State
eps_p = 0.0
R = 0.0

def return_map_1D(eps_total, eps_p, R):
    sig_trial = E * (eps_total - eps_p)
    f = abs(sig_trial) - (sig_y0 + R)
    if f <= 0.0:
        return sig_trial, eps_p, R, 0.0
    dgamma = f / (E + H)
    sgn = 1.0 if sig_trial >= 0.0 else -1.0
    eps_p_new = eps_p + dgamma * sgn
    R_new = R + H * dgamma
    sig_new = E * (eps_total - eps_p_new)
    return sig_new, eps_p_new, R_new, dgamma  # dgamma >= 0

def one_cycle_strain_path(eps_a, nSteps):
    pts = [0.0, eps_a, 0.0, -eps_a, 0.0]
    path = []
    segN = max(1, nSteps // 4)
    for i in range(4):
        a = pts[i]; b = pts[i+1]
        for k in range(segN):
            t = float(k)/float(segN)
            path.append(a + (b-a)*t)
    path.append(0.0)
    return path

def run_one_cycle(eps_p, R):
    sig = 0.0
    dEpbar = 0.0  # accumulated plastic strain increment in this cycle
    for eps in one_cycle_strain_path(eps_a, nStepsPerCycle):
        sig, eps_p, R, dgamma = return_map_1D(eps, eps_p, R)
        dEpbar += abs(dgamma)  # monotone measure (>=0)
    return sig, eps_p, R, dEpbar

# Training
cycle_end = []  # (sig, eps_p, R, Epbar_total)
Epbar_total = 0.0
dEpbar_list = []

for c in range(1, nTrainCycles+1):
    sig, eps_p, R, dEpbar = run_one_cycle(eps_p, R)
    Epbar_total += dEpbar
    cycle_end.append((sig, eps_p, R, Epbar_total))
    dEpbar_list.append(dEpbar)

# Use last 3 cycle dEpbar values for quadratic trend
d1 = dEpbar_list[-1] - dEpbar_list[-2]
d2 = dEpbar_list[-1] - 2.0*dEpbar_list[-2] + dEpbar_list[-3]

# Also track R trend (optional, for stability)
R1 = cycle_end[-1][2] - cycle_end[-2][2]
R2 = cycle_end[-1][2] - 2.0*cycle_end[-2][2] + cycle_end[-3][2]

DeltaN = int(DeltaN_try)

# Cap DeltaN by total allowed changes
if dEpbar_list[-1] > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dEpbar_cap_total / dEpbar_list[-1]))))
if abs(R1) > 0.0:
    DeltaN = min(DeltaN, int(max(1, math.floor(dR_cap_total / abs(R1)))))

accepted = False
attempts = []

# Current end-of-training state
sigN, epspN, RN, EpbarN = cycle_end[-1]

while True:
    if DeltaN < DeltaN_min:
        DeltaN = DeltaN_min

    # Predict dEpbar at N+DeltaN using quadratic extrapolation on dEpbar trend
    dEpbar_pred = dEpbar_list[-1] + DeltaN*d1 + 0.5*(DeltaN**2)*d2
    if dEpbar_pred < 0.0:
        dEpbar_pred = 0.0

    # Predict R similarly (keeps consistency for yield radius)
    R_pred = RN + DeltaN*R1 + 0.5*(DeltaN**2)*R2

    # Trial cycle: start from (epspN, R_pred) — conservative; (epsp jump is tricky non-monotone)
    sig_t, epsp_t, R_t, dEpbar_trial = run_one_cycle(epspN, R_pred)

    # Accept if dEpbar_trial is close to last-cycle dEpbar (rate consistency)
    denom = max(1.0e-14, dEpbar_list[-1])
    err = abs(dEpbar_trial - dEpbar_list[-1]) / denom

    attempts.append((DeltaN, dEpbar_list[-1], dEpbar_pred, dEpbar_trial, err, R_pred))

    if err <= tol_rate:
        accepted = True
        break

    if DeltaN <= DeltaN_min:
        break
    DeltaN = max(DeltaN_min, DeltaN // 2)

# Write output
outPath = os.path.join(os.getcwd(), "ep_cycle_jump_accumulated.txt")
f = open(outPath, "w")
f.write("EP cycle-jump using accumulated plastic strain (monotone)\n")
f.write("E=%.6e, sig_y0=%.6e, H=%.6e\n" % (E, sig_y0, H))
f.write("eps_a=%.6e, nTrainCycles=%d\n" % (eps_a, nTrainCycles))
f.write("DeltaN_try=%d, tol_rate=%.3f\n" % (DeltaN_try, tol_rate))
f.write("Caps: dEpbar_cap_total=%.6e, dR_cap_total=%.6e\n\n" % (dEpbar_cap_total, dR_cap_total))

f.write("Training per-cycle dEpbar:\n")
for i, v in enumerate(dEpbar_list):
    f.write("N=%d  dEpbar=%.6e\n" % (i+1, v))

f.write("\nAttempts: DeltaN  dEpbar_last  dEpbar_pred  dEpbar_trial  err  R_pred\n")
for a in attempts:
    f.write("%d  %.6e  %.6e  %.6e  %.6e  %.6e\n" % a)

f.write("\nACCEPTED = %s\n" % str(accepted))
f.write("Final DeltaN = %d\n" % DeltaN)
f.close()
