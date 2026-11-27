---
name: automation-feasibility
description: Assess which test cases should be automated, kept manual, explored, or deferred, and at which test layer (unit, API, UI). Use when asked about automation feasibility, automation candidates, what to automate, or automation ROI for a set of test cases.
---

# Automation Feasibility

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- `qe-artifacts/<STORY-ID>/03-test-cases.json`. If it is missing, run
  **test-case-generation** first.
- Context about the system under test: available APIs, test IDs in the UI, third-party
  dependencies, data setup options. Ask the user if it isn't known.

## Steps
1. Score each test case 1–5 on each factor (5 = most in favour of automating):
   | Factor | 5 means | 1 means |
   |---|---|---|
   | repeatability | runs every build / regression | one-off |
   | stability | feature and UI are settled | still changing heavily |
   | technical_feasibility | deterministic, controllable data, stable hooks | captcha, hardware, visual judgement |
   | business_risk | failure would be costly | trivial impact |
   | effort | (inverted) 1 = trivial, 5 = very costly | |
2. Pick `suggested_layer`, preferring the lowest layer that proves the behaviour:
   unit < API/contract < UI. Flag UI-only cases that could move down a layer.
3. Set `recommendation` and `rationale`, then write
   `qe-artifacts/<STORY-ID>/04-feasibility.json`.
4. Run:
   ```bash
   python3 scripts/score_feasibility.py qe-artifacts/<STORY-ID>/04-feasibility.json --write
   ```
   The script prints a default recommendation from the score. Where yours differs, the
   rationale must start with `OVERRIDE:` and give a reason. Fix any flagged rows and re-run (exit 1 means at least one row is flagged).
5. Report: counts per recommendation and per layer, the list of `automate` cases in
   priority order, and the main blockers to automation (e.g. "no test IDs on checkout page").
