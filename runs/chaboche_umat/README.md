# Chaboche Unified Viscoplastic UMAT Implementation

## Overview
This folder contains the implementation of a **Chaboche unified viscoplastic User Material (UMAT)** in Abaqus/Standard for cyclic loading analysis.

## Model Specifications

### Geometry & Mesh
- **Base geometry**: 10 × 2 × 2 mm deformable solid block
- **Element type**: C3D8R (8-node linear brick, reduced integration)
- **Boundary conditions**: 
  - Left face: Fixed (ENCASTRE)
  - Right face: Cyclic displacement loading
- **Analysis type**: Static General, Abaqus/Standard

### Material Model
- **Model type**: Chaboche unified viscoplastic UMAT
- **Reference**: Yue & Zhou 2023 / XJTU 316 stainless steel formulation
- **Internal variables (DEPVAR)**: 
  - Equivalent plastic strain
  - Back stress components
  - Damage parameter (if applicable)

## Folder Structure

```
chaboche_umat/
├── README.md                          # This file
├── UMAT_Implementation_Notes.md       # Detailed UMAT implementation notes
├── chaboche_umat_1cycle.inp           # Base 1-cycle test input file
├── chaboche_umat_1cycle.log           # Run log and diagnostics
├── chaboche_umat_10cycle.inp          # Extended 10-cycle input file
├── chaboche_umat_10cycle.log          # Run log and diagnostics
├── postprocessing/                    # Postprocessing scripts
│   ├── extract_hys.py
│   └── extract_peeq.py
└── umat/                              # UMAT source code
    ├── chaboche_umat.f                # Fortran UMAT implementation
    └── chaboche_umat.obj              # Compiled object (if available)
```

## Implementation Roadmap

### Phase 1: Single-Cycle Validation
1. ✓ Create folder structure
2. Create `chaboche_umat_1cycle.inp` from existing template
3. Replace material block with `*User Material`
4. Add `*Depvar` for internal variables
5. Run Abaqus datacheck
6. Run 1-cycle monotonic test
7. Validate results vs. analytical solution

### Phase 2: Cyclic Loading (2-10 cycles)
1. Extend to `chaboche_umat_10cycle.inp`
2. Implement cyclic displacement amplitude
3. Extract hysteresis loops
4. Extract PEEQ (equivalent plastic strain) evolution
5. Compare with reference models

### Phase 3: Cycle-Jump Acceleration
1. Implement internal variable accumulation
2. Apply cycle-jump method for 100+ cycle prediction
3. Validate long-term behavior predictions

## Files Generated During Simulation

- `*.com`: Completion file (Abaqus status)
- `*.msg`: Message file (solver output)
- `*.odb`: Output database (results)
- `*.sta`: Status file
- `*.dat`: Simulation data
- `*.prt`: Print file (diagnostics)

## Running Simulations

### Syntax check (datacheck)
```bash
abaqus job=chaboche_umat_1cycle datacheck
```

### Full simulation
```bash
abaqus job=chaboche_umat_1cycle cpus=4 interactive
```

### With UMAT compilation
```bash
abaqus job=chaboche_umat_1cycle user=chaboche_umat.f cpus=4 interactive
```

## Postprocessing

Use Python scripts in `postprocessing/` to extract:
- Force-displacement hysteresis loops
- PEEQ (equivalent plastic strain) evolution
- Stress-strain responses

## References

- **Yue & Zhou 2023**: Chaboche viscoplastic model formulation
- **Abaqus Documentation**: UMAT subroutine interface
- **316 Stainless Steel**: High-temperature fatigue properties

## Status

- Created: 2026-05-06
- Last updated: 2026-05-06
- Current phase: Phase 1 - Setup & Validation

## Notes

- Keep existing geometry and mesh intact
- Only modify material definition sections in `.inp` files
- All cycles use displacement-controlled loading
- Results stored in `.odb` format for postprocessing
