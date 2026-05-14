import os
import re


ROOT = r"D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat"

NCYCLES = 500
INC_LIMIT = 60000

SRC_INP = os.path.join(ROOT, "chaboche_vp_v1_cyclic_eps005_50cycles.inp")
OUT_DIR = os.path.join(ROOT, "stage11_500cycle_reference", "reference_500cycles")
OUT_INP = os.path.join(OUT_DIR, "chaboche_vp_v1_cyclic_eps005_500cycles.inp")

os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC_INP, "r") as f:
    text = f.read()

amp_lines = []
amp_lines.append("*AMPLITUDE, NAME=AMP_CYCLIC_500, DEFINITION=TABULAR\n")

for cycle in range(NCYCLES):
    t0 = float(cycle)
    for t, a in [
        (t0 + 0.00, 0.0),
        (t0 + 0.25, 1.0),
        (t0 + 0.50, 0.0),
        (t0 + 0.75, -1.0),
    ]:
        amp_lines.append(f"{t:.2f}, {a:.1f}\n")

amp_lines.append(f"{NCYCLES:.2f}, 0.0\n")
amp_block = "".join(amp_lines)

pattern = (
    r"\*AMPLITUDE, NAME=AMP_CYCLIC_50, DEFINITION=TABULAR\n"
    r".*?"
    r"(?=\n\*\* STEP|\n\*STEP)"
)

text = re.sub(pattern, amp_block.rstrip(), text, flags=re.DOTALL)

text = text.replace(
    "Chaboche-v1 UMAT - 50 cyclic tension-compression cycles, eps_amp=0.005",
    "Chaboche-v1 UMAT - 500 cyclic tension-compression cycles, eps_amp=0.005",
)

text = text.replace(
    "** CYCLIC AMPLITUDE: 50 cycles, 0 -> +1 -> 0 -> -1 -> 0 per cycle",
    "** CYCLIC AMPLITUDE: 500 cycles, 0 -> +1 -> 0 -> -1 -> 0 per cycle",
)

text = text.replace(
    "*STEP, NAME=CYCLIC_50, NLGEOM=NO, INC=6000",
    f"*STEP, NAME=CYCLIC_500, NLGEOM=NO, INC={INC_LIMIT}",
)

text = text.replace(
    "0.001, 50.0, 1.0E-08, 0.02",
    "0.001, 500.0, 1.0E-08, 0.02",
)

text = text.replace(
    "*BOUNDARY, AMPLITUDE=AMP_CYCLIC_50",
    "*BOUNDARY, AMPLITUDE=AMP_CYCLIC_500",
)

with open(OUT_INP, "w") as f:
    f.write(text)

print("Wrote:", OUT_INP)
