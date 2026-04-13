# vp_odb_extract_eqp_per_cycle_SCANFRAMES.py
# Robust ODB extractor that scans frames to find the best plastic measure:
# preference: PEEQ -> PE -> PEEQMAX -> PEEQT
# Writes:
#   vp_field_choice.txt
#   vp_frames_eqpmax.csv
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
    pe11, pe22, pe33, pe12, pe13, pe23 = pe6
    m = (pe11 + pe22 + pe33) / 3.0
    d11 = pe11 - m
    d22 = pe22 - m
    d33 = pe33 - m
    dev2 = d11*d11 + d22*d22 + d33*d33 + 2.0*(pe12*pe12 + pe13*pe13 + pe23*pe23)
    return math.sqrt(max(0.0, (2.0/3.0)*dev2))

odb = openOdb(path=odbPath, readOnly=True)
if stepName not in odb.steps:
    odb.close()
    raise ValueError("Step not found: %s" % stepName)

step = odb.steps[stepName]
frames = step.frames
outDir = os.path.dirname(odbPath)

# ---- scan frames to choose the best available field ----
preferred = ["PEEQ", "PE", "PEEQMAX", "PEEQT"]
use_mode = None
first_found_at = None
for i, fr in enumerate(frames):
    keys = fr.fieldOutputs.keys()
    for m in preferred:
        if m in keys:
            use_mode = m
            first_found_at = i
            break
    if use_mode is not None:
        break

if use_mode is None:
    odb.close()
    raise ValueError("None of PEEQ/PE/PEEQMAX/PEEQT exist in any frame.")

# ---- compute per-frame max EQP ----
t_list = []
eqp_max_list = []
prev = 0.0

for fr in frames:
    t = fr.frameValue
    t_list.append(t)

    keys = fr.fieldOutputs.keys()
    if use_mode not in keys:
        # if missing in some frames, carry forward (history variables should be monotone anyway)
        eqp_max_list.append(prev)
        continue

    if use_mode == "PEEQ":
        P = fr.fieldOutputs["PEEQ"].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            if v.data > mx: mx = v.data

    elif use_mode == "PE":
        P = fr.fieldOutputs["PE"].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            val = eqv_from_PE(v.data)
            if val > mx: mx = val

    else:
        # PEEQMAX or PEEQT
        P = fr.fieldOutputs[use_mode].getSubset(position=INTEGRATION_POINT)
        mx = 0.0
        for v in P.values:
            if v.data > mx: mx = v.data

    # enforce monotone (avoid tiny numerical decreases)
    if mx < prev: mx = prev
    prev = mx
    eqp_max_list.append(mx)

# ---- helper: closest frame to a target time ----
def argmin_abs_time(target):
    best_i = 0
    best_dt = 1.0e100
    for i, t in enumerate(t_list):
        dt = abs(t - target)
        if dt < best_dt:
            best_dt = dt
            best_i = i
    return best_i, best_dt

# ---- cycle-end increments ----
cycle_inc = []
for k in range(1, nCycles + 1):
    i_k, _ = argmin_abs_time(k * cycle_T)
    i_km1, _ = argmin_abs_time((k-1) * cycle_T)
    eq_k = eqp_max_list[i_k]
    eq_km1 = eqp_max_list[i_km1]
    cycle_inc.append((k, eq_k, eq_km1, eq_k - eq_km1))

# ---- write outputs ----
choicePath = os.path.join(outDir, "vp_field_choice.txt")
f = open(choicePath, "w")
f.write("ODB: %s\n" % odbPath)
f.write("Step: %s\n" % stepName)
f.write("Chosen mode: %s\n" % use_mode)
f.write("First found at frame index: %d, time=%s\n" % (first_found_at, str(frames[first_found_at].frameValue)))
f.close()

csv1 = os.path.join(outDir, "vp_frames_eqpmax.csv")
csv2 = os.path.join(outDir, "vp_cycle_inc_deqp.csv")

with open_csv(csv1) as f:
    w = csv.writer(f)
    w.writerow(["frame_time", "max_EQP", "mode"])
    for t, mx in zip(t_list, eqp_max_list):
        w.writerow([t, mx, use_mode])

with open_csv(csv2) as f:
    w = csv.writer(f)
    w.writerow(["cycle_id", "eqp_end", "eqp_end_prev", "dEQP", "mode"])
    for r in cycle_inc:
        w.writerow(list(r) + [use_mode])

odb.close()

try:
    os.startfile(csv2)
except:
    pass
