---
name: us-quality-gate
description: Score a user story against the QE quality rubric and decide pass or fail before it can move to Definition of Ready. Use when someone asks to review, score, check or gate a user story, or asks whether a story is good enough, has enough context, or has proper acceptance criteria.
---

# User Story Quality Gate

Scores a story on a fixed rubric and records a pass/fail decision. **You score each
criterion with evidence; the script computes the total and the decision.** Never state a
pass/fail yourself before the script has run.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- A story ID, the story text, or `sdlc/<STORY-ID>/intent.md` from
  **dev-workflow:intent-capture**. An intent drafted by that skill should usually pass,
  because its interview asks the rubric's questions up front; this gate then confirms it.
  - If a tracker tool is available (e.g. Jira MCP), fetch the story, its description,
    acceptance criteria, attachments list and linked issues.
  - Otherwise ask the user to paste it.
- Save the source as `qe-artifacts/<STORY-ID>/00-story.md` (see
  `../../shared/references/handoff-contract.md`).

## Steps
1. Read `../../shared/rubrics/us-quality-rubric.md` (anchors) and
   `../../shared/rubrics/us-quality-rubric.json` (criterion IDs).
2. Extract the acceptance criteria in order and number them `AC-1..n`. Do not invent or
   reword them; quote them. If none exist, record an empty list.
3. Score **every** criterion 0–4 (or `null` only where N/A is allowed and it truly does
   not apply). For each one:
   - `evidence`: quote or point to the story text that justifies the score.
   - `question_for_author`: required when the score is below 3. Make it a concrete question
     the author can answer.
4. Write `qe-artifacts/<STORY-ID>/01-quality-report.json` following
   `../../shared/schemas/quality-report.schema.json`. Leave `total_score` and `decision` out.
5. Run:
   ```bash
   python3 scripts/score_gate.py qe-artifacts/<STORY-ID>/01-quality-report.json --write
   ```
   Exit 0 = pass, 1 = fail, 2 = invalid input (fix the JSON and re-run).
6. Report to the user:
   - the decision and score versus the threshold
   - any hard-fail reasons
   - a table of criteria with scores
   - the list of author questions, ordered by weight. This is the actionable part.
7. If the tracker tool is available, offer to post the author questions as a comment on
   the story. Do not post without confirmation.

## Rules
- Be strict and consistent. The same story must get the same scores on a re-run.
- Score what is written, not what you assume the author meant.
- Do not rewrite the story unless asked. If asked, produce a suggested revision
  separately, and re-gate the revised version as a new run.
- **Overrides:** only a named person can override a fail. Record `decided_by: <name>` and
  `override_reason`, set `decision: pass`, and keep the original score.
