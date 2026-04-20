from odbAccess import openOdb
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

odb_path = r'D:\TUBAF\Master_Thesis\Abaqus_trial\lin_kin_2cycle.odb'
step_name = 'Step-1'
right_node_for_u = 13
left_nodes_for_rf = list(range(501, 526))

def find_node_key(regions, node_label):
    target = '.%d' % node_label
    for k in regions.keys():
        if k.startswith('Node ') and k.endswith(target):
            return k
    raise KeyError('No history region found for node %d' % node_label)

odb = openOdb(path=odb_path, readOnly=True)
step = odb.steps[step_name]
regions = step.historyRegions

u_key = find_node_key(regions, right_node_for_u)
u_hist = regions[u_key].historyOutputs['U1'].data

rf_total = None
for n in left_nodes_for_rf:
    rf_key = find_node_key(regions, n)
    rf_hist = regions[rf_key].historyOutputs['RF1'].data
    if rf_total is None:
        rf_total = [[t, v] for (t, v) in rf_hist]
    else:
        for i, (t, v) in enumerate(rf_hist):
            rf_total[i][1] += v

times, u_vals, rf_pos = [], [], []
for i in range(len(u_hist)):
    t_u, u1 = u_hist[i]
    t_r, rf = rf_total[i]
    if abs(t_u - t_r) > 1e-12:
        raise ValueError('Time mismatch at row %d: U=%g RF=%g' % (i, t_u, t_r))
    times.append(t_u)
    u_vals.append(u1)
    rf_pos.append(-rf)

base = os.path.dirname(odb_path)
csv_path = os.path.join(base, 'lin_kin_2cycle_hys.csv')
png_path = os.path.join(base, 'lin_kin_2cycle_hys.png')

with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['time', 'U1', 'RF_total_positive'])
    for t, u, rf in zip(times, u_vals, rf_pos):
        w.writerow([t, u, rf])

plt.figure(figsize=(6,4))
plt.plot(u_vals, rf_pos, lw=1.5)
plt.xlabel('U1')
plt.ylabel('Reaction force')
plt.title('Linear kinematic hardening: 2 cycles')
plt.grid(True)
plt.tight_layout()
plt.savefig(png_path, dpi=200)

odb.close()
print('Wrote:', csv_path)
print('Wrote:', png_path)
print('Final U1 =', u_vals[-1])
print('Max tensile force =', max(rf_pos))
print('Min compressive force =', min(rf_pos))
