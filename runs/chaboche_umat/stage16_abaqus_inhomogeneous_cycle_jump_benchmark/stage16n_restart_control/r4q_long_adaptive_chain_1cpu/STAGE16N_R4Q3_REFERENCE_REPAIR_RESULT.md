# Stage 16N-R4Q3 Reference Repair Result

Controller: `R4Q3_reference1000_repair_and_compare`

Classification: `accuracy_validation_fail`

No Abaqus solve was submitted.

## Purpose

Classify the completed R4Q3 cycle1000 checkpoint by repairing the reference-data coverage problem that blocked the first comparison.

## Inputs inspected

- `reference_1000_cycle_metrics.csv`
- `reference_1000_selected_cycle_local_states.csv`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_cycle_metrics.csv`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_1000cycle_pilot/stage16n_plate_hole_neml_equiv_1000cycles_selected_cycle_local_states.csv`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_cycle_metrics.csv`
- `runs/chaboche_umat/stage16_abaqus_inhomogeneous_cycle_jump_benchmark/stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles_selected_cycle_local_states.csv`

The copied R4Q reference files and the `stage16n_1000cycle_pilot` files are incomplete for cycle1000. The metric CSVs end at cycle 593, and the selected local-state CSVs end at cycle 500.

The `stage16n_parallel_max_reference` files are the valid repair source. They are documented as the completed full non-jump 1000-cycle baseline:

- metrics: cycles 1--1000
- selected local states: cycles 1, 2, 10, 50, 100, 250, 500, 750, 1000

## Repair

The valid reference CSVs were copied into the R4Q evidence root as:

- `R4Q3_REFERENCE_REPAIR_reference_1000_cycle_metrics.csv`
- `R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv`

No data was fabricated and no Abaqus job was submitted.

## Comparison

The existing comparison script was rerun for cycle1000 using the repaired reference CSVs and the completed R4Q3 output.

Result:

- `status=review` from the existing script's three-band classifier
- Final requested classification: `accuracy_validation_fail`
- Max global error: `2.330504e-05%`
- Max primary-local error: `6.2795526%`
- Diagnostic S11 error: `0.00031922278%`
- Controlling metric: `HOLE_RING_SDV1_MAX`

The requested classification set is pass/fail/blocked. Because the strict primary-local gate is 5%, the cycle1000 checkpoint is not an accuracy-validation pass. Since the repaired reference is valid and the comparison completed, it is not reference-blocked. Therefore the final classification is `accuracy_validation_fail`.

This is not an Abaqus solve failure and not evidence that R4Q3 failed to reach cycle1000. R4Q3 reached cycle1000 cleanly and extracted the state; the failure is a strict local-state accuracy miss at the cycle1000 checkpoint.

## Evidence

- `R4Q3_REFERENCE_REPAIR_STATUS.txt`
- `R4Q3_REFERENCE_REPAIR_AVAILABLE_CYCLES.csv`
- `R4Q3_REFERENCE_REPAIR_COMPARE.log`
- `R4Q3_REFERENCE_REPAIR_cycle1000_comparison_summary.csv`
- `R4Q3_REFERENCE_REPAIR_cycle1000_comparison_details.csv`
- `R4Q3_REFERENCE_REPAIR_reference_1000_cycle_metrics.csv`
- `R4Q3_REFERENCE_REPAIR_reference_1000_selected_cycle_local_states.csv`

Do not resubmit R4Q4 or queue beyond cycle1000 without an explicit decision to either accept a revised local-state rule or continue as feasibility-only.
