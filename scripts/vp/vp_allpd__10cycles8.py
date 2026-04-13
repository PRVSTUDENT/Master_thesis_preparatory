# vp_odb_extract_allpd_per_cycle.py
# Extract per-cycle increments of global plastic dissipation ALLPD from an Abaqus/Standard ODB.
# If ALLPD is missing, it writes vp_history_keys.txt telling you what is available.

import os, sys, csv
from odbAccess import openOdb

# ---- EDIT THIS ----
odbPath  = r"D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\vp_10cycles8.odb"
stepName = "Step-1"
cycle_T  = 1.0
nCycles  = 10

def open_csv(path):
    if sys.version_info[0] >= 3:
        return open(path, "w", newline="")
    return open(path, "wb")

odb = openOdb(path=odbPath, readOnly=True)
if stepName not in odb.steps:
    odb.close()
    raise ValueError("Step not found: %s" % stepName)

step = odb.steps[stepName]
outDir = os.path.dirname(odbPath)

# --- find ALLPD in any history region ---
allpd_region = None
allpd = None

for rname, reg in step.historyRegions.items():
    if "ALLPD" in reg.historyOutputs:
        allpd_region = rname
        allpd = reg.historyOutputs["ALLPD"].data
        break

# --- write available history keys (always) ---
keysPath = os.path.join(outDir, "vp_history_keys.txt")
f = open(keysPath, "w")
f.write("ODB: %s\n" % odbPath)
f.write("Step: %s\n\n" % stepName)
f.write("History regions and keys:\n")
for rname, reg in step.historyRegions.items():
    f.write("\n[%s]\n" % rname)
    for k in sorted(reg.historyOutputs.keys()):
        f.write("  %s\n" % k)
f.write("\nALLPD_found = %s\n" % str(allpd is not None))
if allpd is not None:
    f.write("ALLPD_region = %s\n" % allpd_region)
f.close()

if allpd is None:
    odb.close()
    # open keys file so you can see what’s available
    try:
        os.startfile(keysPath)
    except:
        pass
    raise ValueError("ALLPD not found in ODB history. Add ALLPD as History Output and rerun job.")

# --- helper: closest time sample ---
t_series = [p[0] for p in allpd]
v_series = [p[1] for p in allpd]

def closest_index(tgt):
    best_i = 0
    best_dt = 1.0e100
    for i, t in enumerate(t_series):
        dt = abs(t - tgt)
        if dt < best_dt:
            best_dt = dt
            best_i = i
    return best_i, best_dt

# --- cycle-end ALLPD and increments ---
cycle_end = []
for k in range(nCycles + 1):
    tgt = k * cycle_T
    i, dt_err = closest_index(tgt)
    cycle_end.append((k, tgt, t_series[i], v_series[i], dt_err))

cycle_inc = []
for k in range(1, len(cycle_end)):
    v_k = cycle_end[k][3]
    v_km1 = cycle_end[k-1][3]
    cycle_inc.append((k, v_k, v_km1, v_k - v_km1))

csvOut = os.path.join(outDir, "vp_cycle_inc_allpd.csv")
with open_csv(csvOut) as g:
    w = csv.writer(g)
    w.writerow(["cycle_id", "ALLPD_end", "ALLPD_prev", "dALLPD", "region"])
    for r in cycle_inc:
        w.writerow(list(r) + [allpd_region])

odb.close()

try:
    os.startfile(csvOut)
except:
    pass
