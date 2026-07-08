#!/usr/bin/env python3
"""Thin CLI for documenting Stage 15K adaptive DeltaN parameters."""

from __future__ import print_function

from pathlib import Path


def main():
    Path("adaptive_state_jump").mkdir(parents=True, exist_ok=True)
    text = """# Stage 15K Adaptive DeltaN Controller

Defaults:
- epsilon = 0.01
- DeltaN_min = 1
- DeltaN_max = 100000
- growth_factor = 5
- tiny = 1e-14

Formula:
`DeltaN_i = floor(epsilon_i * max(abs(q_i), q_min_scale_i) / max(abs(dq_i/dN), tiny))`

The selected jump is the minimum variable-wise value, capped by requested target,
DeltaN_max, and growth factor.
"""
    Path("adaptive_state_jump/STAGE15K_ADAPTIVE_DELTAN_CONTROLLER.md").write_text(text)
    print("Wrote adaptive_state_jump/STAGE15K_ADAPTIVE_DELTAN_CONTROLLER.md")


if __name__ == "__main__":
    main()
