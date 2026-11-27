---
name: test-case-generation
description: Generate test cases from a ready user story's acceptance criteria, with traceability from each AC to test cases. Use when asked to write, design, generate or derive test cases or test scenarios for a story or feature.
---

# Test Case Generation

Paths are relative to this skill's directory.

## Inputs
- `qe-artifacts/<STORY-ID>/02-dor-result.json` with `decision: ready`. If it is blocked
  or missing, stop and say so. The user may explicitly choose to proceed anyway; if they
  do, record that in `open_questions`.
- `00-story.md` and the `acceptance_criteria_extracted` list from `01-quality-report.json`.

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
5. Show the user a summary table (ID, title, covers, type, priority) and the open
   questions. **A human reviews the cases before they are pushed to a test management
   tool** (TestRail, Xray, Zephyr). Push only after approval, if a tool is available.

## Rules
- Do not duplicate cases. Merge cases that differ only in data into one case with a data
  table.
- Keep IDs stable on regeneration: keep existing IDs and append new ones.
