# Design Review: QE Workflow as Skills

Feedback on the proposal to build the QE workflow in the SDLC as Claude skills (SKILL.md files).

**Proposed flow:** user story → quality gate → Definition of Ready → development → test case
generation → automation feasibility → automation scripting → pipeline test run → test run
triage → pipeline self-heal → defect raising → testing completed.

Skills are the right tool for most of this, but not all of it. They fit the steps that need
judgment. They fit poorly where you need guaranteed enforcement or plain automation.

## Where skills fit well

These steps are reasoning plus domain knowledge, which is what a SKILL.md is good at encoding:

- **User story quality review**: rubric, scoring guidance, good and bad examples
- **Test case generation**: techniques like boundary values, equivalence classes and negative paths, plus your house format
- **Automation feasibility**: criteria for automate, manual or exploratory
- **Writing automation scripts**: your framework's conventions, page objects, fixtures
- **Test run triage**: how to classify a failure
- **Raising defects**: template, severity and priority rules, reproduction steps

## Where skills alone are not enough

**1. Gates need enforcement, and a skill is only advice.** Claude decides when to load a skill,
and the model's output varies from run to run. So for the quality gate and DoR:
- Have the skill return **structured output**: a JSON score for each criterion, with evidence.
- Compute the pass/fail threshold **in code**, not in the model's head. A bundled script works.
- Put the actual blocking in your **workflow tool**: a Jira transition rule or a pipeline check. The skill produces the evidence; the system enforces the gate.
- Add a human override with a logged reason. Someone will need it.

**2. Running tests on the pipeline is CI, not a skill.** It's a pipeline job. Claude only comes
in afterwards, to read the results for triage.

**3. Pipeline self-heal is the riskiest step.** An AI that "heals" a failing test can quietly
turn a real bug into a pass. Put hard limits on it:
- Only fix test-side causes, like selector or locator drift and wait or timing issues.
- **Never** change an assertion or expected value.
- Always open a PR for a human to review. Never commit straight to the branch.

**4. Triage should route the next step.** Have it classify each failure as one of: product bug,
test bug, environment or infra, flaky, or test data. Then:
- Test bug → self-heal
- Product bug → raise a defect (check for duplicates first)
- Environment or flaky → retry, or notify the right team

That routing is what turns these separate skills into a workflow.

## Structural suggestions

- **Define a handoff format between stages.** Each skill should read the previous stage's output and write a defined format: story → score report → DoR result → test cases → feasibility matrix → scripts → run results → triage → defect. Without this, every skill re-reads raw context and the results drift.
- **Connect to real systems through MCP connectors**: Jira, TestRail or Xray, and your CI. A skill that can only read pasted text won't get used in practice.
- **Bundle scripts and references with the skills.** Skills can carry scripts and reference files. Keep shared material, like the scoring rubric, severity matrix and glossary, in one place rather than copying it into each SKILL.md.
- **Package the set as a plugin** so the whole QE team installs one versioned bundle.
- **Write evals for each skill.** For example, collect 20–30 real user stories that experienced QEs have already scored, and check that the skill agrees with them. A gate nobody has calibrated will be either ignored or resented.

## Gaps in the flow

- **Definition of Done / exit criteria.** "Testing completed" should be a gate just like DoR: coverage met, no open critical defects, sign-off report produced.
- **Traceability** from story to test case, test run and defect. Auditors and release managers will ask for it.
- **Test data preparation**, and **risk-based selection** of which tests to run for regression.

## Bottom line

Use skills for the judgment, code for the scoring and thresholds, the workflow tool for
enforcement, and humans for approving fixes and defects. With that split, this is a solid design.

## Follow-up

The plugin built from these recommendations is in [`qe-workflow/`](../qe-workflow/README.md).
