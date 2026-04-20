import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def read_csv(path):
    u = []
    rf = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        for row in r:
            u.append(float(row["U1"]))
            rf.append(float(row["RF_total_positive"]))
    return u, rf

u_sym, rf_sym = read_csv("combined_2cycle_tuned_hys.csv")
u_asy, rf_asy = read_csv("combined_asym_2cycle_hys.csv")

plt.figure(figsize=(7,5))
plt.plot(u_sym, rf_sym, lw=1.8, label="Combined tuned symmetric 2-cycle")
plt.plot(u_asy, rf_asy, lw=1.8, label="Combined asymmetric 2-cycle")
plt.xlabel("U1")
plt.ylabel("Reaction force")
plt.title("Combined hardening: symmetric vs asymmetric")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("compare_combined_sym_vs_asym_2cycle.png", dpi=200)

print("Wrote: compare_combined_sym_vs_asym_2cycle.png")
print("Symmetric final U1 =", u_sym[-1])
print("Asymmetric final U1 =", u_asy[-1])
print("Symmetric max force =", max(rf_sym))
print("Asymmetric max force =", max(rf_asy))
print("Symmetric min force =", min(rf_sym))
print("Asymmetric min force =", min(rf_asy))
