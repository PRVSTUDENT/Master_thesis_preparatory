# Chaboche UMAT Implementation Guide

## UMAT Subroutine Structure

### Fortran Interface
```fortran
SUBROUTINE UMAT(STRESS, STATEV, DDSDDE, SSE, SPD, SCD,
     1 RPL, DRPL, DRPLDT, STRAN, DSTRAN, TIME, DTIME, TEMP, DTEMP,
     2 PREDEF, DPRED, CMNAME, NDI, NSHR, NTENS, NSTATEV, PROPS, NPROPS,
     3 COORDS, DROT, PNEWDT, CELENT, DFGRD0, DFGRD1, NOEL, NPT, LAYER,
     4 KSPT, JSTEP, KINC)
```

### Input Parameters
- `STRAN`: Strain tensor (6 components) at start of increment
- `DSTRAN`: Strain increment
- `DTIME`: Time increment
- `TIME`: Current total time
- `STRESS`: Stress tensor (input: previous; output: updated)
- `STATEV`: State variables (internal variables)
- `PROPS`: Material properties array

### Output Parameters
- `STRESS`: Updated stress tensor
- `DDSDDE`: Material Jacobian (6×6 matrix)
- `STATEV`: Updated state variables
- `PNEWDT`: Suggested new time increment (ratio to current)

## Chaboche Model Equations

### Yield Function
```
f = J2(σ - X) - R(p) ≤ 0

where:
  J2 = √(3/2 * dev(σ-X) : dev(σ-X))
  R(p) = σ_y + Q * (1 - exp(-b*p))
  X = backstress
  p = accumulated plastic strain
```

### Flow Rule (Associated Plasticity)
```
dε_p = dλ * ∂f/∂σ = dλ * (3/2) * dev(σ-X) / J2
dp = dλ
```

### Backstress Evolution (Armstrong-Frederick)
```
dX = C*dε_p - γ*X*dp
```

### Viscoplastic Extension (if applicable)
```
dε_vp = <Φ(f)>^m * ∂f/∂σ
Φ(f) = (J2(σ-X) - R(p)) / K
```

## State Variables (STATEV) Array

| Index | Variable | Description |
|-------|----------|-------------|
| 1-6   | σ_old    | Previous stress tensor |
| 7     | p        | Accumulated plastic strain |
| 8-13  | X        | Backstress tensor (6 components) |
| 14    | ε_vp_eff | Effective viscoplastic strain |
| 15    | T_internal | Internal temperature rise |

**Total DEPVAR = 15** (adjust based on model complexity)

## Material Properties (PROPS) Array

| Index | Parameter | Value | Unit |
|-------|-----------|-------|------|
| 1     | E         | Young's modulus | GPa |
| 2     | ν         | Poisson's ratio | - |
| 3     | σ_y       | Initial yield stress | MPa |
| 4     | Q         | Hardening parameter | MPa |
| 5     | b         | Hardening exponent | - |
| 6     | C         | Backstress modulus | MPa |
| 7     | γ         | Backstress decay | - |
| 8     | K         | Viscosity parameter | - |
| 9     | m         | Viscosity exponent | - |

**Total NPROPS = 9** (adjust for extended models)

## Input File (*.inp) Modifications

### Original Material Block (Elastic)
```
*MATERIAL, NAME=ELASTIC_316
*ELASTIC
210000, 0.3
```

### New Chaboche UMAT Block
```
*MATERIAL, NAME=CHABOCHE_VP
*USER MATERIAL, CONSTANTS=9
210000.0, 0.3, 520.0, 200.0, 0.05, 120000.0, 800.0, 0.001, 5.0
*DEPVAR
15
```

### In Section Assignment
```
*SOLID SECTION, ELSET=ALL_ELEMENTS, MATERIAL=CHABOCHE_VP
1.0
```

## Numerical Integration Scheme

### Implicit Backward Euler
```
σ_n+1 = σ_n + C_ep : (ε_n+1 - ε_p_n+1)
ε_p_n+1 = ε_p_n + Δλ * n_n+1
```

### Consistent Tangent Operator
```
∂σ/∂ε = C_ep = C - (C : n ⊗ n : C) / (a + n : C : n)
```

where:
- `C`: Elastic stiffness
- `n`: Plastic flow direction
- `a`: Hardening + viscosity terms

## Convergence Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| DIVERGE | Large strain increments | Reduce load amplitude or use automatic time stepping |
| NAN/INF | Division by zero in J2 | Add small tolerance (e.g., 1e-15) |
| Slow convergence | Poor Jacobian | Check DDSDDE calculation |
| Overshooting | Explicit vs implicit mismatch | Use STATEV backup & return strategy |

## Validation Checklist

- [ ] UMAT compiles without errors
- [ ] Datacheck passes
- [ ] 1-cycle monotonic test runs
- [ ] Stress output is physically reasonable
- [ ] Hysteresis loop has correct shape
- [ ] PEEQ increases monotonically
- [ ] Backstress limits to steady-state
- [ ] 10-cycle results show expected hardening/softening

## Debugging Output

Add to Fortran:
```fortran
WRITE(7,*) 'KINC=', KINC, ' J2=', J2, ' LAMBDA=', DLAMBDA
WRITE(7,*) 'STRESS=', (STRESS(I), I=1,NTENS)
WRITE(7,*) 'STATEV(1:6)=', (STATEV(I), I=1,6)
```

Output written to `*.log` or unit 7 file.

## Next Steps

1. Obtain/compile Chaboche UMAT source (`chaboche_umat.f`)
2. Create input file template
3. Run datacheck
4. Execute Phase 1 validation
5. Extract and compare results
6. Proceed to cycle-jump implementation

