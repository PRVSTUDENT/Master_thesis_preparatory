from odbAccess import openOdb
import csv


JOB = "chaboche_vp_v1_cyclic_eps005_10cycles"
L0 = 10.0


def main():
    odb = openOdb(JOB + ".odb")
    assembly = odb.rootAssembly
    right_set = assembly.nodeSets["RIGHT_FACE"]
    right_labels = set(node.label for node in right_set.nodes[0])

    rows = []
    for step_name in odb.steps.keys():
        step = odb.steps[step_name]
        for frame in step.frames:
            t = frame.frameValue
            u1 = 0.0
            rf1 = 0.0
            s11_vals = []
            sdv1_vals = []
            sdv15_vals = []

            for v in frame.fieldOutputs["U"].values:
                if v.nodeLabel in right_labels and abs(v.data[0]) > abs(u1):
                    u1 = v.data[0]

            for v in frame.fieldOutputs["RF"].values:
                if v.nodeLabel in right_labels:
                    rf1 += v.data[0]

            for v in frame.fieldOutputs["S"].values:
                s11_vals.append(v.data[0])

            for v in frame.fieldOutputs["SDV1"].values:
                sdv1_vals.append(v.data)

            for v in frame.fieldOutputs["SDV15"].values:
                sdv15_vals.append(v.data)

            avg_s11 = sum(s11_vals) / len(s11_vals) if s11_vals else 0.0
            avg_sdv1 = sum(sdv1_vals) / len(sdv1_vals) if sdv1_vals else 0.0
            avg_sdv15 = sum(sdv15_vals) / len(sdv15_vals) if sdv15_vals else 0.0
            rows.append([t, t, u1, u1 / L0, rf1, avg_s11, avg_sdv1, avg_sdv15])

    odb.close()

    with open(JOB + "_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Time_s", "Cycle_Number", "U1_mm", "EngStrain", "RF1_N",
                    "Avg_S11_MPa", "Avg_SDV1_p", "Avg_SDV15_dp"])
        for r in rows:
            w.writerow(["%.8g" % r[0], "%.8g" % r[1], "%.10g" % r[2], "%.10g" % r[3],
                        "%.10g" % r[4], "%.10g" % r[5], "%.10g" % r[6], "%.10g" % r[7]])

    cycle_rows = []
    for cycle in range(1, 11):
        nearest = min(rows, key=lambda r: abs(r[0] - cycle))
        cycle_rows.append([cycle, nearest[0], nearest[2], nearest[5], nearest[6], nearest[7]])

    with open(JOB + "_cycle_end.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cycle", "time", "U1", "Avg_S11", "Avg_SDV1", "Avg_SDV15"])
        for r in cycle_rows:
            w.writerow(["%d" % r[0], "%.8g" % r[1], "%.10g" % r[2], "%.10g" % r[3],
                        "%.10g" % r[4], "%.10g" % r[5]])

    u = [r[2] for r in rows]
    rf = [r[4] for r in rows]
    s11 = [r[5] for r in rows]
    sdv1 = [r[6] for r in rows]
    print("Wrote", JOB + "_summary.csv")
    print("Wrote", JOB + "_cycle_end.csv")
    print("Rows =", len(rows))
    print("Max U1 =", max(u))
    print("Min U1 =", min(u))
    print("Max RF1 =", max(rf))
    print("Min RF1 =", min(rf))
    print("Max S11 =", max(s11))
    print("Min S11 =", min(s11))
    print("Final SDV1 =", sdv1[-1])
    print("Max SDV1 =", max(sdv1))


if __name__ == "__main__":
    main()
