from odbAccess import openOdb
import csv

job = "chaboche_vp_v1_cyclic_1cycle"
odb = openOdb(job + ".odb")
assembly = odb.rootAssembly

right_set = assembly.nodeSets["RIGHT_FACE"]
right_labels = set(node.label for node in right_set.nodes[0])

rows = []

for step_name in odb.steps.keys():
    step = odb.steps[step_name]

    for frame in step.frames:
        t = frame.frameValue

        u1 = 0.0
        rf1 = 0.0
        s11_vals = []
        sdv1_vals = []
        sdv15_vals = []

        for v in frame.fieldOutputs["U"].values:
            if v.nodeLabel in right_labels and abs(v.data[0]) > abs(u1):
                u1 = v.data[0]

        for v in frame.fieldOutputs["RF"].values:
            if v.nodeLabel in right_labels:
                rf1 += v.data[0]

        for v in frame.fieldOutputs["S"].values:
            s11_vals.append(v.data[0])

        for v in frame.fieldOutputs["SDV1"].values:
            sdv1_vals.append(v.data)

        for v in frame.fieldOutputs["SDV15"].values:
            sdv15_vals.append(v.data)

        avg_s11 = sum(s11_vals) / len(s11_vals) if s11_vals else 0.0
        avg_sdv1 = sum(sdv1_vals) / len(sdv1_vals) if sdv1_vals else 0.0
        avg_sdv15 = sum(sdv15_vals) / len(sdv15_vals) if sdv15_vals else 0.0

        rows.append([t, u1, rf1, avg_s11, avg_sdv1, avg_sdv15])

odb.close()

with open(job + "_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Time_s", "U1_mm", "RF1_N", "Avg_S11_MPa", "Avg_SDV1_p", "Avg_SDV15_dp"])
    for r in rows:
        w.writerow(["%.8g" % r[0], "%.10g" % r[1], "%.10g" % r[2],
                    "%.10g" % r[3], "%.10g" % r[4], "%.10g" % r[5]])

u = [r[1] for r in rows]
rf = [r[2] for r in rows]
s11 = [r[3] for r in rows]
sdv1 = [r[4] for r in rows]

print("Wrote", job + "_summary.csv")
print("Max U1 =", max(u))
print("Min U1 =", min(u))
print("Max RF1 =", max(rf))
print("Min RF1 =", min(rf))
print("Max S11 =", max(s11))
print("Min S11 =", min(s11))
print("Final SDV1 =", sdv1[-1])
print("Max SDV1 =", max(sdv1))
