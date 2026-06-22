# Stage 16N-R4L Result

Updated: 2026-06-22

## Decision

R4L has not produced a scientific true-jump result yet. Both submitted attempts stopped during setup/source-restart preparation before any R4L1 continuation solve or comparison.

## Attempts

| PBS job | Classification | Evidence |
| --- | --- | --- |
| `1353907.mmaster02` | setup failure | R1A linker expected `stage16n_r1a_restart_ref_500cycles.odb`; the post-cleanup retained offload folder did not contain that ODB. |
| `1353908.mmaster02` | setup failure | Cached jump state was found and copied, but Abaqus source restart failed because the retained R1A restart source is missing required `stage16n_r1a_restart_ref_500cycles.mdl`. |

## Interpretation

This is an infrastructure/provenance-retention blocker, not a scientific failure of the R4L true-jump method. The run stopped before the R4L1 source solve could create a deck-clone restart source, and before any R4L1 continuation/comparison.

The storage-light cleanup preserved the large R1A `.stt` and some support files, but the retained R1A set is incomplete for Abaqus/Standard restart source solving. Abaqus reported that restart requires `res`, `prt`, `mdl`, `stt`, and `sim`; the missing required file is `.mdl`.

## Storage Status

The failed R4L scratch attempt was cleaned of transient `state.csv` and `state.bin`. After cleanup:

- R4L attempt scratch folder: about `2.2M`.
- `/scratch9/pr21vyci`: about `2.7T`.

## Next Rule

Do not resubmit R4L until a complete, provenance-valid R1A restart source set is available, or until the controller is redesigned to use a different validated source that includes all Abaqus-required restart files. Do not regenerate large 505-branch sources, and keep R4J9/R4J10 blocked.
