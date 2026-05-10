import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
UMAT_PATH = ROOT / "umat" / "chaboche_vp_v1_working.f"
INP_PATH = ROOT / "chaboche_vp_v1_cyclic_eps005_20cycles.inp"
CSV_PATH = ROOT / "chaboche_v1_statev_inventory.csv"
REPORT_PATH = ROOT / "CHABOCHE_V1_STATEV_INVENTORY_REPORT.md"


STATEV_LAYOUT = [
    {
        "indices": [1],
        "symbol": "p",
        "meaning": "Accumulated viscoplastic strain",
        "candidate": "yes",
        "classification": "required for restart/injection",
        "notes": "Primary scalar cycle-evolution marker used by the current Level-1 cycle-jump predictor. It controls isotropic hardening through R = QISO*(1-exp(-BISO*p)).",
    },
    {
        "indices": list(range(2, 8)),
        "symbol": "X11, X22, X33, X12, X13, X23",
        "meaning": "Backstress tensor components",
        "candidate": "yes",
        "classification": "required for restart/injection",
        "notes": "Read into XOLD(I), used in deviatoric overstress ETA, and updated to XNEW(I) with Armstrong-Frederick style recovery.",
    },
    {
        "indices": list(range(8, 14)),
        "symbol": "Evp11, Evp22, Evp33, Evp12, Evp13, Evp23",
        "meaning": "Viscoplastic strain tensor components",
        "candidate": "yes",
        "classification": "required for restart/injection",
        "notes": "Read into EPOLD(I) and updated to EPNEW(I)=EPOLD(I)+DP*NFLOW(I). Required to preserve the stored inelastic strain history.",
    },
    {
        "indices": [14],
        "symbol": "RISO",
        "meaning": "Current isotropic hardening stress",
        "candidate": "conditional/recomputable",
        "classification": "diagnostic or recomputable",
        "notes": "Written as QISO*(1-exp(-BISO*STATEV(1))). The UMAT recomputes RISO from SDV1 before yield evaluation, so STATEV(14) is convenient output but not independent if SDV1 and material constants are known.",
    },
    {
        "indices": [15],
        "symbol": "DP",
        "meaning": "Last viscoplastic multiplier increment",
        "candidate": "no",
        "classification": "diagnostic only",
        "notes": "Written at the end of each increment as the last local increment. Useful for diagnostics and output as SDV15, but not a persistent memory variable needed to reconstruct the constitutive state.",
    },
]


