# Stage 16N Unattended Dependency Queue

## Policy

```text
Maximum active solver jobs : 2
CPUs per solver job        : 16
Memory per solver job      : 90 GB
Walltime per solver job    : 24 h
Mail policy                : abe
Old B2/B3                  : held
```

## Stream A: Cycle-100 Boundary

```text
B1D2_100_to_102_to_250
PBS job : 1341026.mmaster02
Status  : running
Purpose : test delta N = 2 near cycle 100

B1D1_100_to_101_to_250
PBS job    : 1341029.mmaster02
Dependency : afterany:1341026.mmaster02
Status     : held by dependency
Purpose    : test smallest practical cycle-100 jump
```

`afterany` is intentional because B1D1 is useful whether B1D2 passes or fails.

## Stream B: Cycle-250 Reinjection Gate

The first Stream B submission failed because the exact B0-2 PBS file had CRLF line endings:

```text
B0_250_to_500 first attempt : 1341030.mmaster02, exit 126, /bin/bash^M
B2D2 first dependent job    : 1341031.mmaster02, dependency not satisfied
B2D5 first dependent job    : 1341032.mmaster02, dependency not satisfied
```

The exact PBS generator was changed to write submit scripts as bytes with LF line endings, and the remote PBS file was normalized.

Stream B retry:

```text
B0_250_to_500
PBS job : 1341033.mmaster02
Status  : failed, exit 1
Purpose : exact cycle-250 state -> continue to cycle 500
Failure : first REINJECTION_EQUILIBRATE increment, too many attempts

B2D2_250_to_252_to_500
PBS job    : 1341034.mmaster02
Dependency : afterok:1341033.mmaster02
Status     : dependency not satisfied
Purpose    : smallest cycle-250 fixed-jump diagnostic after exact reinjection succeeds

B2D5_250_to_255_to_500
PBS job    : 1341035.mmaster02
Dependency : afterok:1341034.mmaster02
Status     : dependency not satisfied
Purpose    : larger but still conservative cycle-250 diagnostic after B2D2 solver success
```

Because B0_250_to_500 failed before physical continuation, B2D2 and B2D5 correctly did not run.

## Stream B Replacement: Cycle-250 Initialization Audit

```text
B0_AUDIT_0250_INITIALIZATION_ONLY
PBS job : 1341036.mmaster02
Status  : failed, exit 1
Purpose : determine whether the cycle-250 manual state injection fails immediately during initialization/equilibration
Failure : first initialization/equilibration increment, too many attempts after cutbacks to 6.25e-11
```

The audit failure means the cycle-250 gate is now clearly a state-initialization/equilibration problem, not a cycle-jump accuracy result.

Because exact B0_250_to_500 and B0_AUDIT_0250_INITIALIZATION_ONLY both fail before physical continuation, do not submit B2SAFE, B2D2, B2D5, old B2, or any later-cycle fixed jump until the cycle-250 manually injected stress/state field is diagnosed.

## Do Not Submit Yet

```text
B2_250_to_300_to_500
B3_500_to_575_to_750
B3SAFE_500_to_515_to_750
B4SAFE_750_to_770_to_1000
```

These remain held until the cycle-250 reinjection/equilibration gate is understood.

## Long-Weekend Extension Queue

Submitted before leaving for the Sunday gap. This keeps at most two 16-core jobs active while avoiding unsafe B2/B3 jumps.

```text
STREAM A: cycle-100 boundary and equilibration fallback

1341026  B1D2_100_to_102_to_250       running
    ↓ afterany
1341029  B1D1_100_to_101_to_250       held
    ↓ afterany
1341037  B1D2_EQ_100_to_102_to_250    held
    ↓ afterany
1341038  B1D1_EQ_100_to_101_to_250    held

STREAM B: cycle-250/500 state-injection diagnostics

1341039  B0_AUDIT_0500_INITIALIZATION_ONLY  running
    ↓ afterany
1341040  B0_AUDIT_0250_SDVINI_ONLY          held
    ↓ afterany
1341041  B0_AUDIT_0250_SIGINI_ONLY          held
    ↓ afterany
1341042  B0_AUDIT_0500_SDVINI_ONLY          held
    ↓ afterany
1341043  B0_AUDIT_0500_SIGINI_ONLY          held
```

Reason for Stream A:

```text
B1D2 and B1D1 finish the hard cycle-100 boundary.
B1D2_EQ and B1D1_EQ repeat the smallest jumps with a smaller equilibration initial increment.
These are diagnostic fallback cases if the original boundary jobs show numerical equilibration sensitivity.
```

Reason for Stream B:

```text
B0_AUDIT_0500_INITIALIZATION_ONLY checks whether the full state/stress injection failure also appears at cycle 500.
The SDVINI-only and SIGINI-only cases split the manual initialization field to identify whether STATEV, stress, or their coupled reinjection causes the equilibration failure.
All Stream B jobs are diagnostics, not accepted fixed-jump validations.
```

## Final Long-Weekend Queue State

The cycle-250/500 injection-only diagnostics completed quickly and failed with exit status 1:

```text
1341039  B0_AUDIT_0500_INITIALIZATION_ONLY  failed, exit 1
1341040  B0_AUDIT_0250_SDVINI_ONLY          failed, exit 1
1341041  B0_AUDIT_0250_SIGINI_ONLY          failed, exit 1
1341042  B0_AUDIT_0500_SDVINI_ONLY          failed, exit 1
1341043  B0_AUDIT_0500_SIGINI_ONLY          failed, exit 1
```

Because those diagnostics finished quickly, a second B1-only EQ stream was submitted into the free slot:

```text
STREAM C: B1 jump-size trend with smaller equilibration initial increment

1341047  B1Q_EQ_100_to_106_to_250    running
    ↓ afterany
1341048  B1S_EQ_100_to_112_to_250    held
    ↓ afterany
1341049  B1_EQ_100_to_125_to_250     held
```

Final live/queued solver jobs after the long-weekend extension:

```text
Total live/queued jobs : 10
Running jobs           : 2
Held jobs              : 8
Active CPU request     : 2 x 16 = 32 cores
Per-job request        : 16 CPUs, 90 GB, 24 h
```
