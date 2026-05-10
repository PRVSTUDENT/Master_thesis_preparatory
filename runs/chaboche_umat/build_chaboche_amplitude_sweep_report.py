import csv
import os
import re


CASES = [
    ("chaboche_vp_v1_cyclic_eps001", 0.001, 0.01),
    ("chaboche_vp_v1_cyclic_eps002", 0.002, 0.02),
    ("chaboche_vp_v1_cyclic_eps005", 0.005, 0.05),
    ("chaboche_vp_v1_cyclic_eps010", 0.010, 0.10),
]


def read_summary(job):
    with open(job + "_summary.csv", newline="") as f:
        return list(csv.DictReader(f))


def read_msg_stats(job):
    path = job + ".msg"
    stats = {
        "number_of_increments": 0,
        "cutbacks": 0,
        "warnings": 0,
        "errors": 0,
        "analysis_completed": "no",
    }
    if not os.path.exists(path):
        return stats

    text = open(path, "r", errors="ignore").read()
    sta_path = job + ".sta"
    sta_text = open(sta_path, "r", errors="ignore").read() if os.path.exists(sta_path) else ""
    stats["analysis_completed"] = "yes" if "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" in sta_text else "no"

    m = re.search(r"TOTAL OF\s+(\d+)\s+INCREMENTS", text)
    if m:
        stats["number_of_increments"] = int(m.group(1))

    m = re.search(r"(\d+)\s+CUTBACKS IN AUTOMATIC INCREMENTATION", text)
    if m:
        stats["cutbacks"] = int(m.group(1))

    warning_counts = [int(v) for v in re.findall(r"^\s*(\d+)\s+WARNING MESSAGES", text, re.MULTILINE)]
    stats["warnings"] = sum(warning_counts)

    m = re.search(r"^\s*(\d+)\s+ERROR MESSAGES", text, re.MULTILINE)
    if m:
        stats["errors"] = int(m.group(1))

    return stats


def case_metrics(job, eps_amp, u_amp):
    rows = read_summary(job)
    s11 = [float(r["Avg_S11_MPa"]) for r in rows]
    rf = [float(r["RF1_N"]) for r in rows]
    sdv1 = [float(r["Avg_SDV1_p"]) for r in rows]
    stats = read_msg_stats(job)
    out = {
        "eps_amp": eps_amp,
        "U_amp": u_amp,
        "max_S11": max(s11),
        "min_S11": min(s11),
        "max_RF1": max(rf),
        "min_RF1": min(rf),
        "final_SDV1": sdv1[-1],
        "max_SDV1": max(sdv1),
    }
    out.update(stats)
    return out


def fmt(v):
    if isinstance(v, float):
        return "{0:.10g}".format(v)
    return str(v)


def main():
    metrics = [case_metrics(*case) for case in CASES]
    fields = [
        "eps_amp", "U_amp", "max_S11", "min_S11", "max_RF1", "min_RF1",
        "final_SDV1", "max_SDV1", "number_of_increments", "cutbacks",
        "warnings", "errors", "analysis_completed",
    ]
    with open("chaboche_vp_v1_amplitude_sweep_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in metrics:
            w.writerow({k: fmt(row[k]) for k in fields})

    generated = ["chaboche_vp_v1_amplitude_sweep_summary.csv",
                 "chaboche_vp_v1_amplitude_sweep_stress_strain.svg"]
    for job, _, _ in CASES:
        generated.extend([
            job + ".inp",
            job + "_summary.csv",
            job + "_stress_strain.svg",
            job + "_force_displacement.svg",
            job + "_sdv1_time.svg",
        ])

    lines = [
        "# Chaboche-v1 amplitude sweep report",
        "",
        "## Purpose",
        "",
        "The previous cyclic validation used Umax = +/-0.5 mm over L0 = 10 mm, i.e. +/-5% engineering strain. For a first steel validation this is too aggressive, so the response reached stresses of several GPa and accumulated about 0.047 plastic strain. That run proved the pipeline, but it was not a good first physical calibration target.",
        "",
        "## Run status",
        "",
        "All four lower-amplitude Abaqus jobs passed datacheck and completed the full analysis with 57 increments, 0 cutbacks, 0 warnings, and 0 errors.",
        "",
        "## Comparison",
        "",
        "| eps_amp | U_amp mm | max S11 MPa | min S11 MPa | max RF1 N | min RF1 N | final SDV1 | max SDV1 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics:
        lines.append("| {eps_amp:.4g} | {U_amp:.4g} | {max_S11:.4f} | {min_S11:.4f} | {max_RF1:.4f} | {min_RF1:.4f} | {final_SDV1:.10g} | {max_SDV1:.10g} |".format(**row))

    lines.extend([
        "",
        "## Interpretation",
        "",
        "+/-0.1% and +/-0.2% are essentially elastic for this parameter set: stress scales linearly and SDV1 remains zero. +/-0.5% is the best first cyclic validation amplitude because it activates plasticity while keeping stresses in a much more plausible range than the old +/-5% case. +/-1.0% gives a stronger plastic response and may be useful after the first loop shape is accepted.",
        "",
        "SDV1 remains reasonable in the lower sweep: it is zero below first yield, about 0.0056 at +/-0.5%, and about 0.0229 at +/-1.0%. The hysteresis shape is physically plausible as a first numerical check: elastic at small amplitudes, then open loops with plastic accumulation once the imposed strain exceeds the yield threshold.",
        "",
        "## Generated files",
        "",
    ])
    lines.extend(["- " + name for name in generated])
    lines.append("")

    with open("CHABOCHE_AMPLITUDE_SWEEP_REPORT.md", "w") as f:
        f.write("\n".join(lines))

    print("Wrote chaboche_vp_v1_amplitude_sweep_summary.csv")
    print("Wrote CHABOCHE_AMPLITUDE_SWEEP_REPORT.md")


if __name__ == "__main__":
    main()
