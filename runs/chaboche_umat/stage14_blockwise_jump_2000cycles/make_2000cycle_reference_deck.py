import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE14 = ROOT / "chaboche_umat" / "stage14_blockwise_jump_2000cycles"

SRC_INP = ROOT / "chaboche_umat" / "stage12_percentage_jump_1000cycles" / "reference_1000cycles" / "chaboche_vp_v1_cyclic_eps005_1000cycles.inp"
SRC_UMAT = ROOT / "chaboche_umat" / "stage12_percentage_jump_1000cycles" / "reference_1000cycles" / "umat_chaboche_v1_with_sdvini_sigini.f"

OUT_DIR = STAGE14 / "reference_2000cycles"
OUT_INP = OUT_DIR / "chaboche_vp_v1_cyclic_eps005_2000cycles.inp"
OUT_UMAT = OUT_DIR / "umat_chaboche_v1_with_sdvini_sigini.f"
RUN_BAT = OUT_DIR / "run_2000cycle_reference.bat"
MONITOR_PY = OUT_DIR / "monitor_2000cycle_reference.py"
EXTRACT_PY = OUT_DIR / "extract_2000cycle_reference_history.py"

NEW_CYCLES = 2000
NEW_INC = 240000
JOB_NAME = "chaboche_vp_v1_cyclic_eps005_2000cycles"


def fail(message):
    raise RuntimeError(message)


def amplitude_block():
    rows = ["*AMPLITUDE, NAME=AMP_CYCLIC_2000, DEFINITION=TABULAR"]
    for cycle in range(NEW_CYCLES):
        base = float(cycle)
        rows.extend([
            "%.2f, 0.0" % base,
            "%.2f, 1.0" % (base + 0.25),
            "%.2f, 0.0" % (base + 0.50),
            "%.2f, -1.0" % (base + 0.75),
        ])
    rows.append("%.2f, 0.0" % float(NEW_CYCLES))
    return "\n".join(rows) + "\n"


def patch_static_line(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("*static"):
            if i + 1 >= len(lines):
                fail("Found *Static but no following data line.")
            old = lines[i + 1]
            lines[i + 1] = "0.001, 2000, 1.0E-08, 0.02"
            print("Patched *Static:")
            print("  old: %s" % old)
            print("  new: %s" % lines[i + 1])
            return "\n".join(lines) + "\n"
    fail("Could not find *Static block.")


def patch_step_and_load(text):
    text = text.replace("1000cycles", "2000cycles")
    text = text.replace("1000 cycles", "2000 cycles")
    text = text.replace("1000-cycle", "2000-cycle")
    text = text.replace("cycle 1000", "cycle 2000")
    text = text.replace("1000 FULLY REVERSED CYCLES", "2000 FULLY REVERSED CYCLES")
    text = text.replace("CYCLIC_1000", "CYCLIC_2000")
    text = text.replace("AMP_CYCLIC_1000", "AMP_CYCLIC_2000")
    text = re.sub(r"(inc\s*=\s*)120000", r"\g<1>%d" % NEW_INC, text, flags=re.IGNORECASE)

    amp_match = re.search(
        r"(?ms)^\*AMPLITUDE,\s*NAME=AMP_CYCLIC_2000,\s*DEFINITION=TABULAR\s*\n.*?(?=^\*\* STEP:)",
        text,
    )
    if not amp_match:
        fail("Could not find AMP_CYCLIC_2000 amplitude block to regenerate.")
    text = text[:amp_match.start()] + amplitude_block() + text[amp_match.end():]
    text = patch_static_line(text)

    if "TIME MARKS=YES" in text.upper():
        fail("TIME MARKS=YES found after patching; remove it before running.")
    if "INC=240000" not in text.upper():
        fail("Expected INC=240000 was not found.")
    if "2000.00, 0.0" not in text:
        fail("Expected amplitude endpoint 2000.00, 0.0 was not found.")
    return text


def write_run_bat():
    RUN_BAT.write_text("""@echo off
setlocal
cd /d %%~dp0

set "VSDEV=C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\Common7\\Tools\\VsDevCmd.bat"
set "SETVARS=C:\\Program Files (x86)\\Intel\\oneAPI\\setvars.bat"

call "%%VSDEV%%" -arch=amd64
if errorlevel 1 exit /b 1
call "%%SETVARS%%" intel64
if errorlevel 1 exit /b 1

abaqus job=%s_datacheck input=%s.inp user=umat_chaboche_v1_with_sdvini_sigini.f datacheck interactive ask_delete=OFF scratch=.
if errorlevel 1 exit /b 1

abaqus job=%s input=%s.inp user=umat_chaboche_v1_with_sdvini_sigini.f interactive ask_delete=OFF scratch=.
if errorlevel 1 exit /b 1

abaqus python extract_2000cycle_reference_history.py
if errorlevel 1 exit /b 1

endlocal
""" % (JOB_NAME, JOB_NAME, JOB_NAME, JOB_NAME), encoding="utf-8")


def write_monitor_py():
    MONITOR_PY.write_text("""from pathlib import Path

job = "%s"
for suffix in [".sta", ".msg"]:
    path = Path(job + suffix)
    print("--- %%s tail ---" %% path.name)
    if path.exists():
        print("\\n".join(path.read_text(errors="ignore").splitlines()[-80:]))
    else:
        print("Missing %%s" %% path)

odb = Path(job + ".odb")
if odb.exists():
    print("--- ODB ---")
    print("%%s bytes" %% odb.stat().st_size)
""" % JOB_NAME, encoding="utf-8")


def main():
    if not SRC_INP.exists():
        fail("Missing source deck: %s" % SRC_INP)
    if not SRC_UMAT.exists():
        fail("Missing source UMAT: %s" % SRC_UMAT)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text = SRC_INP.read_text(errors="ignore")
    if "TIME MARKS=YES" in text.upper():
        fail("Source deck contains TIME MARKS=YES.")

    OUT_INP.write_text(patch_step_and_load(text), encoding="utf-8")
    OUT_UMAT.write_text(SRC_UMAT.read_text(errors="ignore"), encoding="utf-8")
    write_run_bat()
    write_monitor_py()
    EXTRACT_PY.write_text((STAGE14 / "extract_2000cycle_reference_history.py").read_text(encoding="utf-8"), encoding="utf-8")

    print("Wrote %s" % OUT_INP)
    print("Wrote %s" % OUT_UMAT)
    print("Wrote %s" % RUN_BAT)
    print("Wrote %s" % MONITOR_PY)
    print("Wrote %s" % EXTRACT_PY)


if __name__ == "__main__":
    main()
