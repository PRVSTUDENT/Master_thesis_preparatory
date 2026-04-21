from odbAccess import openOdb
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

odb_path = r"D:\TUBAF\Master_Thesis\Abaqus_trial\combined_ratcheting_10cycle.odb"
step_name = "Step-1"

odb = openOdb(path=odb_path, readOnly=True)
step = odb.steps[step_name]

base = os.path.dirname(odb_path)
csv_path = os.path.join(base, "combined_ratcheting_10cycle_peeq.csv")
png_path = os.path.join(base, "combined_ratcheting_10cycle_peeq.png")

times = []
vals = []

for fr in step.frames:
    t = fr.frameValue
    if "PEEQ" not in fr.fieldOutputs:
        continue
    peeq = fr.fieldOutputs["PEEQ"]
    if len(peeq.values) == 0:
        continue
    vmax = max(float(v.data) for v in peeq.values)
    times.append(t)
    vals.append(vmax)

if not vals:
    odb.close()
    raise RuntimeError("No PEEQ field output values found in Step-1 frames")

with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time", "PEEQ_max"])
    for t, v in zip(times, vals):
        w.writerow([t, v])

plt.figure(figsize=(6,4))
plt.plot(times, vals, lw=1.5)
plt.xlabel("Time")
plt.ylabel("PEEQ (max over model)")
plt.title("10-cycle ratcheting-style combined hardening: PEEQ vs time")
plt.grid(True)
plt.tight_layout()
plt.savefig(png_path, dpi=200)

odb.close()
print("Wrote:", csv_path)
print("Wrote:", png_path)
print("Final PEEQ =", vals[-1])
print("Max PEEQ =", max(vals))
print("Min PEEQ =", min(vals))
