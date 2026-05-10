from odbAccess import openOdb

odb = openOdb("chaboche_vp_v1.odb")
assembly = odb.rootAssembly
right_set = assembly.nodeSets["RIGHT_FACE"]
right_labels = set(node.label for node in right_set.nodes[0])
step = odb.steps["MONOTONIC_TENSION"]
fr = step.frames[-1]

rf1 = 0.0
u1 = 0.0

for v in fr.fieldOutputs["RF"].values:
    if v.nodeLabel in right_labels:
        rf1 += v.data[0]

for v in fr.fieldOutputs["U"].values:
    if v.nodeLabel in right_labels:
        u1 = max(u1, v.data[0], key=abs)

print("Last frame time =", fr.frameValue)
print("RIGHT_FACE U1 =", u1)
print("RIGHT_FACE RF1 sum =", rf1)

odb.close()
