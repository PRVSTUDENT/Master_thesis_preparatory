#!/usr/bin/env python3
import csv
import os
from odbAccess import openOdb

def extract_hysteresis(odb_file, output_csv, nset_name="RIGHT_FACE"):
    odb = openOdb(odb_file)
    assembly = odb.rootAssembly

    if nset_name not in assembly.nodeSets:
        print("Available assembly node sets:")
        for k in assembly.nodeSets.keys():
            print("  ", k)
        raise RuntimeError("Node set %s not found at assembly level" % nset_name)

    right_set = assembly.nodeSets[nset_name]
    right_labels = set(node.label for node in right_set.nodes[0])
    print("Using assembly node set %s with node labels: %s" % (nset_name, sorted(right_labels)))

    rows = []

    for step_name in odb.steps.keys():
        step = odb.steps[step_name]
        print("Processing step:", step_name)

        for frame_idx, frame in enumerate(step.frames):
            time_val = frame.frameValue

            u_max = 0.0
            rf_sum = 0.0
            s11_vals = []

            if "U" in frame.fieldOutputs:
                for v in frame.fieldOutputs["U"].values:
                    if v.nodeLabel in right_labels:
                        u_max = max(u_max, v.data[0], key=abs)

            if "RF" in frame.fieldOutputs:
                for v in frame.fieldOutputs["RF"].values:
                    if v.nodeLabel in right_labels:
                        rf_sum += v.data[0]

            if "S" in frame.fieldOutputs:
                for v in frame.fieldOutputs["S"].values:
                    s11_vals.append(v.data[0])

            s11_avg = sum(s11_vals) / len(s11_vals) if s11_vals else 0.0

            rows.append([time_val, u_max, rf_sum, s11_avg])

            if frame_idx % 5 == 0:
                print("  frame=%d time=%.6g U1=%.6g RF1=%.6g S11avg=%.6g"
                      % (frame_idx, time_val, u_max, rf_sum, s11_avg))

    with open(output_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Time_s", "Displacement_mm", "ReactionForce_N", "Avg_S11_MPa"])
        for r in rows:
            w.writerow(["%.8g" % r[0], "%.10g" % r[1], "%.10g" % r[2], "%.10g" % r[3]])

    odb.close()
    print("Wrote", output_csv)

if __name__ == "__main__":
    odb_file = "chaboche_umat_1cycle.odb"
    output_csv = "chaboche_umat_1cycle_hys.csv"

    if not os.path.exists(odb_file):
        raise RuntimeError("%s not found" % odb_file)

    extract_hysteresis(odb_file, output_csv)
