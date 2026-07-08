# Stage 14D 24-Hour High-Density Controller Sweep

Purpose: find the fastest accepted-clean 2000-cycle adaptive cycle-jump controller for the Chaboche UMAT problem.

Stage 14D starts from the Stage 14C result set, where X06 was the best accuracy case and D4 was the fastest accepted-clean case.

## Baselines

- Stage 14 fixed best: jump25, STATEV1 error about 2.85226684954%.
- Stage 14B adaptive: STATEV1 error 124.209089872%.
- Stage 14C best accuracy: X06, STATEV1 error 0.0418369623642%, S11/RF1 error about 0.0075359655%, speed-up 1.88501413761x.
- Stage 14C fastest accepted clean: D4, STATEV1 error 0.886575562466%, S11/RF1 error about 0.1723839424%, speed-up 3.59066427289x.

## Queue Strategy

The controller runs a large priority-ordered case queue and stops launching new cases after 23 h 20 min.

Checkpointing happens after every completed block through:

- `STAGE14D_24H_BLOCK_HISTORY.csv`
- `STAGE14D_24H_CASE_SUMMARY.csv`
- `STAGE14D_24H_MASTER_SUMMARY.csv`
- `STAGE14D_24H_REPORT.md`
- `_logs/stage14d_progress_status.txt`

Runtime-error diagnostics are written to:

- `STAGE14D_24H_RUNTIME_ERROR_DIAGNOSTICS.csv`
- `DBGxx_STA_TAIL.txt`
- `DBGxx_MSG_TAIL.txt`
- `DBGxx_DAT_ERROR_EXTRACT.txt`
- `DBGxx_CONSOLE_TAIL.txt`

The controller exposes `PARALLEL_LANES` and `CPUS_PER_CASE`, but uses serialized case execution for lock-safe CSV/report updates.

## Case Groups

### SPEED_BOUNDARY

Grid:

- `SAFETY_FACTOR = 0.45, 0.50, 0.55, 0.60`
- `DN_MAX = 50, 75, 100, 125, 150, 175, 200, 250`
- `LOCAL_TOL = 0.001`
- `DN_MIN = 1`
- `RECOVERY_WINDOW = 10`
- `prediction_order = first_order`
- `deltaN_control_variables = STATEV1_only`
- `injection_mode = full_STATEV_plus_predicted_stress`

Goal: push beyond the D4 speed boundary while staying under 1% in STATEV1, S11, and RF1.

### D4_FINE

Fine sweep around D4:

- D4F01: safety 0.46, DN_MAX 150
- D4F02: safety 0.47, DN_MAX 150
- D4F03: safety 0.48, DN_MAX 150
- D4F04: safety 0.49, DN_MAX 150
- D4F05: safety 0.50, DN_MAX 175
- D4F06: safety 0.50, DN_MAX 200
- D4F07: safety 0.52, DN_MAX 125
- D4F08: safety 0.52, DN_MAX 150
- D4F09: safety 0.54, DN_MAX 100
- D4F10: safety 0.54, DN_MAX 125

### RECOVERY_WINDOW_SHORT

Shorter recovery windows of 5 and 7 cycles around the accepted Stage 14C cases.

### TOLERANCE

Tolerance sweep around:

- safety 0.50, DN_MAX 150
- safety 0.55, DN_MAX 100

### SECOND_ORDER

Second-order cycle-space prediction tests from DN_MAX 25 through 200.

### MULTIVARIABLE

Multi-variable DeltaN controller tests using:

- `STATEV1_plus_S11_RF1`
- `active_STATEVs`
- `active_STATEVs_plus_S11_RF1`

### ROLLBACK

Aggressive larger-jump cases with `rollback_enabled=true`. On analysis failure, the controller retries the current block with a halved `DN_MAX`.

### DEBUG_RUNTIME_ERRORS

One-block reproductions of Stage 14C runtime-error patterns. These write lightweight tail extracts instead of raw Abaqus output files.

## Report Ranking

The report ranks:

1. accepted-clean cases by highest speed-up
2. accepted-clean cases by lowest STATEV1 error
3. accepted exploratory cases
4. not accepted cases by lowest STATEV1 error
5. runtime errors with reason

## Upload Rule

Upload lightweight Markdown, CSV, scripts, PBS files, status files, and selected logs only. Do not upload Abaqus bulk files such as `.odb`, `.sim`, `.prt`, `.sta`, `.msg`, `.dat`, `.lck`, `.com`, `.mdl`, `.cax`, `.023`, `.stt`, `.env`, `.res`, `.fil`, `.abq`, `.pac`, `.sel`, or `.ipm`.
