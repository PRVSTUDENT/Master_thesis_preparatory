# step3_linear_elastic_variable_blocks_noprint.py
# Variable-amplitude Miner damage accumulation with Basquin S-N.
# No prints; writes to: miner_variable_blocks_results.txt

import os, math

# ---- Basquin parameters (same units as your stress) ----
# sigma_a = sigma_f_prime * (2*Nf)^b
sigma_f_prime = 1.0e4
b = -0.10

# ---- Define your spectrum blocks: (stress_range, cycles_in_block) ----
# You can edit/add rows.
blocks = [
    (1.352911e3, 1000),   # your current one-cycle range repeated 1000 cycles
    (1.0e3,      2000),
    (8.0e2,      5000),
]

# ---- Optional Goodman mean-stress correction ----
use_goodman = False
sigma_ult = 1.2e4
sigma_m = 0.0

def life_from_range(stress_range):
    sigma_a = 0.5 * stress_range
    if use_goodman:
        denom = 1.0 - sigma_m / sigma_ult
        if denom <= 0.0:
            raise ValueError("Goodman denom <= 0")
        sigma_a = sigma_a / denom
    twoNf = (sigma_a / sigma_f_prime) ** (1.0 / b)
    return 0.5 * twoNf

D = 0.0
lines = []
for (dr, ncyc) in blocks:
    Nf = life_from_range(dr)
    dD = float(ncyc) / float(Nf)
    D += dD
    lines.append((dr, ncyc, Nf, dD))

outPath = os.path.join(os.getcwd(), "miner_variable_blocks_results.txt")
f = open(outPath, "w")
f.write("Variable-amplitude Miner + Basquin (linear elastic)\n")
f.write("cwd = %s\n" % os.getcwd())
f.write("sigma_f_prime = %.6e\n" % sigma_f_prime)
f.write("b = %.6f\n" % b)
f.write("use_goodman = %s\n" % str(use_goodman))
f.write("\nBlocks: (stress_range, cycles, Nf, dD)\n")
for (dr, ncyc, Nf, dD) in lines:
    f.write("%.6e  %d  %.6e  %.6e\n" % (dr, ncyc, Nf, dD))
f.write("\nTotal damage D = %.6e\n" % D)
f.close()
