# Stage 16N-B0-1 Local Diagnostic Review

## Purpose

Diagnose whether the `HOLE_RING_SDV8_MAX` mismatch in B0-1 is a field-wide reinjection error or a local extreme / argmax-location artifact.

## Inputs

- Reference ODB: `stage16n_parallel_max_reference/stage16n_parallel_max_reference_1000cycles.odb`
- Reinjection ODB: `stage16n_exact_reinjection/cases/B0_100_to_250/stage16n_exact_b0_100_to_250.odb`
- Compared cycle: `250`
- Reference step: `CYCLE_0250`
- Reinjection step: `CYCLE_0250`
- Common hole-ring element/IP records: `480`

## SDV8 Summary

- Mean relative error: `95.7018746161%`
- Median relative error: `11.5787939835%`
- 95th percentile relative error: `294.173582623%`
- Maximum pointwise relative error: `2199.63337835%`
- Reference argmax element/IP: `1242/7`
- Reinjection argmax element/IP: `1242/7`
- Same argmax location: `true`

## Output Files

- `stage16n_b0_100_to_250_pointwise_hole_errors.csv`
- `stage16n_b0_100_to_250_error_percentiles.csv`
- `stage16n_b0_100_to_250_argmax_location_check.csv`

## Interpretation Rule

If SDV8 median and 95th-percentile errors are small while only the max/argmax metric is high, B0-1 may be accepted as a practical reinjection pass. If the same element/IP shows large SDV8 error or many hole-ring points are high, B0-1 remains blocked for fixed cycle-jump validation.

## Diagnostic Conclusion

B0-1 remains `REVIEW / CONDITIONAL PASS`, not a clean exact-reinjection pass.

The `HOLE_RING_SDV8_MAX` mismatch is not explained by a max-location shift:

```text
Reference SDV8 argmax:    element 1242, IP 7, value 91.1466598511
Reinjection SDV8 argmax:  element 1242, IP 7, value 81.1967315674
Same argmax location:     true
Argmax relative error:    about 10.9164 %
```

The pointwise distribution also shows that the local SDV8 mismatch is not only a single harmless max-location artifact:

```text
SDV8 median relative error: 11.5788 %
SDV8 p95 relative error:    294.174 %
SDV8 mean absolute error:   4.06392
SDV8 p95 absolute error:    11.1338
```

The very large maximum relative errors are partly inflated by small denominators at low-magnitude points, but the same-location SDV8 maximum error is physically relevant for the hole-ring benchmark.

The global response remains strong:

```text
RF1 max error:  0.259048 %
RF1 min error:  0.687538 %
Loop area error: 0.967300 %
```

So B0-1 proves the `SIGINI` / `SDVINI` workflow can complete a long 16-CPU threaded continuation, but it does not yet prove exact local field reproduction.

## Next Decision

Do not submit B0-2 or B0-3 yet as validation jobs. First add an initialization-only audit:

```text
B0_AUDIT_100_INITIALIZATION_ONLY
```

This should inject the exact cycle-100 stress/STATEV field, output immediately after initialization/equilibration, and compare against reference cycle 100. The goal is to determine whether the local SDV8 mismatch is already present immediately after initialization or appears during the 100 -> 250 continuation.
