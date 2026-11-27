---
name: definition-of-ready
description: Check a user story against the Definition of Ready (DoR) checklist and report ready or blocked before development and test case design start. Use when asked if a story is ready, ready for sprint, ready for dev or test design, or to run DoR.
---

# Definition of Ready

Checks that every required condition holds. **Any required condition that is not `met`
blocks the story, including `unknown`.** The script decides; you gather the evidence.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- `qe-artifacts/<STORY-ID>/01-quality-report.json`. If it is missing, stop and tell the
  user to run **us-quality-gate** first.
- The story in the tracker (status, estimate, links, attachments, comments) if a tool is
  available; otherwise ask the user for each condition you cannot verify.

## Steps
1. Load the conditions from `../../shared/rubrics/dor-checklist.json`.
2. For each condition, set `status` to `met`, `not_met`, `not_applicable` or `unknown`,
   with `evidence`: a link, field value, comment or the user's confirmation.
   - `quality_gate_passed`: read `decision` from 01-quality-report.json.
   - `not_applicable` is only valid for non-required conditions.
   - If you cannot verify a condition, mark it `unknown`. Do not assume it is met.
   - For each condition that is not met, name an `owner` if you can tell who should act
     (PO, Dev lead, QE, Env team).
3. Write `qe-artifacts/<STORY-ID>/02-dor-result.json` per
   `../../shared/schemas/dor-result.schema.json`.
4. Run:
   ```bash
   python3 scripts/check_dor.py qe-artifacts/<STORY-ID>/02-dor-result.json --write
   ```
   Exit 0 = ready, 1 = blocked.
5. Report READY or BLOCKED, then list the blockers with their owners and the action each
   one needs.

## Rules
- Never mark the story ready to "unblock" people; that is an override decision for a
  named person (`decided_by`, `override_reason`).
- Re-running is cheap. After blockers are fixed, run the check again rather than editing
  the result by hand.
