import os
import re


ROOT = r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat"

SRC_INP = os.path.join(ROOT, "chaboche_vp_v1_cyclic_eps005_50cycles.inp")

OUT_DIR = os.path.join(ROOT, "stage10_100cycle_reference", "reference_100cycles")
OUT_INP = os.path.join(OUT_DIR, "chaboche_vp_v1_cyclic_eps005_100cycles.inp")

os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC_INP, "r") as f:
    text = f.read()

# ------------------------------------------------------------
# Build 100-cycle amplitude table:
# one cycle: 0 -> +1 -> 0 -> -1 -> 0
# period = 1.0, final time = 100.0
# ------------------------------------------------------------
amp_lines = []
amp_lines.append("*AMPLITUDE, NAME=AMP_CYCLIC_100, DEFINITION=TABULAR\n")

for cycle in range(100):
    t0 = float(cycle)
    points = [
        (t0 + 0.00, 0.0),
        (t0 + 0.25, 1.0),
        (t0 + 0.50, 0.0),
        (t0 + 0.75, -1.0),
    ]
    for t, a in points:
        amp_lines.append(f"{t:.2f}, {a:.1f}\n")

amp_lines.append("100.00, 0.0\n")
amp_block = "".join(amp_lines)

# ------------------------------------------------------------
# Replace the full 50-cycle amplitude block.
# It starts at *AMPLITUDE and ends just before the next comment/step.
# ------------------------------------------------------------
pattern = (
    r"\*AMPLITUDE, NAME=AMP_CYCLIC_50, DEFINITION=TABULAR\n"
    r".*?"
    r"(?=\n\*\* STEP|\n\*STEP)"
)

text = re.sub(pattern, amp_block.rstrip(), text, flags=re.DOTALL)

# Header/comment replacements.
text = text.replace(
    "Chaboche-v1 UMAT - 50 cyclic tension-compression cycles, eps_amp=0.005",
    "Chaboche-v1 UMAT - 100 cyclic tension-compression cycles, eps_amp=0.005",
)
text = text.replace(
    "** CYCLIC AMPLITUDE: 50 cycles, 0 -> +1 -> 0 -> -1 -> 0 per cycle",
    "** CYCLIC AMPLITUDE: 100 cycles, 0 -> +1 -> 0 -> -1 -> 0 per cycle",
)

# Step name and increment limit.
text = text.replace(
    "*STEP, NAME=CYCLIC_50, NLGEOM=NO, INC=6000",
    "*STEP, NAME=CYCLIC_100, NLGEOM=NO, INC=12000",
)

# Static time period: keep same increment controls, extend total time.
text = text.replace(
    "0.001, 50.0, 1.0E-08, 0.02",
    "0.001, 100.0, 1.0E-08, 0.02",
)

# Boundary amplitude name.
text = text.replace(
    "*BOUNDARY, AMPLITUDE=AMP_CYCLIC_50",
    "*BOUNDARY, AMPLITUDE=AMP_CYCLIC_100",
)

with open(OUT_INP, "w") as f:
    f.write(text)

print("Wrote:", OUT_INP)
