from odbAccess import openOdb
odb = openOdb("elastic_umat_smoke.odb")
step = odb.steps["MONOTONIC_TENSION"]
fr = step.frames[-1]
print("Last frame time =", fr.frameValue)
print("S values:")
for v in fr.fieldOutputs["S"].values:
    print(v.data)
print("SDV1 values:")
for v in fr.fieldOutputs["SDV1"].values:
    print(v.data)
odb.close()
