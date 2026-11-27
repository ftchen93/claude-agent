# Handoff Contract

Every skill reads the previous stage's output and writes its own, so the workflow is
traceable and each stage can be re-run independently.

## Location

```
qe-artifacts/<STORY-ID>/
  00-story.md                  # source story, as fetched or pasted
  01-quality-report.json       # us-quality-gate          -> schemas/quality-report.schema.json
  02-dor-result.json           # definition-of-ready      -> schemas/dor-result.schema.json
  03-test-cases.json           # test-case-generation     -> schemas/test-cases.schema.json
  04-feasibility.json          # automation-feasibility   -> schemas/feasibility.schema.json
  05-automation-notes.md       # automation-scripting (scripts live in the test repo)
  06-triage-<RUN-ID>.json      # testrun-triage           -> schemas/triage.schema.json
  07-heal-<RUN-ID>.md          # pipeline-self-heal (PR link + diff summary)
  08-defects.json              # defect-raising           -> schemas/defect.schema.json
  09-dod-result.json           # definition-of-done       -> schemas/dod-result.schema.json
```

`<STORY-ID>` is the tracker key (e.g. `PAY-1234`). Override the root with the
`QE_ARTIFACTS_DIR` environment variable.

## Rules

1. A skill must not start if its required input file is missing. It says which upstream
   skill to run instead.
2. JSON outputs must validate against their schema (`shared/scripts/validate.py`).
3. IDs are stable and carried forward: acceptance criteria `AC-1..n`, test cases
   `TC-001..n`. That chain is your traceability: story -> AC -> TC -> run -> defect.
4. Every gate decision records `decided_by` (`skill` or a person's name) and, for
   overrides, an `override_reason`.
5. Pass/fail is computed by the bundled scripts from the model's structured scores, never
   decided freehand by the model.
