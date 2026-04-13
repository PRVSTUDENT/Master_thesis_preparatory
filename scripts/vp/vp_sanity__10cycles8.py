# vp_sanity_check_loading_and_plasticity.py
# Checks: max|U1| on SET-2, sum RF1 on SET-2, max Mises stress,
# and max plastic measure (PEEQ or PEEQMAX if present) over the whole step.
# Writes vp_sanity_report.txt next to the ODB. No fancy prints.

import os
from odbAccess import openOdb
from abaqusConstants import NODAL, INTEGRATION_POINT

# ---- EDIT THIS ----
odbPath = r"D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\vp_10cycles8.odb"
stepName = "Step-1"
nodeSetName = "SET-2"   # your loaded face set (as in the .inp: Set-2)


def find_nodeset(odb, name):
    asm = odb.rootAssembly
    # 1) assembly-level
    if name in asm.nodeSets:
        return asm.nodeSets[name]
    # 2) search in instances
    for inst_name, inst in asm.instances.items():
        if name in inst.nodeSets:
            return inst.nodeSets[name]
    # 3) try case-insensitive match
    cand = []
    for key in asm.nodeSets.keys():
        cand.append(key)
    for inst_name, inst in asm.instances.items():
        for key in inst.nodeSets.keys():
            cand.append(key)
    low = name.lower()
    for key in cand:
        if key.lower() == low:
            # return actual
            if key in asm.nodeSets:
                return asm.nodeSets[key]
            for inst_name, inst in asm.instances.items():
                if key in inst.nodeSets:
                    return inst.nodeSets[key]
    return None


odb = openOdb(path=odbPath, readOnly=True)
if stepName not in odb.steps:
    odb.close()
    raise ValueError("Step not found: %s" % stepName)

step = odb.steps[stepName]
ns = find_nodeset(odb, nodeSetName)
if ns is None:
    # write available node sets to help
    outDir = os.path.dirname(odbPath)
    node_set_path = os.path.join(outDir, "vp_available_nodesets.txt")
    handle = open(node_set_path, "w")
    handle.write("Assembly node sets:\n")
    for key in sorted(odb.rootAssembly.nodeSets.keys()):
        handle.write("  %s\n" % key)
    handle.write("\nInstance node sets:\n")
    for inst_name, inst in odb.rootAssembly.instances.items():
        handle.write("[%s]\n" % inst_name)
        for key in sorted(inst.nodeSets.keys()):
            handle.write("  %s\n" % key)
    handle.close()
    odb.close()
    raise ValueError("Node set not found: %s (see vp_available_nodesets.txt)" % nodeSetName)

max_abs_u1 = 0.0
max_abs_sum_rf1 = 0.0
max_mises = 0.0

# plastic measure (if any)
plastic_mode = None
max_plastic = 0.0

for frame in step.frames:
    fo = frame.fieldOutputs

    # --- displacement U on loaded face ---
    if "U" in fo:
        U = fo["U"].getSubset(region=ns, position=NODAL)
        for value in U.values:
            u1 = value.data[0]
            if abs(u1) > max_abs_u1:
                max_abs_u1 = abs(u1)

    # --- reaction force RF on loaded face (sum RF1) ---
    if "RF" in fo:
        RF = fo["RF"].getSubset(region=ns, position=NODAL)
        rf_sum = 0.0
        for value in RF.values:
            rf_sum += value.data[0]
        if abs(rf_sum) > max_abs_sum_rf1:
            max_abs_sum_rf1 = abs(rf_sum)

    # --- Mises stress (whole model) ---
    if "S" in fo:
        S = fo["S"].getSubset(position=INTEGRATION_POINT)
        for value in S.values:
            mises = value.mises
            if mises > max_mises:
                max_mises = mises

    # --- plastic measure: prefer PEEQ, else PEEQMAX, else PEEQT ---
    if plastic_mode is None:
        if "PEEQ" in fo:
            plastic_mode = "PEEQ"
        elif "PEEQMAX" in fo:
            plastic_mode = "PEEQMAX"
        elif "PEEQT" in fo:
            plastic_mode = "PEEQT"

    if plastic_mode is not None and plastic_mode in fo:
        P = fo[plastic_mode].getSubset(position=INTEGRATION_POINT)
        for value in P.values:
            if value.data > max_plastic:
                max_plastic = value.data

odb.close()

outDir = os.path.dirname(odbPath)
outPath = os.path.join(outDir, "vp_sanity_report.txt")
handle = open(outPath, "w")
handle.write("ODB sanity report\n")
handle.write("odbPath = %s\n" % odbPath)
handle.write("stepName = %s\n" % stepName)
handle.write("nodeSetName = %s\n\n" % nodeSetName)

handle.write("max_abs_U1_on_SET2 = %.6e\n" % max_abs_u1)
handle.write("max_abs_sum_RF1_on_SET2 = %.6e\n" % max_abs_sum_rf1)
handle.write("max_mises_stress = %.6e\n" % max_mises)
handle.write("plastic_mode_used = %s\n" % str(plastic_mode))
handle.write("max_plastic_value = %.6e\n" % max_plastic)
handle.close()

try:
    os.startfile(outPath)
except Exception:
    pass