def read_lines(path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def find_depvar_count(path):
    lines = read_lines(path)
    for i, line in enumerate(lines):
        if line.strip().upper().startswith("*DEPVAR"):
            for following in lines[i + 1:]:
                stripped = following.strip()
                if not stripped or stripped.startswith("**"):
                    continue
                if stripped.startswith("*"):
                    return None
                try:
                    return int(stripped.split(",")[0])
                except ValueError:
                    return None
    return None


def statev_occurrences(lines):
    occurrences = {}
    pattern = re.compile(r"STATEV\s*\(([^)]+)\)", re.IGNORECASE)
    for line_no, line in enumerate(lines, start=1):
        for match in pattern.finditer(line):
            expr = match.group(1).strip().upper().replace(" ", "")
            access = "write/update" if "=" in line and line.index("=") > match.start() else "read"
            occurrences.setdefault(expr, []).append({
                "line": line_no,
                "access": access,
                "code": line.rstrip(),
            })
    return occurrences


def expand_occurrence_notes(index):
    notes = []
    if index == 1:
        keys = ["1"]
    elif 2 <= index <= 7:
        keys = ["I+1"]
    elif 8 <= index <= 13:
        keys = ["I+7"]
    elif index == 14:
        keys = ["14"]
    elif index == 15:
        keys = ["15"]
    else:
        keys = []
    return keys


def collect_access(index, occurrences):
    keys = expand_occurrence_notes(index)
    accesses = []
    source_lines = []
    for key in keys:
        for occurrence in occurrences.get(key, []):
            accesses.append(occurrence["access"])
            source_lines.append(f"line {occurrence['line']}: {occurrence['code'].strip()}")
    if not accesses:
        return "not found", "no", ""
    if any("write" in item for item in accesses) and any(item == "read" for item in accesses):
        access = "read/write"
    elif any("write" in item for item in accesses):
        access = "write"
    else:
        access = "read"
    updated = "yes" if any("write" in item for item in accesses) else "no"
    return access, updated, " | ".join(source_lines)


def build_rows(occurrences):
    rows = []
    for group in STATEV_LAYOUT:
        for offset, index in enumerate(group["indices"]):
            if group["symbol"].startswith("X"):
                symbol = group["symbol"].split(", ")[offset]
            elif group["symbol"].startswith("Evp"):
                symbol = group["symbol"].split(", ")[offset]
            else:
                symbol = group["symbol"]
            access, updated, source_note = collect_access(index, occurrences)
            notes = group["notes"]
            if source_note:
                notes = f"{notes} Source: {source_note}"
            rows.append({
                "statev_index": index,
                "symbol_or_name": symbol,
                "inferred_meaning": group["meaning"],
                "read_or_write": access,
                "updated_in_umat": updated,
                "candidate_for_cycle_jump": group["candidate"],
                "classification": group["classification"],
                "notes": notes,
            })
    return rows


def write_csv(rows):
    fieldnames = [
        "statev_index",
        "symbol_or_name",
        "inferred_meaning",
        "read_or_write",
        "updated_in_umat",
        "candidate_for_cycle_jump",
        "classification",
        "notes",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows, depvar_count):
    required = [r for r in rows if r["classification"] == "required for restart/injection"]
    diagnostic = [r for r in rows if r["classification"] in ("diagnostic only", "diagnostic or recomputable")]
    unclear = [r for r in rows if "unclear" in r["classification"]]

    lines = [
        "# Chaboche-v1 STATEV Inventory Report",
        "",
        "This report inventories the solution-dependent state variables used by the active Chaboche-v1 UMAT. It is a preparation step for a future Level-2 restart/state-variable injection workflow.",
        "",
        "## Source Files",
        "",
        f"- Active UMAT inspected: `{UMAT_PATH.relative_to(ROOT)}`",
        f"- Representative input deck checked for DEPVAR count: `{INP_PATH.name}`",
        f"- DEPVAR count in input deck: `{depvar_count}`",
        "",
        "No UMAT files were modified, no Abaqus input files were modified, and Abaqus was not rerun.",
        "",
        "## STATEV Layout",
        "",
        "| STATEV index | Symbol/name | Inferred meaning | Access | Cycle-jump candidate | Classification |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['statev_index']} | `{row['symbol_or_name']}` | {row['inferred_meaning']} | "
            f"{row['read_or_write']} | {row['candidate_for_cycle_jump']} | {row['classification']} |"
        )

    lines += [
        "",
        "## Required for Restart/Injection",
        "",
    ]
    for row in required:
        lines.append(f"- `STATEV({row['statev_index']})` `{row['symbol_or_name']}`: {row['inferred_meaning']}")

    lines += [
        "",
        "## Diagnostic or Recomputable",
        "",
    ]
    for row in diagnostic:
        lines.append(f"- `STATEV({row['statev_index']})` `{row['symbol_or_name']}`: {row['inferred_meaning']}")

    lines += [
        "",
        "## Unclear / Needs Manual Confirmation",
        "",
    ]
    if unclear:
        for row in unclear:
            lines.append(f"- `STATEV({row['statev_index']})` `{row['symbol_or_name']}`")
    else:
        lines.append("- None identified from the active UMAT source.")

    lines += [
        "",
        "## Implication for Nesnas-Saanouni Cycle Jump",
        "",
        "The current Level-1 predictor jumps only `STATEV(1)`, the accumulated viscoplastic strain. That is sufficient for a postprocessing validation of cycle-space extrapolation, but it is not sufficient for a restart or injected-state Abaqus continuation.",
        "",
        "For a Level-2 restart/state-variable injection test, the independent UMAT memory should include at least:",
        "",
        "- `STATEV(1)`: accumulated viscoplastic strain `p`",
        "- `STATEV(2-7)`: backstress tensor components",
        "- `STATEV(8-13)`: viscoplastic strain tensor components",
        "",
        "`STATEV(14)` can be recomputed from `STATEV(1)` and the material constants in this UMAT, while `STATEV(15)` is a last-increment diagnostic. A conservative injection workflow may still initialize all 15 values for output consistency, but the physically independent state is concentrated in `STATEV(1-13)`.",
        "",
        "The next implementation stage should therefore extrapolate a consistent vector of state variables, not only SDV1. The smallest safe adaptive jump over the selected state components should control the full material-state jump.",
        "",
        "## Generated File",
        "",
        f"- `{CSV_PATH.name}`",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    lines = read_lines(UMAT_PATH)
    occurrences = statev_occurrences(lines)
    rows = build_rows(occurrences)
    depvar_count = find_depvar_count(INP_PATH)
    write_csv(rows)
    write_report(rows, depvar_count)
    print("STATEV inventory complete")
    print("UMAT:", UMAT_PATH)
    print("DEPVAR count:", depvar_count)
    print("CSV:", CSV_PATH)
    print("Report:", REPORT_PATH)


if __name__ == "__main__":
    main()
