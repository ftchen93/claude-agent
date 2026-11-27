# Plan: <short title> (from spec.md <date or commit>)
ID: <ID> · Engineer: <name> · Status: draft | accepted (by <name>, <date>)

## Files that change
<path> (new|changed) - <why>

## Order of work
1. <step>, which proves <TC IDs>

## Risks
- <what could break, and how the plan mitigates it>

## Alternatives considered
- <option not taken, and why>

## Proof
<!-- The tests that prove the change works. Cite TC IDs from qe-artifacts/<ID>/03-test-cases.json.
     Every AC must be covered by at least one cited TC, and every P1 scripted TC must be cited.
     Give the exact command(s), one per line, with no chaining (&&, ;): headless agents
     may only run single commands. -->
- Command: `<single test command>`
- TC-001 (AC-1): <test file::test name>
- Manual / exploratory: <TC IDs that are not automated, and who runs them>

## Deviations
<!-- Filled in during implementation. When the work departs from the plan, record it here
     in the same commit. -->
