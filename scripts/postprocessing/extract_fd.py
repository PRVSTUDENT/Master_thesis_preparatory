from odbAccess import openOdb
import csv
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
odb_path = os.path.join(repo_root, 'one_cycle_run', 'mono_ep_test_fix.odb')
step_name = 'Step-1'

# From the corrected input:
# Right loaded face nodes = 1..25
# Left fixed face nodes   = 501..525
right_node_for_u = 1
left_nodes_for_rf = list(range(501, 526))

odb = openOdb(path=odb_path, readOnly=True)
step = odb.steps[step_name]
regions = step.historyRegions

# Read one U1 history from the loaded face.
u_key = f'Node PART-1-1.{right_node_for_u}'
u_hist = regions[u_key].historyOutputs['U1'].data

# Sum RF1 over all fixed-face nodes.
rf_total = None
for n in left_nodes_for_rf:
    rf_key = f'Node PART-1-1.{n}'
    rf_hist = regions[rf_key].historyOutputs['RF1'].data

    if rf_total is None:
        rf_total = [[t, v] for (t, v) in rf_hist]
    else:
        for i, (t, v) in enumerate(rf_hist):
            rf_total[i][1] += v

# Write combined force-displacement data.
out_csv = os.path.join(repo_root, 'analysis', 'force_displacement.csv')
out_png = os.path.join(repo_root, 'analysis', 'force_displacement.png')

with open(out_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time', 'U1', 'RF_total', 'RF_total_positive'])

    u_values = []
    rf_positive_values = []

    for i in range(len(u_hist)):
        t_u, u1 = u_hist[i]
        t_r, rf = rf_total[i]

        if abs(t_u - t_r) > 1e-12:
            raise ValueError('Time mismatch at row {}: U={}, RF={}'.format(i, t_u, t_r))

        rf_positive = -rf
        u_values.append(u1)
        rf_positive_values.append(rf_positive)
        writer.writerow([t_u, u1, rf, rf_positive])

plt.figure(figsize=(6, 4))
plt.plot(u_values, rf_positive_values, linewidth=1.5)
plt.xlabel('U1')
plt.ylabel('Reaction force')
plt.title('Force-displacement')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(out_png, dpi=200)
plt.close()

odb.close()
print('Wrote:', out_csv)
print('Wrote:', out_png)
print('Final U1 =', u_hist[-1][1])
print('Final RF_total =', rf_total[-1][1])
print('Final RF_total_positive =', -rf_total[-1][1])
