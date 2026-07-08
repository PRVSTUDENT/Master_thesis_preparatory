from odbAccess import openOdb
import csv, os

def top_peeq_elements(odb_path, out_csv):
    odb = openOdb(path=odb_path, readOnly=True)
    step = odb.steps["Step-1"]
    frame = step.frames[-1]
    if "PEEQ" not in frame.fieldOutputs:
        odb.close()
        raise RuntimeError("No PEEEQ field output in final frame: " + odb_path)

    peeq = frame.fieldOutputs["PEEQ"]
    elem_max = {}

    for v in peeq.values:
        lab = v.elementLabel
        val = float(v.data)
        if (lab not in elem_max) or (val > elem_max[lab]):
            elem_max[lab] = val

    top10 = sorted(elem_max.items(), key=lambda x: x[1], reverse=True)[:10]

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "element_label", "final_frame_peeq_max_ip"])
        for i, (lab, val) in enumerate(top10, start=1):
            w.writerow([i, lab, val])

    odb.close()
    return top10

base = r"D:\TUBAF\Master_Thesis\Abaqus_trial"
asym_odb = os.path.join(base, "combined_asym_2cycle.odb")
rat_odb  = os.path.join(base, "combined_ratcheting_2cycle.odb")

asym_csv = os.path.join(base, "combined_asym_top10_final_peeq_elements.csv")
rat_csv  = os.path.join(base, "combined_ratcheting_top10_final_peeq_elements.csv")

top_asym = top_peeq_elements(asym_odb, asym_csv)
top_rat  = top_peeq_elements(rat_odb, rat_csv)

print("Wrote:", asym_csv)
print("Top asymmetric element:", top_asym[0][0], top_asym[0][1])

print("Wrote:", rat_csv)
print("Top ratcheting element:", top_rat[0][0], top_rat[0][1])
