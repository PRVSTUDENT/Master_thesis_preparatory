# Stage 16N-R4K2B 505 Candidate Validation Controller

Created: 2026-06-22

Purpose: validate the provisionally accepted R4E2 cycle-505 restart source without generating any new source `.stt`.

## Rules

- Use the preserved R4E2 cycle-505 restart source on `/scratch9/pr21vyci`.
- Do not run a source-regeneration solve.
- Read restart at cycle 505 and continue cycles 506--750.
- Do not request continuation restart writes in the input deck.
- Extract and compare immediately after the solve.
- Copy only lightweight evidence back to the Git clone.
- Delete continuation/datacheck heavy scratch outputs after classification.
- Do not run R4J9/R4J10 from this controller.

## Expected Decision

- If the comparison is exact, the 505 branch has a validated continuation control.
- If the comparison is nonzero, classify the R4E2 candidate as scientifically unsuitable for the 505 branch.
- If the job fails from I/O or stage-out, classify as infrastructure and clean the scratch case before retry design.
