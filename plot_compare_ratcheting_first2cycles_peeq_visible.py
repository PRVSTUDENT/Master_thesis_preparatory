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
plt.plot(t10, p10, lw=2.0, label="Ratcheting-style 10 cycles")
plt.plot(t2, p2, lw=0, marker="o", markersize=4, label="Ratcheting-style 2 cycles (markers)")
plt.xlim(0, 2.05)
plt.xlabel("Time")
plt.ylabel("PEEQ (max over model)")
plt.title("Ratcheting-style PEEQ: first 2 cycles visibility check")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("compare_ratcheting_first2cycles_peeq_visible.png", dpi=200)

print("Wrote: compare_ratcheting_first2cycles_peeq_visible.png")
print("2-cycle final PEEQ =", p2[-1])
print("10-cycle PEEQ at t<=2 final visible point =", p10[[i for i,x in enumerate(t10) if x <= 2.0][-1]])
