---
name: definition-of-done
description: Decide whether testing for a story is complete using Definition of Done exit criteria (AC coverage, pass rate, open defects, regression, report), and produce a test summary. Use when asked if testing is complete, done, or signed off, whether a story can be closed or released, or for a test summary report.
---

# Definition of Done (Testing Completed)

The exit gate, symmetric with DoR. Thresholds live in `../../shared/config/gates.json`.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- `01-quality-report.json` (AC list), `03-test-cases.json` (coverage),
  the latest `06-triage-*.json` and the test run results, and `08-defects.json`.
- If a tracker or test management tool is available, current defect statuses and
  execution results. Use those over the local files when they differ.

## Steps
1. Compute the metrics:
   - `ac_total`: the number of ACs.
   - `ac_covered_executed`: ACs with at least one TC **executed** in the latest run
     (designed is not enough).
   - `tests_executed` and `tests_passed` for this story's cases in the latest run.
   - `open_defects`: counts by severity for defects linked to the story and not closed.
2. Assess each condition in `../../shared/rubrics/dod-checklist.json` with evidence.
3. Write `qe-artifacts/<STORY-ID>/09-dod-result.json` and run:
   ```bash
   python3 scripts/check_dod.py qe-artifacts/<STORY-ID>/09-dod-result.json --write
   ```
   Exit 0 = done, 1 = not done.
4. Produce a short test summary: scope, metrics, AC-to-TC-to-result traceability table,
   open defects, known risks and untested areas, and the decision. Offer to post it on
   the story.

## Rules
- Untested areas and accepted risks must be listed explicitly, never omitted.
- Sign-off on `not_done` is an override by a named person, with a reason.
