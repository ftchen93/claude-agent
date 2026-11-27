---
name: test-case-generation
description: Generate test cases from the acceptance criteria in a spec, intent or user story, with traceability from each AC to test cases. Runs in the Design stage, before build, so the implementation plan can cite the test cases as its Proof. Use when asked to write, design, generate or derive test cases or test scenarios for a story, spec or feature.
---

# Test Case Generation

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
Test design runs in the **Design stage, in parallel with spec review**, so the
implementation plan can cite these test cases as its Proof. Use the most refined source
available:
1. `sdlc/<STORY-ID>/spec.md` (from **dev-workflow:spec-design**). Preferred: it has the
   final AC IDs and the *Test strategy notes*.
2. Otherwise `sdlc/<STORY-ID>/intent.md`, or `qe-artifacts/<STORY-ID>/00-story.md` with
   the `acceptance_criteria_extracted` list from `01-quality-report.json`.

Keep the AC IDs exactly as the source numbers them. If
`qe-artifacts/<STORY-ID>/02-dor-result.json` exists and says `blocked`, carry its blockers
into `open_questions`. DoR no longer has to pass before test design starts, but its blockers
must be visible.

## Steps
1. For each AC, design tests using the techniques that fit:
   - **Equivalence partitioning** and **boundary values** for any input with ranges,
     lengths, dates or amounts
   - **Negative paths:** invalid input, missing permissions, dependency failure, timeouts
   - **Decision tables** for combinations of business rules
   - **State transitions** for workflows and statuses
   - **Non-functional** checks only where the story states an NFR
   Add `exploratory_charter` items for risky areas that scripted cases cannot cover well.
2. Each test case gets: `id` (`TC-001`...), `title`, `covers` (AC IDs), `type`,
   `technique`, `priority`, `preconditions`, `test_data`, `steps`, `expected`.
   - Priority: P1 = core business flow or high risk, P2 = important variations,
     P3 = edge or cosmetic.
   - Each step is an action; each expected result is observable and assertable.
3. Build `coverage`, a map from every AC to its TC IDs. **Every AC must have at least one
   TC.** If an AC cannot be tested as written, add it to `open_questions` and do not
   invent behaviour.
4. Write `qe-artifacts/<STORY-ID>/03-test-cases.json` and validate it:
   ```bash
   python3 ../../shared/scripts/validate.py test-cases qe-artifacts/<STORY-ID>/03-test-cases.json
   ```
5. Set `suggested_layer` thinking for each case now (unit, API or UI; the lowest layer that
   proves the behaviour) and say in `technique` or the title if a case should stay manual.
   The **automation-feasibility** skill is optional after this.
6. Show the user a summary table (ID, title, covers, type, priority) and the open
   questions. **A human reviews the cases before they are pushed to a test management
   tool** (TestRail, Xray, Zephyr). Push only after approval, if a tool is available.
7. Next step: the engineer's **dev-workflow:implementation-plan** cites these TC IDs in
   its Proof section. P1 scripted cases must all be cited.

## Rules
- Do not duplicate cases. Merge cases that differ only in data into one case with a data
  table.
- Keep IDs stable on regeneration: keep existing IDs and append new ones.
