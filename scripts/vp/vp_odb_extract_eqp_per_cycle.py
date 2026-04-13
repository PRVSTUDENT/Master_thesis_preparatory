# vp_odb_extract_eqp_per_cycle.py
# Robust ODB extractor:
# - If PEEQ exists -> uses it
# - Else if PE exists -> computes equivalent plastic strain from PE tensor
# Writes:
#   vp_odb_field_keys.txt
#   vp_frames_eqpmax.csv
#   vp_cycle_end_eqpmax.csv
#   vp_cycle_inc_deqp.csv

import os, sys, csv, math
from odbAccess import openOdb
from abaqusConstants import INTEGRATION_POINT

# ---- EDIT THIS ----
odbPath  = r"D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\vp_10cycles3.odb"
stepName = "Step-1"
cycle_T  = 1.0
nCycles  = 10

def open_csv(path):
    if sys.version_info[0] >= 3:
        return open(path, "w", newline="")
    return open(path, "wb")

def eqv_from_PE(pe6):
    # pe6 = (pe11, pe22, pe33, pe12, pe13, pe23)
    pe11, pe22, pe33, pe12, pe13, pe23 = pe6
    m = (pe11 + pe22 + pe33) / 3.0
    d11 = pe11 - m
    d22 = pe22 - m
    d33 = pe33 - m
    # dev:dev = d11^2+d22^2+d33^2 + 2*(shear^2)
    dev2 = d11*d11 + d22*d22 + d33*d33 + 2.0*(pe12*pe12 + pe13*pe13 + pe23*pe23)
    # eq plastic strain (von Mises) = sqrt(2/3 * dev:dev)
    return math.sqrt(max(0.0, (2.0/3.0)*dev2))

odb = openOdb(path=odbPath, readOnly=True)
if stepName not in odb.steps:
    odb.close()
    raise ValueError("Step not found: %s" % stepName)

step = odb.steps[stepName]
frames = step.frames

# --- write available field output keys (all frames) ---
outDir = os.path.dirname(odbPath)
keysPath = os.path.join(outDir, "vp_odb_field_keys.txt")

fo_keys_set = set()
has_peeq = False
has_pe = False
has_peeqt = False
has_peeqmax = False
for fr in frames:
    keys = fr.fieldOutputs.keys()
    for k in keys:
        fo_keys_set.add(k)
    if "PEEQ" in keys:
        has_peeq = True
    if "PE" in keys:
        has_pe = True
    if "PEEQT" in keys:
        has_peeqt = True
    if "PEEQMAX" in keys:
        has_peeqmax = True

fo_keys = sorted(list(fo_keys_set))
f = open(keysPath, "w")
f.write("ODB: %s\n" % odbPath)
f.write("Step: %s\n" % stepName)
f.write("FieldOutputs found across frames:\n")
for k in fo_keys:
    f.write("  %s\n" % k)
f.close()

use_mode = None
if has_peeq:
    use_mode = "PEEQ"
elif has_pe:
    use_mode = "PE"
elif has_peeqt:
    use_mode = "PEEQT"
elif has_peeqmax:
    use_mode = "PEEQMAX"
else:
    odb.close()
    raise ValueError("None of PEEQ, PE, PEEQT, PEEQMAX found in ODB. Check material/outputs.")

def scalar_from_data(data):
    if isinstance(data, (tuple, list)):
        if len(data) == 0:
            return 0.0
        return float(data[0])
    return float(data)

# --- per-frame time and max eq plastic strain ---
t_list = []
eqp_max_list = []

for fr in frames:
    t = fr.frameValue
    t_list.append(t)

    if use_mode == "PEEQ" and "PEEQ" in fr.fieldOutputs:
        P = fr.fieldOutputs["PEEQ"].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            val = scalar_from_data(v.data)
            if val > mx:
                mx = val
        eqp_max_list.append(mx)
    elif use_mode == "PE" and "PE" in fr.fieldOutputs:
        P = fr.fieldOutputs["PE"].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            val = eqv_from_PE(v.data)
            if val > mx:
                mx = val
        eqp_max_list.append(mx)
    elif use_mode == "PEEQT" and "PEEQT" in fr.fieldOutputs:
        P = fr.fieldOutputs["PEEQT"].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            val = scalar_from_data(v.data)
            if val > mx:
                mx = val
        eqp_max_list.append(mx)
    elif use_mode == "PEEQMAX" and "PEEQMAX" in fr.fieldOutputs:
        P = fr.fieldOutputs["PEEQMAX"].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            val = scalar_from_data(v.data)
            if val > mx:
                mx = val
        eqp_max_list.append(mx)
    else:
        if len(eqp_max_list) == 0:
            eqp_max_list.append(0.0)
        else:
            eqp_max_list.append(eqp_max_list[-1])

# --- helper: closest frame to target time ---
def argmin_abs_time(target):
    best_i = 0
    best_dt = 1.0e100
    for i, t in enumerate(t_list):
        dt = abs(t - target)
        if dt < best_dt:
            best_dt = dt
            best_i = i
    return best_i, best_dt

# --- cycle-end sampling ---
cycle_end = []
for k in range(nCycles + 1):
    tgt = k * cycle_T
    i, dt_err = argmin_abs_time(tgt)
    cycle_end.append((k, tgt, t_list[i], eqp_max_list[i], dt_err))

cycle_inc = []
for k in range(1, len(cycle_end)):
    eq_k = cycle_end[k][3]
    eq_km1 = cycle_end[k-1][3]
    deq = eq_k - eq_km1
    cycle_inc.append((k, eq_k, eq_km1, deq))

# --- write CSVs ---
csv1 = os.path.join(outDir, "vp_frames_eqpmax.csv")
csv2 = os.path.join(outDir, "vp_cycle_end_eqpmax.csv")
csv3 = os.path.join(outDir, "vp_cycle_inc_deqp.csv")

with open_csv(csv1) as f:
    w = csv.writer(f); w.writerow(["frame_time", "max_EQP", "mode"])
    for t, mx in zip(t_list, eqp_max_list):
        w.writerow([t, mx, use_mode])

with open_csv(csv2) as f:
    w = csv.writer(f); w.writerow(["cycle_id", "target_time", "frame_time_used", "max_EQP", "abs_time_error", "mode"])
    for r in cycle_end:
        w.writerow(list(r) + [use_mode])

with open_csv(csv3) as f:
    w = csv.writer(f); w.writerow(["cycle_id", "eqp_end", "eqp_end_prev", "dEQP", "mode"])
    for r in cycle_inc:
        w.writerow(list(r) + [use_mode])

odb.close()

# open the key CSV
try:
    os.startfile(csv3)
except:
    pass
