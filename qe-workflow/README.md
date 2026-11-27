# qe-workflow plugin

> Pairs with [`dev-workflow`](../dev-workflow/README.md), which covers Plan, Design, Build and
> Review. With both installed, test design runs in the Design stage, and the implementation
> plan cites these test cases as its Proof.

Quality Engineering skills for the SDLC. Each skill is one stage. The stages hand off
through files with fixed schemas, and every gate decision is computed by a script rather
than by the model.

```
user story ──> [us-quality-gate] ──> [definition-of-ready] ──> (development)
                  score + pass/fail      ready / blocked
                                                │
                                                v
             [test-case-generation] ──> [automation-feasibility] ──> [automation-scripting]
                 AC -> TC coverage          automate/manual/defer        tests in test repo
                                                                                │
                                                       CI pipeline runs tests (not a skill)
                                                                                │
                                                                                v
                                                                       [testrun-triage]
                                                     ┌──────────────┬───────────┴───────────┬───────────────┐
                                                product_bug   test_bug (locator/      environment / flaky /
                                                     │        timing/data)            low confidence
                                                     v              v                       v
                                             [defect-raising] [pipeline-self-heal]   notify / quarantine /
                                                     │          PR for review          human review
                                                     └──────────────┬───────────────┘
                                                                    v
                                                          [definition-of-done]
                                                          testing complete?
```

## Skills

| Skill | Writes | Decides with |
|---|---|---|
| `us-quality-gate` | `01-quality-report.json` | `scripts/score_gate.py` (weights, threshold, hard fails) |
| `definition-of-ready` | `02-dor-result.json` | `scripts/check_dor.py` (any required condition not `met` blocks) |
| `test-case-generation` | `03-test-cases.json` | schema validation; human review before pushing to a test management tool |
| `automation-feasibility` | `04-feasibility.json` | `scripts/score_feasibility.py` (default recommendation; overrides need a rationale) |
| `automation-scripting` | tests in the test repo + `05-automation-notes.md` | local test run |
| `testrun-triage` | `06-triage-<RUN>.json` | taxonomy plus routing rules; low confidence goes to a human |
| `pipeline-self-heal` | PR + `07-heal-<RUN>.md` | `scripts/check_heal_diff.py` (rejects assertion, sleep or product-code changes) |
| `defect-raising` | `08-defects.json` | duplicate check; human confirms before anything is created |
| `definition-of-done` | `09-dod-result.json` | `scripts/check_dod.py` (coverage, pass rate, open defects) |

## Agents

Agents are separate Claude instances that **use** the skills above. Each has its own
context, tool list and model. The skills stay the single source of truth for how each step
is done.

| Agent | Uses skills | Why it is an agent |
|---|---|---|
| `story-gatekeeper` | us-quality-gate, definition-of-ready | Independent judge: never sees the conversation that wrote the story |
| `triage-analyst` | testrun-triage | Reads large logs in its own context and returns only the routed result. Runs headless in CI |
| `self-heal-fixer` | pipeline-self-heal | Isolated git worktree when used as a subagent. In CI, restricted by the tool allowlist |

Use them in a session by name (e.g. "use the story-gatekeeper agent on PAY-101"), or
headless: `claude -p "..." --plugin-dir ./qe-workflow --agent qe-workflow:triage-analyst`.

Plugin agents ignore `permissionMode`, `hooks` and `mcpServers` in their frontmatter.
Enforce limits with `--allowedTools` and `--permission-mode dontAsk` in headless runs,
or copy an agent into `.claude/agents/` if you need those fields.

See [`examples/ci/`](examples/ci/README.md) for a GitHub Actions workflow that runs triage
on every failed test run and, after a person approves, self-heal as a draft PR.

## Layout

```
qe-workflow/
  .claude-plugin/plugin.json
  skills/<skill>/SKILL.md (+ scripts/)
  agents/                    <- story-gatekeeper, triage-analyst, self-heal-fixer
  shared/
    config/gates.json        <- thresholds and limits: tune these, not the prompts
    rubrics/                 <- story rubric (md anchors + json weights), DoR and DoD checklists
    references/              <- handoff contract, triage taxonomy, severity matrix,
                                automation conventions (TEMPLATE), glossary
    schemas/                 <- JSON Schemas for every handoff file
    scripts/                 <- validate.py, triage_summary.py, qe_common.py (stdlib only)
  evals/us-quality-gate/     <- eval cases + runner
  examples/qe-artifacts/PAY-101/  <- worked example outputs
  examples/ci/               <- GitHub Actions triage + self-heal workflow, sample report
```

The scripts use only the Python 3 standard library.

## Install

From this repo's marketplace:

```
/plugin marketplace add <path-or-git-url-of-this-repo>
/plugin install qe-workflow@qe-marketplace
```

Or, for local development: `claude --plugin-dir ./qe-workflow`

## Adapting it to your team

1. **Fill in `shared/references/automation-conventions.md`.** Until you do, the scripting
   and self-heal skills ask before they assume anything about your framework.
2. Tune `shared/config/gates.json` and the weights in `shared/rubrics/us-quality-rubric.json`.
3. Edit the DoR and DoD checklists to match your team's working agreement.
4. Adjust `TEST_PATH_PATTERNS` and `ASSERTION_PATTERNS` in
   `skills/pipeline-self-heal/scripts/check_heal_diff.py` for your stack.
5. Connect MCP servers for your tracker (Jira), test management tool (TestRail, Xray) and
   CI. The skills use them when they are available and ask for pasted input when they aren't.
6. **Enforce the gates in your workflow tool.** For example, make a Jira transition or a
   pipeline check require `decision: pass` or `ready`. A skill can only advise; the
   enforcement has to live in that system.

## Evals

```bash
cd qe-workflow/evals/us-quality-gate
./run_skill.sh ./out 3          # runs the skill 3 times on each case with `claude -p`
python3 run_eval.py ./out       # accuracy, calibration, consistency across runs
```

The six cases and their `expected.json` values are **placeholders** that came with the
scaffold. Replace them with 20–30 real stories scored by experienced QEs before you trust
the gate. Add eval sets for the other skills the same way, starting with triage, which is
the step that routes everything after it.
