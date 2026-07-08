from odbAccess import openOdb

odb = openOdb("chaboche_umat_1cycle.odb")
step = odb.steps["MONOTONIC_TENSION"]

for iframe in [0, 1, 2, 5, 10, len(step.frames)-1]:
    fr = step.frames[iframe]
    print("\nFRAME", iframe, "time=", fr.frameValue)

    if "S" in fr.fieldOutputs:
        print("S values:")
        for v in fr.fieldOutputs["S"].values:
            print("  elem", v.elementLabel, "ip", v.integrationPoint, "S=", v.data)

    if "SDV1" in fr.fieldOutputs:
        print("SDV1 values:")
        for v in fr.fieldOutputs["SDV1"].values:
            print("  elem", v.elementLabel, "ip", v.integrationPoint, "SDV1=", v.data)

odb.close()
