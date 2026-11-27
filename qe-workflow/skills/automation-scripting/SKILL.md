---
name: automation-scripting
description: Write automated test scripts for test cases marked 'automate', following the team's automation conventions. Use when asked to automate test cases, write automation or e2e or API test scripts, or convert test cases into code.
---

# Automation Scripting

Paths are relative to this skill's directory.

## Inputs
- `qe-artifacts/<STORY-ID>/04-feasibility.json`. Script only the cases with
  `recommendation: automate`.
- `03-test-cases.json` for steps, data and expected results.
- `../../shared/references/automation-conventions.md`. **If it still contains
  `<placeholders>`**, inspect the test repo for existing patterns (framework config, page
  objects, fixtures) and confirm your inferred conventions with the user before writing code.

## Steps
1. Study 2–3 existing tests in the repo and match their structure, helpers and style.
   Reuse existing page objects, fixtures and API clients; extend them rather than
   duplicating them.
2. For each case, write one test:
   - Test title starts with the TC ID, e.g. `TC-012 rejects expired card`.
   - Tag it with the story ID and suite tags per the conventions.
   - Implement every `expected` item as an assertion. Do not drop any.
   - Create and clean up its own data; no dependency on test order.
   - Use explicit waits on conditions, never fixed sleeps.
   - Choose locators in the order the conventions file gives.
3. Run the new tests locally (use the command from the conventions file) and the linter.
   Fix failures caused by the test itself. If a failure looks like a product bug, do
   **not** weaken the assertion: report it and hand off to **testrun-triage**.
4. Write `qe-artifacts/<STORY-ID>/05-automation-notes.md` with: files added or changed, a
   TC-to-test mapping, the local run result, and any cases you could not automate, with reasons.
5. Commit on a feature branch and open a PR only if the user asks.

## Rules
- Never hard-code secrets or environment URLs.
- Don't add retries to hide instability. Flakiness gets fixed or reported.
