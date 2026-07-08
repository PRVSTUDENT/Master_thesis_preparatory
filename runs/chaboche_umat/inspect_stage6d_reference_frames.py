from odbAccess import openOdb


odb = openOdb("chaboche_vp_v1_cyclic_eps005_50cycles.odb", readOnly=True)
try:
    step = odb.steps[odb.steps.keys()[0]]
    for frame in step.frames:
        if 29.95 <= frame.frameValue <= 30.05:
            stress_values = frame.fieldOutputs["S"].values
            sdv_values = frame.fieldOutputs["SDV1"].values
            s11 = sum([value.data[0] for value in stress_values]) / float(len(stress_values))
            statev1 = sum([value.data for value in sdv_values]) / float(len(sdv_values))
            print("%.12g %.12g %.12g" % (frame.frameValue, statev1, s11))
finally:
    odb.close()
