# step1_extract_stress_range_NOSET.py  (Abaqus/CAE 2021, Python 2.7)
# Computes global min/max/range of a stress component across ALL elements/ips
# over ALL frames in a step (i.e., over the whole cycle).
#
# This version does NOT need elem sets like EALL.

odbPath   = r"D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\one-cycle.odb"
stepName  = "Step-1"
component = "S11"   # "S11","S22","S33","S12","S13","S23" or "MISES"

from odbAccess import openOdb
from abaqusConstants import INTEGRATION_POINT
import os, csv, sys

compIdx = {"S11":0, "S22":1, "S33":2, "S12":3, "S13":4, "S23":5}

odb = openOdb(path=odbPath, readOnly=True)

if stepName not in odb.steps:
    odb.close()
    raise ValueError("Step not found: %s" % stepName)

step = odb.steps[stepName]

# Helpful info
print("ODB opened: %s" % odbPath)
print("Instances in ODB:")
for nm in sorted(odb.rootAssembly.instances.keys()):
    print("  - %s" % nm)

minVal = 1.0e100
maxVal = -1.0e100
tAtMin = None
tAtMax = None
rows = []

for fr in step.frames:
    t = fr.frameValue
    S = fr.fieldOutputs["S"]

    frMin = 1.0e100
    frMax = -1.0e100

    if component.upper() == "MISES":
        for v in S.values:
            if v.position != INTEGRATION_POINT:
                continue
            val = v.mises
            if val < frMin: frMin = val
            if val > frMax: frMax = val
    else:
        c = component.upper()
        if c not in compIdx:
            odb.close()
            raise ValueError("Unknown component: %s" % component)
        k = compIdx[c]
        for v in S.values:
            if v.position != INTEGRATION_POINT:
                continue
            val = v.data[k]
            if val < frMin: frMin = val
            if val > frMax: frMax = val

    if frMin < minVal:
        minVal = frMin; tAtMin = t
    if frMax > maxVal:
        maxVal = frMax; tAtMax = t

    rows.append([t, frMin, frMax])

odb.close()

stressRange = maxVal - minVal

print("\nRESULTS")
print("Component: %s" % component)
print("GLOBAL MIN = % .6e at t = %s" % (minVal, str(tAtMin)))
print("GLOBAL MAX = % .6e at t = %s" % (maxVal, str(tAtMax)))
print("RANGE (max-min) = % .6e" % stressRange)

# Write CSV next to ODB (works in Python 2 and 3)
outDir = os.path.dirname(odbPath)
csvPath = os.path.join(outDir, "one_cycle_%s_minmax_NOSET.csv" % component)

if sys.version_info[0] >= 3:
    f = open(csvPath, "w", newline="")
else:
    f = open(csvPath, "wb")

with f:
    w = csv.writer(f)
    w.writerow(["time", "min", "max"])
    for r in rows:
        w.writerow(r)

print("Wrote: %s" % csvPath)
