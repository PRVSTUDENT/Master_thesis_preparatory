import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def read_csv(path):
    t = []
    v = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        time_key = [k for k in r.fieldnames if k.lower().startswith("time")][0]
        peeq_key = [k for k in r.fieldnames if "PEEQ" in k][0]
        for row in r:
            t.append(float(row[time_key]))
            v.append(float(row[peeq_key]))
    return t, v

t_asym, p_asym = read_csv("combined_asym_2cycle_peeq.csv")
t_rat, p_rat = read_csv("combined_ratcheting_2cycle_peeq.csv")

plt.figure(figsize=(7,5))
plt.plot(t_asym, p_asym, lw=1.8, label="Asymmetric combined")
plt.plot(t_rat, p_rat, lw=1.8, label="Ratcheting-style combined")
plt.xlabel("Time")
plt.ylabel("PEEQ (max over model)")
plt.title("PEEQ comparison: asymmetric vs ratcheting-style")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("compare_asym_vs_ratcheting_peeq.png", dpi=200)

print("Wrote: compare_asym_vs_ratcheting_peeq.png")
print("Asymmetric final PEEQ =", p_asym[-1])
print("Ratcheting final PEEQ =", p_rat[-1])
print("Asymmetric max PEEQ =", max(p_asym))
print("Ratcheting max PEEQ =", max(p_rat))
