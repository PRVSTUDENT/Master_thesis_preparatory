# R4Q3D2 HOLE_RING_SDV1 Trace Compare

status=completed_no_abaqus
classification_scope=diagnostic_after_cycle1000_accuracy_fail

The repaired reference has selected local-state anchors at cycles 1, 2, 10, 50, 100, 250, 500, 750, and 1000.
The retained R4Q3 selected local-state file has only the cycle1000 endpoint, so the SDV1 deviation cannot be classified as sudden or gradual from lightweight R4Q3 history alone.
At cycle1000, `HOLE_RING_SDV1_MAX` is 24.4159812927 for R4Q3 and 26.0519256592 for the repaired reference, giving 6.2795526% relative error.

CSV: `R4Q3D2_HOLE_RING_SDV1_trace_compare.csv`
