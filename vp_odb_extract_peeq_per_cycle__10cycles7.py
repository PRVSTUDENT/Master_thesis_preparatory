# vp_odb_extract_peeq_per_cycle.py
# ODB-driven viscoplastic metric extraction:
# - reads max PEEQ over the model for each frame
# - samples cycle-end points at t = 0,1,2,...,Ncycles (closest frame)
# - outputs per-cycle dPEEQ (monotone proxy for accumulated plastic strain)
#
# Run in Abaqus/CAE: File -> Run Script...
# Output files are written next to the ODB.

import os, sys, csv
from odbAccess import openOdb
from abaqusConstants import INTEGRATION_POINT

# ---- EDIT THESE ----
odbPath = r"D:\TUBAF\Master_Thesis\Abaqus_trial\one_cycle_run\vp_10cycles7.odb"
stepName  = "Step-1"
cycle_T   = 1.0     # 1.0 time unit per cycle (because your amplitude is 2*pi with T=1)
nCycles   = 10      # Step time period should be 10.0 for 10 cycles

odb = openOdb(path=odbPath, readOnly=True)
if stepName not in odb.steps:
    odb.close()
    raise ValueError("Step not found: %s" % stepName)

step = odb.steps[stepName]
frames = step.frames

# --- collect per-frame time and max(PEEQ) ---
t_list = []
peeq_max_list = []

for fr in frames:
    t = fr.frameValue
    if "PEEQ" not in fr.fieldOutputs:
        odb.close()
        raise ValueError("Field output PEEQ not found. Enable PEEQ in Field Output Requests and rerun job.")

F = None
for fr in frames:
    t = fr.frameValue
    P = fr.fieldOutputs["PEEQ"].getSubset(position=INTEGRATION_POINT)
    mx = 0.0
    for v in P.values:
        if v.data > mx:
            mx = v.data
    t_list.append(t)
    peeq_max_list.append(mx)

# --- helper: find frame index closest to a target time ---
def argmin_abs_time(target):
    best_i = 0
    best_dt = 1.0e100
    for i, t in enumerate(t_list):
        dt = abs(t - target)
        if dt < best_dt:
            best_dt = dt
            best_i = i
    return best_i, best_dt

# --- sample cycle ends ---
cycle_end = []  # (cycle_id, target_time, frame_time, maxPEEQ, dt_error)
for k in range(nCycles + 1):
    tgt = k * cycle_T
    i, dt_err = argmin_abs_time(tgt)
    cycle_end.append((k, tgt, t_list[i], peeq_max_list[i], dt_err))

# --- compute per-cycle increments ---
cycle_inc = []  # (cycle_k, peeq_end_k, peeq_end_km1, dPEEQ)
for k in range(1, len(cycle_end)):
    pe_k = cycle_end[k][3]
    pe_km1 = cycle_end[k-1][3]
    dpe = pe_k - pe_km1
    cycle_inc.append((k, pe_k, pe_km1, dpe))

# --- write outputs next to ODB ---
outDir = os.path.dirname(odbPath)
csv1 = os.path.join(outDir, "vp_frames_peeqmax.csv")
csv2 = os.path.join(outDir, "vp_cycle_end_peeqmax.csv")
csv3 = os.path.join(outDir, "vp_cycle_inc_dpeeq.csv")

def open_csv(path):
    if sys.version_info[0] >= 3:
        return open(path, "w", newline="")
    return open(path, "wb")

with open_csv(csv1) as f:
    w = csv.writer(f)
    w.writerow(["frame_time", "max_PEEQ"])
    for t, mx in zip(t_list, peeq_max_list):
        w.writerow([t, mx])

with open_csv(csv2) as f:
    w = csv.writer(f)
    w.writerow(["cycle_id", "target_time", "frame_time_used", "max_PEEQ", "abs_time_error"])
    for r in cycle_end:
        w.writerow(list(r))

with open_csv(csv3) as f:
    w = csv.writer(f)
    w.writerow(["cycle_id", "peeq_end", "peeq_end_prev", "dPEEQ"])
    for r in cycle_inc:
        w.writerow(list(r))

odb.close()

# Try to open the key CSV automatically (Windows)
try:
    os.startfile(csv3)
except:
    pass
