# Stage 14: 2000-Cycle Repeated Blockwise Cycle-Jump Controller

Stage 14 tests repeated, re-anchored cycle jumps for a 2000-cycle Chaboche UMAT problem. It is separate from Stage 13: Stage 13 is a single initial jump for a 5000-cycle horizon, while Stage 14 repeatedly injects a predicted state and then computes a short real Abaqus recovery window.

## Rules

- Final cycle: `2000`
- Base cycle: `10`
- Recovery window after each jump: `10` real Abaqus cycles
- Final comparison: each strategy at cycle `2000` against the no-skip 2000-cycle reference
- Primary acceptance: final `STATEV1` relative error `<= 1%`

## Outcomes

- `accepted_clean_success`: `STATEV1 <= 1%`, `S11 <= 1%`, and `RF1 <= 1%`
- `accepted_exploratory_success`: `STATEV1 <= 1%`, but `S11` or `RF1 > 1%`
- `not_accepted`: `STATEV1 > 1%`

## Strategies

| Strategy | Route |
|---|---|
| `jump25` | `10 -> 500 -> 510 -> 1000 -> 1010 -> 1500 -> 1510 -> 1990 -> 2000` |
| `jump37` | `10 -> 740 -> 750 -> 1480 -> 1490 -> 1990 -> 2000` |
| `jump50` | `10 -> 1000 -> 1010 -> 1990 -> 2000` |
| `jump65` | `10 -> 1300 -> 1310 -> 1990 -> 2000` |

## Scientific Constraint

Block 1 uses no-skip reference cycles `2-10` to estimate mean per-cycle increments. Later blocks must use the previous block's actual recovered route history. For example, `jump25` block 2 uses actual route cycles `501-510` from block 1, not the no-skip reference window.

## Execution

Run from the repository root:

```powershell
.\runs\chaboche_umat\stage14_blockwise_jump_2000cycles\run_stage14_blockwise_controller.ps1
```

Abaqus generated files are intentionally not staged or cleaned by this workflow.
