from odbAccess import openOdb

odb = openOdb("chaboche_umat_1cycle.odb")
a = odb.rootAssembly

print("ASSEMBLY NODESETS:")
for k in a.nodeSets.keys():
    print("  ", k)

print("\nINSTANCES:")
for iname, inst in a.instances.items():
    print("INSTANCE:", iname)
    print("  NODESETS:")
    for k in inst.nodeSets.keys():
        print("    ", k)

print("\nFIELD OUTPUTS IN LAST FRAME:")
last_step = odb.steps[list(odb.steps.keys())[-1]]
last_frame = last_step.frames[-1]
for k in last_frame.fieldOutputs.keys():
    print("  ", k)

odb.close()
