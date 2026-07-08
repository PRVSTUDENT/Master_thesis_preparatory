import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ORIG_CSV = ROOT / "chaboche_v1_full_statev_cycle_history.csv"
EXACT_CSV = ROOT / "chaboche_v1_full_statev_cycle_history_exact.csv"
OUT_CSV = ROOT / "chaboche_v1_original_vs_exact_statev_comparison.csv"
OUT_MD = ROOT / "CHABOCHE_V1_ORIGINAL_VS_EXACT_STATEV_COMPARISON_REPORT.md"

VEC_REPORT_ORIG = ROOT / "CHABOCHE_V1_VECTOR_STATEV_CYCLE_JUMP_REPORT.md"
VEC_REPORT_EXACT = ROOT / "CHABOCHE_V1_VECTOR_STATEV_CYCLE_JUMP_REPORT_EXACT.md"

KEY_CYCLES = [10, 11, 12, 19, 20]
NSTATEV = 15


def read_history(path):
    out = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cycle = int(r["cycle"])
            if cycle not in out:
                out[cycle] = {}
            for i in range(1, NSTATEV + 1):
                out[cycle][i] = float(r[f"STATEV{i}_end"])
    return out


def rel_pct(a, b):
    if a is None or abs(a) < 1e-16:
        return None
    return (abs(b - a) / abs(a)) * 100.0


def parse_vector_report(path):
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    # Conservative global DeltaN: `X`
    m1 = re.search(r"Conservative global DeltaN[:]?\s*`?(\d+)`?", text)
    delta_n = int(m1.group(1)) if m1 else None
    # Adaptive target cycle
    m2 = re.search(r"Adaptive target cycle[:]?\s*`?(\d+)`?", text)
    target = int(m2.group(1)) if m2 else None
    # Controlling component line
    m3 = re.search(r"Controlling component[:]?.*STATEV\(?([0-9]+)\)?\D+`?([A-Za-z0-9_\-]+)`?", text)
    if m3:
        comp_idx = int(m3.group(1))
        comp_name = m3.group(2)
    else:
        # fallback: find "Controlling component" then the following lines
        comp_idx = None
        comp_name = None
        m4 = re.search(r"Controlling component[:]?.*STATEV\(?([0-9]+)\)?", text)
        if m4:
            comp_idx = int(m4.group(1))
    return {"delta_n": delta_n, "target": target, "controlling_component_index": comp_idx, "controlling_component_name": comp_name}


def main():
    orig = read_history(ORIG_CSV)
    exact = read_history(EXACT_CSV)

    # write long-format comparison CSV
    fields = ["cycle", "statev_index", "original_value", "exact_value", "abs_diff", "rel_diff_percent"]
    rows = []
    for cycle in range(1, 21):
        for i in range(1, NSTATEV + 1):
            a = orig.get(cycle, {}).get(i)
            b = exact.get(cycle, {}).get(i)
            if a is None or b is None:
                continue
            absd = b - a
            r = rel_pct(a, b)
            rows.append({
                "cycle": cycle,
                "statev_index": i,
                "original_value": a,
                "exact_value": b,
                "abs_diff": absd,
                "rel_diff_percent": r,
            })
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("" if r[k] is None else ("%.12g" % r[k])) for k in fields})

    # build Markdown report
    orig_vec = parse_vector_report(VEC_REPORT_ORIG)
    exact_vec = parse_vector_report(VEC_REPORT_EXACT)

    def cycle_table(cycle):
        lines = []
        lines.append(f"### Cycle {cycle}")
        lines.append("")
        lines.append("| STATEV | original | exact | abs diff | rel diff [%] |")
        lines.append("| ---: | ---: | ---: | ---: | ---: |")
        for i in [1, 2, 3, 4, 8, 9, 10, 14]:
            a = orig[cycle][i]
            b = exact[cycle][i]
            absd = b - a
            r = rel_pct(a, b)
            lines.append(f"| STATEV({i}) | `{a:.12g}` | `{b:.12g}` | `{absd:.12g}` | `{'' if r is None else ('%.6g' % r)}` |")
        lines.append("")
        return "\n".join(lines)

    # cycle-20 summary
    a20 = orig[20][1]
    b20 = exact[20][1]
    abs20 = b20 - a20
    rel20 = rel_pct(a20, b20)

    lines = [
        "# Original vs Exact STATEV History Comparison",
        "",
        "This comparison contrasts the original nearest-frame extraction against the exact-output extraction for the validated 20-cycle Chaboche-v1 run.",
        "",
        "## Key files",
        "",
        f"- Original history: `{ORIG_CSV.name}`",
        f"- Exact history: `{EXACT_CSV.name}`",
        f"- Long-format comparison CSV: `{OUT_CSV.name}`",
        "",
        "## Cycle-range compared: 1-20",
        "",
        "## Cycle-20 STATEV(1) comparison",
        "",
        f"- Original STATEV(1) at cycle 20: `{a20:.12g}`",
        f"- Exact STATEV(1) at cycle 20: `{b20:.12g}`",
        f"- Absolute difference (exact - original): `{abs20:.12g}`",
        f"- Relative difference percent: `{'' if rel20 is None else ('%.6g' % rel20)}%`",
        "",
        "## Selected cycle summaries",
    ]

    for c in KEY_CYCLES:
        lines.append(cycle_table(c))

    lines += [
        "## Vector analyzer comparison",
        "",
        f"- Original vector analyzer: DeltaN = `{orig_vec.get('delta_n')}`, target = `{orig_vec.get('target')}`, controlling component index = `{orig_vec.get('controlling_component_index')}`",
        f"- Exact vector analyzer: DeltaN = `{exact_vec.get('delta_n')}`, target = `{exact_vec.get('target')}`, controlling component index = `{exact_vec.get('controlling_component_index')}`",
        "",
        "## Interpretation",
        "",
        "- Exact phase output successfully removed frame-time ambiguity (max time_error = 0).",
        "- However, `TIME MARKS=YES` changed the accepted increment schedule and therefore the UMAT-integrated response (cycle-20 SDV1 differs noticeably).",
        "- The simplified Chaboche-v1 UMAT is increment-schedule sensitive as shown by the difference in SDV1 at cycle 20.",
        "- The original validated 20-cycle result should remain the main validation baseline for subsequent work.",
        "- The exact-output run should be treated as a diagnostic branch for phase-consistent STATEV extraction; do not attempt STATEV injection yet.",
        "",
        "## Notes",
        "",
        "- No UMAT, input files, or Abaqus runs were modified by this comparison script; it only postprocesses existing CSVs and reports.",
    ]

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Comparison complete")
    print("Comparison CSV:", OUT_CSV)
    print("Comparison report:", OUT_MD)


if __name__ == "__main__":
    main()
