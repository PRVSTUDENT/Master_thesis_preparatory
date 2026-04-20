import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def read_csv(path):
    u = []
    rf = []
    with open(path, 'r') as f:
        r = csv.DictReader(f)
        for row in r:
            u.append(float(row['U1']))
            rf.append(float(row['RF_total_positive']))
    return u, rf

u_lin, rf_lin = read_csv('lin_kin_2cycle_hys.csv')
u_com, rf_com = read_csv('combined_2cycle_hys.csv')
u_tun, rf_tun = read_csv('combined_2cycle_tuned_hys.csv')

plt.figure(figsize=(7,5))
plt.plot(u_lin, rf_lin, lw=1.8, label='Linear kinematic 2-cycle')
plt.plot(u_com, rf_com, lw=1.8, label='Combined 2-cycle')
plt.plot(u_tun, rf_tun, lw=1.8, label='Combined tuned 2-cycle')
plt.xlabel('U1')
plt.ylabel('Reaction force')
plt.title('Hysteresis comparison: linear vs combined vs tuned')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('compare_lin_combined_tuned_2cycle.png', dpi=200)

print('Wrote: compare_lin_combined_tuned_2cycle.png')
print('Linear max force', max(rf_lin))
print('Combined max force', max(rf_com))
print('Tuned max force', max(rf_tun))
print('Linear min force', min(rf_lin))
print('Combined min force', min(rf_com))
print('Tuned min force', min(rf_tun))
