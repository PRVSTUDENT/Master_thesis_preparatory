# Abaqus Python script to extract force-displacement data from mono_ep_test.odb
# Run with:
#   abaqus python extract_fd_terminal.py

from odbAccess import openOdb
import csv
import os

ODB_NAME = 'mono_ep_test.odb'
STEP_NAME = 'Step-1'
RIGHT_NODE = 1                 # one representative node on the loaded face (x = 10)
LEFT_NODES = list(range(501, 526))  # all nodes on the fixed face (x = 0)

base_dir = os.getcwd()
odb_path = os.path.join(base_dir, ODB_NAME)
if not os.path.exists(odb_path):
    raise IOError('ODB not found: %s' % odb_path)

odb = openOdb(path=odb_path, readOnly=True)
step = odb.steps[STEP_NAME]
regions = step.historyRegions

u_key = 'Node PART-1-1.%d' % RIGHT_NODE
u_hist = regions[u_key].historyOutputs['U1'].data

rf_total = None
for n in LEFT_NODES:
    rf_key = 'Node PART-1-1.%d' % n
    rf_hist = regions[rf_key].historyOutputs['RF1'].data
    if rf_total is None:
        rf_total = [[t, v] for (t, v) in rf_hist]
    else:
        for i, (t, v) in enumerate(rf_hist):
            rf_total[i][1] += v

out_csv = os.path.join(base_dir, 'force_displacement.csv')
with open(out_csv, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['time', 'U1', 'RF_total', 'RF_total_positive'])
    for i in range(len(u_hist)):
        t_u, u1 = u_hist[i]
        t_r, rf = rf_total[i]
        if abs(t_u - t_r) > 1e-12:
            raise ValueError('Time mismatch at row %d: U=%g RF=%g' % (i, t_u, t_r))
        writer.writerow([t_u, u1, rf, -rf])

odb.close()
print('Wrote:', out_csv)
print('Final U1 =', u_hist[-1][1])
print('Final RF_total_positive =', -rf_total[-1][1])
