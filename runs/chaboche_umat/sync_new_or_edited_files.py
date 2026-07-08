import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HANDOFF_DIR = ROOT / "new files created or edited"
WORKSPACE_ROOT = ROOT.parent.parent

# Source/text-first policy from .agent.md
EXCLUDED_EXTENSIONS = {
    ".odb",
    ".prt",
    ".dat",
    ".msg",
    ".sta",
    ".sim",
    ".stt",
    ".mdl",
    ".cax",
    ".com",
    ".lck",
    ".023",
}

# If a text file exceeds this size, skip unless explicitly allowed.
LARGE_TEXT_BYTES = 2 * 1024 * 1024


def is_likely_text_file(path):
    try:
        with path.open("rb") as handle:
            sample = handle.read(4096)
    except OSError:
        return False
    return b"\x00" not in sample


def ensure_inside_workspace(path):
    resolved = path.resolve()
    root = WORKSPACE_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Refusing to copy path outside workspace: {path}") from exc
    return resolved


def clear_handoff_dir():
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    handoff_root = HANDOFF_DIR.resolve()
    if handoff_root == ROOT.resolve():
        raise RuntimeError("Refusing to clear the run root.")
    for item in HANDOFF_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def copy_files(files):
    copied = []
    skipped = []
    for item in files:
        src = ensure_inside_workspace((ROOT / item) if not Path(item).is_absolute() else Path(item))
        if not src.exists():
            raise FileNotFoundError(src)
        if HANDOFF_DIR.resolve() in src.resolve().parents:
            continue

        if src.suffix.lower() in EXCLUDED_EXTENSIONS:
            skipped.append((src, "excluded generated/binary extension"))
            continue

        if not is_likely_text_file(src):
            skipped.append((src, "binary or non-text content"))
            continue

        if src.stat().st_size > LARGE_TEXT_BYTES:
            skipped.append((src, "large text file (requires explicit user approval)"))
            continue

        # Flat mirror: preserve filename only, never create subfolders.
        dst = HANDOFF_DIR / src.name
        shutil.copy2(src, dst)
        copied.append(src)
    return copied, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Clear the handoff folder and copy the current new/edited files into it."
    )
    parser.add_argument("files", nargs="+", help="Files to copy (relative to runs/chaboche_umat or absolute).")
    args = parser.parse_args()

    clear_handoff_dir()
    copied, skipped = copy_files(args.files)
    print("Handoff folder:", HANDOFF_DIR)
    print("Copied files:")
    for item in copied:
        print("-", item)

    if skipped:
        print("Skipped files:")
        for item, reason in skipped:
            print(f"- {item} ({reason})")


if __name__ == "__main__":
    main()
