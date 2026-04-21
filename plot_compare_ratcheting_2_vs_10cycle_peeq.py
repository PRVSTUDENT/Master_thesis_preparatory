import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def read_csv(path):
    t = []
    p = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        time_key = [k for k in r.fieldnames if k.lower().startswith("time")][0]
        peeq_key = [k for k in r.fieldnames if "PEEQ" in k][0]
        for row in r:
            t.append(float(row[time_key]))
            p.append(float(row[peeq_key]))
    return t, p

t2, p2 = read_csv("combined_ratcheting_2cycle_peeq.csv")
t10, p10 = read_csv("combined_ratcheting_10cycle_peeq.csv")

plt.figure(figsize=(7,5))
plt.plot(t2, p2, lw=1.8, label="Ratcheting-style 2 cycles")
plt.plot(t10, p10, lw=1.8, label="Ratcheting-style 10 cycles")
plt.xlabel("Time")
plt.ylabel("PEEQ (max over model)")
plt.title("Ratcheting-style combined hardening: PEEQ 2 vs 10 cycles")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("compare_ratcheting_2_vs_10cycle_peeq.png", dpi=200)

print("Wrote: compare_ratcheting_2_vs_10cycle_peeq.png")
print("2-cycle final PEEQ =", p2[-1])
print("10-cycle final PEEQ =", p10[-1])
print("2-cycle max PEEQ =", max(p2))
print("10-cycle max PEEQ =", max(p10))
