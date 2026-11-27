---
name: pipeline-self-heal
description: Repair broken automated tests whose failure triage classified as locator drift, timing or wait issues, or stale test data, and deliver the fix as a pull request for human review. Use when asked to self-heal, auto-fix or repair failing tests after triage. Never for product bugs or changed expectations.
---

# Pipeline Self-Heal

Fixes **the test, never the product, and never the expectation.** A heal that makes a
real bug pass is the worst outcome this workflow can produce.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Preconditions (all of them, or stop)
- A triage file `06-triage-<RUN-ID>.json` exists.
- Each failure you touch has `route: pipeline-self-heal`, `confidence` high or medium,
  and a `sub_type` listed in `self_heal.allowed_categories` in
  `../../shared/config/gates.json`.

## Steps
1. For each eligible failure, find the root cause:
   - `locator_drift`: compare the old selector with the current DOM or snapshot. Choose
     the new locator by the preference order in `automation-conventions.md`, ideally a
     stable test ID. Prefer fixing the page object over the test.
   - `timing_wait`: replace the race with an explicit wait for the actual condition
     (element state, network response). Never add a fixed sleep or raise a global timeout.
   - `test_data_refresh`: fix the setup or fixture so the test creates its own data.
2. Make the change on a new branch named `self-heal/<RUN-ID>`.
3. Stage the change and run the guardrail:
   ```bash
   python3 scripts/check_heal_diff.py          # checks staged changes
   ```
   If it reports `SELF-HEAL REJECTED`, do not work around it. Revert that change and mark
   the failure `human-review`.
4. Re-run the healed tests locally or in a pipeline run. Each one must pass **3 times in
   a row** to count as fixed.
5. Open a PR (only if the user authorised self-heal PRs for this repo). Include: run ID,
   triage link, each failure, the root cause, the before and after locator or wait, and
   the re-run evidence. Request review from the test owner. **Never merge it yourself.**
6. Write `qe-artifacts/.../07-heal-<RUN-ID>.md` with the PR link and summary.

## Hard limits
- No changes to assertions, expected values, test steps' intent, or product code.
- No new retries, skips, `.only`, quarantine tags, or disabled tests.
- No more files than `self_heal.max_files_changed` in one PR.
