import csv
import os


ROOT = r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat"

HISTORY_CSV = os.path.join(ROOT, "chaboche_vp_v1_cyclic_eps005_50cycles_cycle_history.csv")
OUT_CSV = os.path.join(
    ROOT,
    "stage9_thousand_cycle_error_accumulation",
    "prediction_scan",
    "stage9_long_horizon_prediction_scan.csv",
)

BASE_CYCLE = 10
MEAN_START = 2
MEAN_END = 10

TARGET_CYCLES = [20, 30, 40, 50, 100, 200, 500, 1000, 2000]

NSTATEV = 15
STRESS_COMPONENTS = ["S11", "S22", "S33", "S12", "S13", "S23"]


def f(x):
    if x is None or x == "":
        return None
    return float(x)


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / float(len(values)) if values else None


def fmt(x):
    if x is None:
        return ""
    return "%.12g" % x


rows = []
with open(HISTORY_CSV, "r") as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        parsed = {"cycle": int(row["cycle"])}
        for i in range(1, NSTATEV + 1):
            parsed["STATEV%d_end" % i] = f(row["STATEV%d_end" % i])
            parsed["Delta_STATEV%d" % i] = f(row["Delta_STATEV%d" % i])
        for name in STRESS_COMPONENTS:
            parsed[name] = f(row[name])
            parsed["Delta_%s" % name] = f(row["Delta_%s" % name])
        rows.append(parsed)


def get_cycle(cycle):
    for row in rows:
        if row["cycle"] == cycle:
            return row
    return None


base = get_cycle(BASE_CYCLE)
window = [r for r in rows if MEAN_START <= r["cycle"] <= MEAN_END]

statev_mean = {}
stress_mean = {}

for i in range(1, NSTATEV + 1):
    statev_mean[i] = mean([r["Delta_STATEV%d" % i] for r in window])

for name in STRESS_COMPONENTS:
    stress_mean[name] = mean([r["Delta_%s" % name] for r in window])

fields = [
    "target_cycle",
    "delta_n_from_cycle10",
    "pred_STATEV1",
    "pred_S11",
    "exact_available",
    "exact_STATEV1",
    "exact_S11",
    "STATEV1_rel_error_percent_if_available",
    "S11_rel_error_percent_if_available",
]

with open(OUT_CSV, "w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()

    for target in TARGET_CYCLES:
        delta_n = target - BASE_CYCLE
        pred_statev1 = base["STATEV1_end"] + delta_n * statev_mean[1]
        pred_s11 = base["S11"] + delta_n * stress_mean["S11"]

        exact = get_cycle(target)
        exact_available = exact is not None

        exact_statev1 = exact["STATEV1_end"] if exact else None
        exact_s11 = exact["S11"] if exact else None

        statev1_err = None
        s11_err = None

        if exact_available and abs(exact_statev1) > 1e-30:
            statev1_err = 100.0 * abs(pred_statev1 - exact_statev1) / abs(exact_statev1)

        if exact_available and abs(exact_s11) > 1e-30:
            s11_err = 100.0 * abs(pred_s11 - exact_s11) / abs(exact_s11)

        writer.writerow({
            "target_cycle": target,
            "delta_n_from_cycle10": delta_n,
            "pred_STATEV1": fmt(pred_statev1),
            "pred_S11": fmt(pred_s11),
            "exact_available": "yes" if exact_available else "no",
            "exact_STATEV1": fmt(exact_statev1),
            "exact_S11": fmt(exact_s11),
            "STATEV1_rel_error_percent_if_available": fmt(statev1_err),
            "S11_rel_error_percent_if_available": fmt(s11_err),
        })

print("Wrote:", OUT_CSV)
