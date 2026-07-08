#!/usr/bin/env python3
"""Audit the Stage 16N UMAT STATEV layout.

The goal is to separate true material memory variables from derived or
diagnostic STATEV entries before any restart-preserved state-jump work.
"""

from __future__ import annotations

from pathlib import Path


STAGE_DIR = Path(__file__).resolve().parent
UMAT = STAGE_DIR / "stage16n_neml_equivalent_chaboche_umat.for"
OUT = STAGE_DIR / "STAGE16N_STATEV_INDEPENDENCE_AUDIT.md"


STATEV_ROWS = [
    (1, "accumulated plastic strain alpha", "independent", "History variable used by isotropic hardening and the return mapping."),
    ("2:7", "backstress tensor 1", "independent", "Nonlinear Chaboche kinematic hardening memory."),
    ("8:13", "backstress tensor 2", "independent", "Nonlinear Chaboche kinematic hardening memory."),
    ("14:19", "backstress tensor 3", "independent", "Nonlinear Chaboche kinematic hardening memory."),
    ("20:25", "plastic strain tensor", "independent", "Plastic strain history used to keep strain decomposition consistent."),
    (26, "isotropic hardening R", "derived", "Recomputed as Q * (1 - exp(-b * alpha)); should not be independently jumped."),
    (27, "last plastic multiplier increment", "derived/diagnostic", "Increment-local output from the previous Abaqus increment; reset/recompute during continuation."),
]


def extract_layout_comments(text: str) -> list[str]:
    lines = []
    capture = False
    for line in text.splitlines():
        if "State variable layout:" in line:
            capture = True
        if capture:
            if line.strip().startswith("C"):
                lines.append(line.rstrip())
            elif line.strip().startswith("SUBROUTINE"):
                break
    return lines


def main() -> None:
    text = UMAT.read_text(errors="replace")
    layout_comments = extract_layout_comments(text)

    rows = [
        "# Stage 16N STATEV Independence Audit",
        "",
        "## Source",
        "",
        f"- UMAT: `{UMAT.relative_to(STAGE_DIR.parent.parent.parent)}`",
        "- Purpose: identify which STATEV entries should be modified by a restart-preserved material-state jump.",
        "",
        "## UMAT Layout Comment",
        "",
        "```text",
        *layout_comments,
        "```",
        "",
        "## Classification",
        "",
        "| STATEV entry | Meaning | Classification | Consequence for Stage 16N-R |",
        "|---:|---|---|---|",
    ]
    for entry, meaning, classification, consequence in STATEV_ROWS:
        rows.append(f"| {entry} | {meaning} | {classification} | {consequence} |")

    rows.extend(
        [
            "",
            "## Recommended Jump Set",
            "",
            "For the first restart-preserved overwrite/jump prototype, modify only:",
            "",
            "- `STATEV(1)` accumulated plastic strain alpha",
            "- `STATEV(2:19)` three Chaboche backstress tensors",
            "- `STATEV(20:25)` plastic strain tensor",
            "",
            "Do not independently inject `STATEV(26)` or `STATEV(27)`. `STATEV(26)` is a deterministic function of alpha in the UMAT and should be recomputed after the overwrite. `STATEV(27)` is an increment-local diagnostic/output value and should be reset or recomputed by the next constitutive update.",
            "",
            "## Interpretation",
            "",
            "The failed SDVINI/SIGINI route injected all available STATEV entries plus stress into a scratch FE model. That route does not preserve displacement, strain, equilibrium, or solver history. The Stage 16N-R repair should therefore keep Abaqus' FE state through native restart and overwrite only independent material memory inside the UMAT.",
            "",
        ]
    )
    OUT.write_text("\n".join(rows), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
