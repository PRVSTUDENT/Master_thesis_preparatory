from __future__ import annotations

import argparse
import shutil
from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = STAGE_DIR / "stage16n_1000cycle_pilot"
SOURCE_JOB = "stage16n_plate_hole_neml_equiv_1000cycles"
UMAT_NAME = "stage16n_neml_equivalent_chaboche_umat.for"
EXTRACTOR = "stage16n_extract_hysteresis_and_local_states.py"


def truncate_deck(source: Path, target: Path, cycles: int) -> None:
    lines = source.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    completed_steps = 0
    for line in lines:
        out.append(line)
        if line.strip().upper() == "*END STEP":
            completed_steps += 1
            if completed_steps >= cycles:
                break
    if completed_steps < cycles:
        raise RuntimeError(f"Source deck ended after {completed_steps} cycles, requested {cycles}")
    target.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=50)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else STAGE_DIR / "stage16n_cpu_scaling_benchmark" / f"cycles_{args.cycles:04d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    job = f"stage16n_scaling_{args.cycles:04d}cycles"

    source_inp = SOURCE_DIR / f"{SOURCE_JOB}.inp"
    if not source_inp.exists():
        raise RuntimeError(f"Missing source deck: {source_inp}")

    truncate_deck(source_inp, out_dir / f"{job}.inp", args.cycles)
    shutil.copy2(SOURCE_DIR / UMAT_NAME, out_dir / UMAT_NAME)
    shutil.copy2(STAGE_DIR / EXTRACTOR, out_dir / EXTRACTOR)

    manifest = [
        "# Stage 16N CPU Scaling Benchmark Deck",
        "",
        f"- Source deck: `{source_inp}`",
        f"- Benchmark job stem: `{job}`",
        f"- Cycles: `{args.cycles}`",
        "- Purpose: compare Abaqus walltime and CPU efficiency at different CPU counts.",
        "- Accept the CPU count with the lowest practical core-hour cost, not necessarily the lowest walltime.",
    ]
    (out_dir / "STAGE16N_CPU_SCALING_BENCHMARK_MANIFEST.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(out_dir)
    print(job)


if __name__ == "__main__":
    main()
