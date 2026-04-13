# step2_miner_block_noprint.py
# No prints (avoids "Failed to encode Unicode object to locale")
# Writes results to: miner_block_results.txt

import os, math

# ---- inputs (EDIT if needed) ----
stress_range = 1.352911e3   # from your ODB (max-min)
DeltaN = 1000               # cycles to jump

# Basquin: sigma_a = sigma_f_prime * (2*Nf)^b
sigma_f_prime = 1.0e4       # EDIT (same units as stress_range)
b = -0.10                   # EDIT (negative)

# Optional Goodman correction (keep False for now)
use_goodman = False
sigma_ult = 1.2e4           # only if use_goodman=True
sigma_m = 0.0               # mean stress

# ---- calculations ----
sigma_a = 0.5 * stress_range

if use_goodman:
    denom = 1.0 - sigma_m / sigma_ult
    if denom <= 0.0:
        raise ValueError("Goodman denom <= 0")
    sigma_a_eq = sigma_a / denom
else:
    sigma_a_eq = sigma_a

if sigma_f_prime <= 0.0:
    raise ValueError("sigma_f_prime must be positive")
if b >= 0.0:
    raise ValueError("b must be negative")
if sigma_a_eq <= 0.0:
    raise ValueError("sigma_a_eq must be positive")

twoNf = (sigma_a_eq / sigma_f_prime) ** (1.0 / b)
Nf = 0.5 * twoNf
dD = float(DeltaN) / float(Nf)

# ---- write results ----
outDir = r"D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run"
outPath = os.path.join(outDir, "miner_block_results.txt")

f = open(outPath, "w")
f.write("Miner + Basquin block update (linear elastic)\n")
f.write("stress_range = %.6e\n" % stress_range)
f.write("sigma_a = %.6e\n" % sigma_a)
f.write("sigma_a_eq = %.6e\n" % sigma_a_eq)
f.write("sigma_f_prime = %.6e\n" % sigma_f_prime)
f.write("b = %.6f\n" % b)
f.write("Nf = %.6e\n" % Nf)
f.write("DeltaN = %d\n" % DeltaN)
f.write("dD = %.6e\n" % dD)
f.close()