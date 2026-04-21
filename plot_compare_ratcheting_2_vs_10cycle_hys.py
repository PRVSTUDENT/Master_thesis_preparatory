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

u2, rf2 = read_csv("combined_ratcheting_2cycle_hys.csv")
u10, rf10 = read_csv("combined_ratcheting_10cycle_hys.csv")

plt.figure(figsize=(7,5))
plt.plot(u2, rf2, lw=1.8, label="Ratcheting-style 2 cycles")
plt.plot(u10, rf10, lw=1.8, label="Ratcheting-style 10 cycles")
plt.xlabel("U1")
plt.ylabel("Reaction force")
plt.title("Ratcheting-style combined hardening: 2 vs 10 cycles")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("compare_ratcheting_2_vs_10cycle_hys.png", dpi=200)

print("Wrote: compare_ratcheting_2_vs_10cycle_hys.png")
print("2-cycle final U1 =", u2[-1])
print("10-cycle final U1 =", u10[-1])
print("2-cycle max force =", max(rf2))
print("10-cycle max force =", max(rf10))
print("2-cycle min force =", min(rf2))
print("10-cycle min force =", min(rf10))
