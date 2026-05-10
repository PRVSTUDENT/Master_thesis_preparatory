from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_INP = ROOT / "chaboche_vp_v1_cyclic_eps005_20cycles.inp"
TARGET_INP = ROOT / "chaboche_vp_v1_cyclic_eps005_20cycles_exact_cycle_outputs.inp"
REPORT = ROOT / "CHABOCHE_V1_EXACT_PHASE_OUTPUT_PREP_REPORT.md"

PREVIOUS_MAX_TIME_ERROR = 0.00974273681641

OLD_OUTPUT_BLOCK = """*OUTPUT, FIELD, FREQUENCY=1
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, SDV

*OUTPUT, HISTORY, FREQUENCY=1
*NODE OUTPUT, NSET=RIGHT_FACE
U1, RF1"""

NEW_OUTPUT_BLOCK = """** Exact cycle-end output request for Level-2 STATEV phase consistency
** Output is requested at integer cycle times using a 1.0 time interval.
** TIME MARKS=YES asks Abaqus to adjust increments so output is written at
** the requested marks rather than only at the nearest accepted increment.
*OUTPUT, FIELD, TIME INTERVAL=1.0, TIME MARKS=YES
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, SDV

*OUTPUT, HISTORY, TIME INTERVAL=1.0, TIME MARKS=YES
*NODE OUTPUT, NSET=RIGHT_FACE
U1, RF1"""


def write_report():
    lines = [
        "# Chaboche-v1 Exact Phase Output Preparation Report",
        "",
        "This report documents a copied Abaqus input deck prepared for exact cycle-end field output. It is a preparation step before repeating full STATEV extraction and vector-valued cycle-jump analysis.",
        "",
        "## Files",
        "",
        f"- Source input deck: `{SOURCE_INP.name}`",
        f"- Copied exact-output deck: `{TARGET_INP.name}`",
        "",
        "The original input deck was not modified.",
        "",
        "## Why Exact Phase-Point Output Is Needed",
        "",
        "The previous full STATEV extraction used the nearest available ODB frame to each integer cycle-end time. The maximum absolute time error was:",
        "",
        f"- `{PREVIOUS_MAX_TIME_ERROR}`",
        "",
        "This is acceptable for preliminary postprocessing, but it is not ideal for full internal-state cycle jumping. Backstress components `STATEV(2-4)` and viscoplastic strain components `STATEV(8-10)` are phase-sensitive, so a small offset from the intended cycle-end point can change the apparent cycle-to-cycle increments.",
        "",
        "## Output-Control Change",
        "",
        "The copied deck replaces increment-frequency output with time-marked output:",
        "",
        "```text",
        "*OUTPUT, FIELD, TIME INTERVAL=1.0, TIME MARKS=YES",
        "*NODE OUTPUT",
        "U, RF",
        "*ELEMENT OUTPUT",
        "S, SDV",
        "",
        "*OUTPUT, HISTORY, TIME INTERVAL=1.0, TIME MARKS=YES",
        "*NODE OUTPUT, NSET=RIGHT_FACE",
        "U1, RF1",
        "```",
        "",
        "This requests output at integer step times `1, 2, ..., 20` for the 20-cycle step.",
        "",
        "## Preserved Model Content",
        "",
        "- Geometry: unchanged",
        "- Material constants: unchanged",
        "- UMAT expectation: unchanged",
        "- Boundary conditions: unchanged",
        "- Amplitude definition: unchanged",
        "- Total step time: unchanged",
        "- Number of cycles: unchanged",
        "",
        "## Status",
        "",
        "- Abaqus was not run automatically.",
        "- The UMAT was not modified.",
        "- The original input deck was not modified.",
        "- No STATEV injection is attempted.",
        "",
        "## Implication",
        "",
        "This prepares a cleaner reference ODB with exact cycle-end field output. After running the copied deck, the full STATEV extraction and vector-valued STATEV cycle-jump analyzer should be repeated to remove phase-point ambiguity before any restart or injected-state Abaqus continuation is attempted.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    text = SOURCE_INP.read_text(encoding="utf-8")
    if OLD_OUTPUT_BLOCK not in text:
        raise RuntimeError("Could not find the original output block to replace.")
    updated = text.replace(OLD_OUTPUT_BLOCK, NEW_OUTPUT_BLOCK)
    TARGET_INP.write_text(updated, encoding="utf-8")
    write_report()
    print("Exact phase output deck prepared")
    print("Source:", SOURCE_INP)
    print("Target:", TARGET_INP)
    print("Report:", REPORT)
    print("Abaqus was not run.")


if __name__ == "__main__":
    main()
