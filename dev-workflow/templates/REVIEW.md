# Review instructions

## Passes
Run four passes and tag each finding with its pass:
- **Bugs:** logic errors, broken edge cases, race conditions, subtle regressions
- **Security:** injection, authentication/authorisation gaps, secrets, PII in logs or errors
- **Compliance:** the change matches `sdlc/<ID>/spec.md`, `plan.md` and our design principles;
  any deviation from the plan is recorded in plan.md's Deviations section
- **QE:**
  - every acceptance criterion in spec.md is covered by at least one test in this PR or
    in the existing suite (cite TC IDs)
  - no existing test was deleted, skipped, weakened, or had its assertion or expected value
    changed without the spec changing
  - the Proof in plan.md was actually run, and the output is in the PR
  - tests create and clean up their own data; no fixed sleeps; locators follow conventions
  - for bug fixes, a failing test was committed before the fix

## What Important means here
Reserve **Important** for findings that would break behaviour, leak data, breach a policy,
or leave an acceptance criterion untested. Style and naming are **Nits**.

## Cap the nits
Report at most five nits per review; summarise the rest as a count.

## Do not report
Generated files, lockfiles, and anything CI already enforces (formatting, lint).

## Output
End every review with one machine-readable line:
`REVIEW-TALLY: important=<n> nit=<n> qe_gaps=<n>`
Findings inform the human reviewer. They never approve or block the PR on their own.
