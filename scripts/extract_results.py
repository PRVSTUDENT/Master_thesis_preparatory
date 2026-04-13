# Run with: abaqus python scripts/extract_results.py -- <args>
"""
extract_results.py
==================
Opens an Abaqus ODB file and extracts reaction-force and displacement history
output to a CSV file.

Usage (must run inside the Abaqus Python kernel)
-------------------------------------------------
    abaqus python scripts/extract_results.py -- \\
        --odb    models/<job_name>.odb \\
        --set    LOAD_NODE \\
        --step   Step-1 \\
        --output results/<job_name>_fd.csv

Arguments
---------
--odb       Path to the Abaqus output database (.odb)
--set       Name of the node set where history output was requested
--step      Name of the Abaqus step to read (default: Step-1)
--output    Path to the output CSV file (default: results/force_disp.csv)
--rf-key    History variable name for reaction force (default: RF2)
--u-key     History variable name for displacement   (default: U2)
"""

import argparse
import csv
import os
import sys


def parse_args(argv=None):
    """Parse command-line arguments (everything after the ``--`` separator)."""
    # Abaqus passes the script arguments after a bare '--'
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
    else:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Extract force-displacement data from an Abaqus ODB."
    )
    parser.add_argument("--odb", required=True, help="Path to the ODB file.")
    parser.add_argument(
        "--set", dest="node_set", default="LOAD_NODE",
        help="Node set name containing history output (default: LOAD_NODE)."
    )
    parser.add_argument(
        "--step", default="Step-1",
        help="Step name to read (default: Step-1)."
    )
    parser.add_argument(
        "--output", default=os.path.join("results", "force_disp.csv"),
        help="Output CSV path (default: results/force_disp.csv)."
    )
    parser.add_argument(
        "--rf-key", default="RF2",
        help="History output key for reaction force (default: RF2)."
    )
    parser.add_argument(
        "--u-key", default="U2",
        help="History output key for displacement (default: U2)."
    )
    return parser.parse_args(argv)


def extract_history(odb_path, node_set_name, step_name, rf_key, u_key):
    """
    Read reaction force and displacement histories from the ODB.

    Returns
    -------
    list of dict
        Each entry has keys: ``time``, ``displacement_mm``, ``force_N``.
    """
    # Lazy import — only available when running inside Abaqus Python
    from odbAccess import openOdb  # noqa: F401

    odb = openOdb(odb_path, readOnly=True)

    try:
        step = odb.steps[step_name]
    except KeyError:
        available = list(odb.steps.keys())
        odb.close()
        raise KeyError(
            "Step '{}' not found. Available steps: {}".format(step_name, available)
        )

    # History regions are keyed by "Node <set_name>" or the set name directly
    hist_region = None
    for key in step.historyRegions.keys():
        if node_set_name.upper() in key.upper():
            hist_region = step.historyRegions[key]
            break

    if hist_region is None:
        odb.close()
        raise KeyError(
            "Node set '{}' not found in history regions of step '{}'.\n"
            "Available regions: {}".format(
                node_set_name, step_name,
                list(step.historyRegions.keys())
            )
        )

    try:
        rf_data = hist_region.historyOutputs[rf_key].data
        u_data = hist_region.historyOutputs[u_key].data
    except KeyError as exc:
        odb.close()
        available_keys = list(hist_region.historyOutputs.keys())
        raise KeyError(
            "Output key {} not found. Available keys: {}".format(exc, available_keys)
        )

    odb.close()

    # Pair by index (both lists should have the same length)
    records = []
    for (t_rf, rf), (t_u, u) in zip(rf_data, u_data):
        records.append(
            {
                "time": t_rf,
                "displacement_mm": u,
                "force_N": rf,
            }
        )

    return records


def write_csv(records, output_path):
    """Write the extracted records to a CSV file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fieldnames = ["time", "displacement_mm", "force_N"]
    with open(output_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print("Wrote {} records to: {}".format(len(records), output_path))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args.odb):
        sys.exit("ODB file not found: {}".format(args.odb))

    records = extract_history(
        args.odb, args.node_set, args.step, args.rf_key, args.u_key
    )
    write_csv(records, args.output)
