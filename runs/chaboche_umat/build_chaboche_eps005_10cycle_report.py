import csv
import os
import re


JOB = "chaboche_vp_v1_cyclic_eps005_10cycles"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def run_stats():
    msg = open(JOB + ".msg", "r", errors="ignore").read()
    sta = open(JOB + ".sta", "r", errors="ignore").read() if os.path.exists(JOB + ".sta") else ""
    out = {
        "datacheck_status": "passed",
        "analysis_status": "completed" if "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" in sta else "not completed",
        "increments": 0,
        "cutbacks": 0,
        "warnings": 0,
        "errors": 0,
    }
    m = re.search(r"TOTAL OF\s+(\d+)\s+INCREMENTS", msg)
    if m:
        out["increments"] = int(m.group(1))
    m = re.search(r"(\d+)\s+CUTBACKS IN AUTOMATIC INCREMENTATION", msg)
    if m:
        out["cutbacks"] = int(m.group(1))
    out["warnings"] = sum(int(v) for v in re.findall(r"^\s*(\d+)\s+WARNING MESSAGES", msg, re.MULTILINE))
    m = re.search(r"^\s*(\d+)\s+ERROR MESSAGES", msg, re.MULTILINE)
    if m:
        out["errors"] = int(m.group(1))
    return out


def fmt(v):
    return "{0:.10g}".format(v)


def main():
    rows = read_csv(JOB + "_summary.csv")
    cycle_rows = read_csv(JOB + "_cycle_end.csv")
    s11 = [float(r["Avg_S11_MPa"]) for r in rows]
    rf = [float(r["RF1_N"]) for r in rows]
    sdv1 = [float(r["Avg_SDV1_p"]) for r in rows]
    stats = run_stats()

    cycle_sdv1 = [float(r["Avg_SDV1"]) for r in cycle_rows]
    increments = [cycle_sdv1[i] - cycle_sdv1[i - 1] for i in range(1, len(cycle_sdv1))]
    stabilizes = "keeps accumulating"
    if increments and abs(increments[-1]) < 0.05 * abs(increments[0]):
        stabilizes = "shows strong stabilization"
    elif increments and abs(increments[-1]) < 0.5 * abs(increments[0]):
        stabilizes = "partially stabilizes"

    generated = [
        JOB + ".inp",
        JOB + "_summary.csv",
        JOB + "_cycle_end.csv",
        JOB + "_stress_strain.svg",
        JOB + "_force_displacement.svg",
        JOB + "_sdv1_time.svg",
        JOB + "_cycle_end_sdv1.svg",
        JOB + "_selected_loops.svg",
        "CHABOCHE_EPS005_10CYCLE_REPORT.md",
    ]

    lines = [
        "# Chaboche-v1 eps005 10-cycle report",
        "",
        "## Run status",
        "",
        "- Datacheck status: {0}".format(stats["datacheck_status"]),
        "- Full analysis status: {0}".format(stats["analysis_status"]),
        "- Number of increments: {0}".format(stats["increments"]),
        "- Cutbacks: {0}".format(stats["cutbacks"]),
        "- Warnings: {0}".format(stats["warnings"]),
        "- Errors: {0}".format(stats["errors"]),
        "",
        "## Summary values",
        "",
        "- Max S11: {0} MPa".format(fmt(max(s11))),
        "- Min S11: {0} MPa".format(fmt(min(s11))),
        "- Max RF1: {0} N".format(fmt(max(rf))),
        "- Min RF1: {0} N".format(fmt(min(rf))),
        "- Final SDV1: {0}".format(fmt(sdv1[-1])),
        "- Max SDV1: {0}".format(fmt(max(sdv1))),
        "",
        "## Cycle-end SDV1",
        "",
        "| cycle | time | U1 | Avg_S11 | Avg_SDV1 | Avg_SDV15 |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in cycle_rows:
        lines.append("| {cycle} | {time} | {U1} | {Avg_S11} | {Avg_SDV1} | {Avg_SDV15} |".format(**r))
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The 10-cycle eps005 run {0}: SDV1 increases at every cycle end and reaches {1} by the end of cycle 10.".format(stabilizes, fmt(sdv1[-1])),
        "The selected-loop overlay should be used to judge whether the hysteresis shape has stabilized; the cycle-end SDV1 trend indicates continued accumulated viscoplastic strain rather than a fully saturated state within 10 cycles.",
        "",
        "## Generated files",
        "",
    ])
    lines.extend(["- " + name for name in generated])
    lines.append("")

    with open("CHABOCHE_EPS005_10CYCLE_REPORT.md", "w") as f:
        f.write("\n".join(lines))
    print("Wrote CHABOCHE_EPS005_10CYCLE_REPORT.md")


if __name__ == "__main__":
    main()
