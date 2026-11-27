---
name: testrun-triage
description: Triage failed tests from a pipeline or test run: classify each failure (product bug, test bug, environment, flaky, test data), give evidence and confidence, and route it to the next action. Use when asked to triage a test run, analyse pipeline failures, explain why tests failed, or sort failures.
---

# Test Run Triage

Classifies every failure and decides where it goes next. This skill is the router of the
workflow; read `../../shared/references/triage-taxonomy.md` first.

Paths are relative to this skill's directory.

## Inputs
- A run ID or pipeline URL. If a CI tool is available (GitHub Actions, GitLab, Jenkins via
  MCP), fetch the job logs and test reports (JUnit XML, Allure, Playwright report);
  otherwise ask for the report files.
- Useful extra context, if reachable: the last N runs of each failing test (to spot
  flakiness), app commits since the last green run, and environment health.

## Steps
1. List the failed tests. Group them by **error signature** (normalised message plus top
   stack frame) so 40 failures from one outage become one item.
2. Classify each group with `category`, `sub_type` (for test_bug), `confidence` and
   `evidence`. Check signals in this order:
   1. **environment:** connection or DNS errors, 5xx from dependencies, many unrelated tests failing at once
   2. **test_data:** not-found or constraint errors on setup
   3. **flaky:** the same test passed on retry or alternates in recent history with no related change
   4. **test_bug:** a selector is missing after a UI change, or a fixture is broken
   5. **product_bug:** a business assertion fails consistently, in an area with recent app changes
3. Set `route`:
   - `product_bug` -> `defect-raising`
   - `test_bug` with `locator_drift`, `timing_wait` or `test_data_refresh` -> `pipeline-self-heal`
   - `test_bug` with `assertion_outdated` or `logic_error` -> `human-review`
   - `environment` -> `notify-env-owner`
   - `flaky` -> `quarantine`
   - **any classification with `confidence: low` -> `human-review`**, whatever its category
4. Write `qe-artifacts/<STORY-ID or RUN>/06-triage-<RUN-ID>.json` and validate it:
   ```bash
   python3 ../../shared/scripts/validate.py triage <file>
   ```
5. Report a summary: counts by category, then a table of signature, tests affected,
   category, confidence and route. Put the product bugs first.
6. Ask before handing off to downstream skills. Do not raise defects or open heal PRs
   automatically unless the user has said to.

## Rules
- Do not call something flaky just because it is inconvenient. Flaky needs evidence:
  retry results or run history.
- An assertion failure on a business value is a product bug until evidence shows the
  expectation itself is wrong.
