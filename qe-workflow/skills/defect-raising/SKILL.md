---
name: defect-raising
description: Draft and raise defects for product bugs found in testing or triage, with reproduction steps, evidence, severity, and links to the story, acceptance criteria and test cases, after checking for duplicates. Use when asked to raise, log, file or write a bug or defect.
---

# Defect Raising

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- Failures with `route: defect-raising` from `06-triage-<RUN-ID>.json`, or a bug the
  user describes.
- `03-test-cases.json` and `01-quality-report.json` for TC and AC links.
- `../../shared/references/severity-matrix.md`.

## Steps
1. **Check for duplicates first.** If a tracker tool is available, search open defects
   by error signature, component and key words from the title. If you find a likely
   match, propose linking to it (`status: linked_to_existing`, `duplicate_of`) rather
   than creating a new one.
2. Draft each defect:
   - **Title:** `[Component] <what fails> when <condition>`. Specific, no "doesn't work".
   - **Environment and build:** from the pipeline run.
   - **Steps to reproduce:** numbered and minimal, from a clean state, including the test data used.
   - **Expected:** quote the AC (`AC-n`) or the spec.
   - **Actual:** the observed result and the exact error message.
   - **Evidence:** log excerpt, screenshot or trace path, failing test name, run URL.
   - **Severity** from the matrix; **suggested priority** is only a suggestion, the PO decides.
   - **Links:** story ID, AC IDs, TC IDs, run ID.
3. Write `qe-artifacts/<STORY-ID>/08-defects.json` with `status: draft` and validate it:
   ```bash
   python3 ../../shared/scripts/validate.py defect qe-artifacts/<STORY-ID>/08-defects.json
   ```
4. Show the drafts to the user. **Create them in the tracker only after confirmation.**
   Then record each `key` and set `status: created`.

## Rules
- One defect per distinct root cause, not one per failing test.
- No speculation about the cause in the defect body. Put hypotheses in a separate
  "Notes for developer" section, clearly labelled.
