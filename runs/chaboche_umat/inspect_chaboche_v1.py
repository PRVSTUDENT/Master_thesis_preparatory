from odbAccess import openOdb

odb = openOdb("chaboche_vp_v1.odb")
step = odb.steps["MONOTONIC_TENSION"]
fr = step.frames[-1]

s11 = [v.data[0] for v in fr.fieldOutputs["S"].values]
sdv1 = [v.data for v in fr.fieldOutputs["SDV1"].values]
sdv15 = [v.data for v in fr.fieldOutputs["SDV15"].values]

print("Last frame time =", fr.frameValue)
print("Avg S11 =", sum(s11)/len(s11))
print("Min S11 =", min(s11))
print("Max S11 =", max(s11))
print("Avg SDV1 =", sum(sdv1)/len(sdv1))
print("Max SDV1 =", max(sdv1))
print("Avg SDV15 last dp =", sum(sdv15)/len(sdv15))

odb.close()
