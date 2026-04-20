from odbAccess import openOdb
import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

odb_path = r'D:\TUBAF\Master_Thesis\Abaqus_trial\lin_kin_1cycle.odb'
step_name = 'Step-1'

# one representative node on the loaded right face
right_node_for_u = 13

# all nodes on the fixed left face
left_nodes_for_rf = list(range(501, 526))

odb = openOdb(path=odb_path, readOnly=True)
step = odb.steps[step_name]
regions = step.historyRegions


def node_history_key(node_number):
    suffix = '.%d' % node_number
    matches = [key for key in regions.keys() if key.startswith('Node ') and key.endswith(suffix)]
    if not matches:
        raise KeyError('No history region found for node %d' % node_number)
    if len(matches) > 1:
        raise KeyError('Multiple history regions found for node %d: %s' % (node_number, matches))
    return matches[0]

# U1 history
u_hist = regions[node_history_key(right_node_for_u)].historyOutputs['U1'].data

# total RF1 history
rf_total = None
for n in left_nodes_for_rf:
    rf_hist = regions[node_history_key(n)].historyOutputs['RF1'].data
    if rf_total is None:
        rf_total = [[t, v] for (t, v) in rf_hist]
    else:
        for i, (t, v) in enumerate(rf_hist):
            rf_total[i][1] += v

times = []
u_vals = []
rf_vals = []
rf_pos = []

for i in range(len(u_hist)):
    t_u, u1 = u_hist[i]
    t_r, rf = rf_total[i]
    if abs(t_u - t_r) > 1e-12:
        raise ValueError(f'Time mismatch at row {i}: U={t_u}, RF={t_r}')
    times.append(t_u)
    u_vals.append(u1)
    rf_vals.append(rf)
    rf_pos.append(-rf)   # make tensile force positive

base = os.path.dirname(odb_path)
csv_path = os.path.join(base, 'lin_kin_1cycle_hys.csv')
png_path = os.path.join(base, 'lin_kin_1cycle_hys.png')

with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time', 'U1', 'RF_total', 'RF_total_positive'])
    for t, u, rf, rfp in zip(times, u_vals, rf_vals, rf_pos):
        writer.writerow([t, u, rf, rfp])

plt.plot(u_vals, rf_pos)
plt.xlabel('U1')
plt.ylabel('Reaction force')
plt.title('Linear kinematic hardening: 1 cycle')
plt.grid(True)
plt.tight_layout()
plt.savefig(png_path, dpi=200)

odb.close()
print('Wrote:', csv_path)
print('Wrote:', png_path)
print('Final U1 =', u_vals[-1])
print('Max tensile force =', max(rf_pos))
print('Min compressive force =', min(rf_pos))