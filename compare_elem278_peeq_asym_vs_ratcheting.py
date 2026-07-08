from odbAccess import openOdb
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

elem_label = 278
step_name = "Step-1"
base = r"D:\TUBAF\Master_Thesis\Abaqus_trial"

def extract_elem_peeq_history(odb_path):
    odb = openOdb(path=odb_path, readOnly=True)
    step = odb.steps[step_name]
    times = []
    vals = []
    for fr in step.frames:
        if "PEEQ" not in fr.fieldOutputs:
            continue
        peeq = fr.fieldOutputs["PEEQ"]
        vmax = None
        for v in peeq.values:
            if v.elementLabel == elem_label:
                val = float(v.data)
                if (vmax is None) or (val > vmax):
                    vmax = val
        if vmax is not None:
            times.append(fr.frameValue)
            vals.append(vmax)
    odb.close()
    if not vals:
        raise RuntimeError("No PEEQ values found for element %d in %s" % (elem_label, odb_path))
    return times, vals

t_asym, p_asym = extract_elem_peeq_history(os.path.join(base, "combined_asym_2cycle.odb"))
t_rat, p_rat   = extract_elem_peeq_history(os.path.join(base, "combined_ratcheting_2cycle.odb"))

csv_path = os.path.join(base, "compare_elem278_peeq_asym_vs_ratcheting.csv")
png_path = os.path.join(base, "compare_elem278_peeq_asym_vs_ratcheting.png")

with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time_asym", "peeq_elem278_asym", "time_ratcheting", "peeq_elem278_ratcheting"])
    n = max(len(t_asym), len(t_rat))
    for i in range(n):
        row = []
        row += [t_asym[i], p_asym[i]] if i < len(t_asym) else ["", ""]
        row += [t_rat[i], p_rat[i]] if i < len(t_rat) else ["", ""]
        w.writerow(row)

plt.figure(figsize=(7,5))
plt.plot(t_asym, p_asym, lw=1.8, label="Asymmetric element 278")
plt.plot(t_rat, p_rat, lw=1.8, label="Ratcheting-style element 278")
plt.xlabel("Time")
plt.ylabel("PEEQ (max IP in element 278)")
plt.title("Element 278 PEEQ: asymmetric vs ratcheting-style")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(png_path, dpi=200)

print("Wrote:", csv_path)
print("Wrote:", png_path)
print("Asymmetric final elem278 PEEQ =", p_asym[-1])
print("Ratcheting final elem278 PEEQ =", p_rat[-1])
print("Asymmetric max elem278 PEEQ =", max(p_asym))
print("Ratcheting max elem278 PEEQ =", max(p_rat))
