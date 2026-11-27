# QE Workflow: Gap Analysis and Revised Flow

**Status:** draft for team discussion
**Compares:** (1) our original QE ideation, (2) the current `qe-workflow` plugin, and
(3) Anthropic's *AI-native SDLC playbook* (notes in
[`references/ai-native-sdlc-playbook.md`](references/ai-native-sdlc-playbook.md))

---

## 1. Summary

Our principles match the playbook. Our **shape** does not.

- **What matches:**
  - Stages hand off defined artifacts.
  - Gates are decided by code, not by the model.
  - People make the judgment calls.
  - Triage runs read-only in CI.
  - Self-heal only arrives as PRs.
  - Self-heal never weakens a test.
  - An independent agent reviews.
  - Skills have evals.
- **What doesn't match:** our flow is a **linear sequence of QE stages with a human gate
  between most of them**, and test work starts **after** development. The playbook calls this
  the traditional model ("QA gates at stage boundaries"). It replaces it with a loop where:
  - tests are written **with** the code
  - verification runs **continuously** inside each session
  - human attention is reserved for a few judgment gates
  - production problems feed back into the start of the loop

**The proposal:** keep every skill, script and guardrail we built, and change *when* they run
and *who must stop for them*:

1. **Shift QE left.** Use the quality rubric while the story is drafted, and design tests
   from the acceptance criteria before build starts.
2. **Build tests with the code.** The coding session writes and runs the automated tests
   named in its plan.
3. **Fewer human gates and more automatic checks.** DoR and DoD become automated checks,
   with named-person overrides, instead of meetings.
4. **Add the missing enforcement and feedback:** hooks, a QE pass in PR review, evals in CI,
   production feedback, and metrics.

---

## 2. Gap analysis

Priority: **P1** = do next, high value and low cost; **P2** = next quarter; **P3** = later,
once the basics are running.

### 2.1 Shape of the workflow

| Area | Original ideation | Current plugin | Playbook | Gap | Recommendation | Pri |
|---|---|---|---|---|---|---|
| Overall flow | Linear: story → gate → DoR → dev → test design → feasibility → scripting → run → triage → heal → defect → done | Same order, one skill per stage | A loop: intent → spec → plan → diff+tests → PR → deploy → monitoring writes the next intent | Linear; QE work is concentrated after dev | Reorder around the loop (Section 3). Keep the skills, change where they're used | P1 |
| Human gates | A gate at most stages | Quality gate, DoR, test-case review, defect confirmation, DoD, self-heal approval | Judgment gates only: PO accepts intent and spec, engineer accepts the plan, code owner approves the PR, release manager authorises prod. Gates asking a person stay out of the build | Too many stops; people on the critical path | Turn DoR and DoD into automated checks that pass by default, with named overrides. Keep people for judgment | P1 |
| Handoff artifacts | Not defined | `qe-artifacts/<ID>/0N-*.json`, with schemas | Committed to git: intent.md, spec.md, plan.md, diff, PR findings, incident record | Our files are working files, not committed, and not linked to the plan or PR | Commit QE artifacts next to intent/spec/plan, or link them by ID and commit SHA (see 2.5) | P2 |

### 2.2 Plan and Design

| Area | Original ideation | Current plugin | Playbook | Gap | Recommendation | Pri |
|---|---|---|---|---|---|---|
| Requirements | User stories written by hand or by Claude, then checked by a person | `us-quality-gate` scores a finished story | intent.md from an interview where Claude asks analyst questions; the PO corrects it before commit | Quality is inspected after drafting instead of built in | Add an **elicitation mode**: Claude uses the rubric criteria as its interview questions while drafting. The gate then becomes a confirming check that should usually pass | P1 |
| Quality gate | Score the story; block if low | Deterministic score with hard fails, run by an independent `story-gatekeeper` | No score gate; PO acceptance is the decision. Independent confidence gates appear when the loop runs headless | Blocking-and-rejecting creates rework loops | Keep the scored check, but make it **advisory to the PO** when the story came from elicitation and **blocking** for headless or incoming stories (tickets, incidents) | P2 |
| DoR | A separate gate before dev and test design | `check_dor.py`; `unknown` blocks | "Ready" = spec accepted, then plan accepted in plan mode | DoR is a separate ceremony | Run the DoR check **automatically when the spec is accepted**. Keep the QE-specific conditions (test environment, test data, dependencies); drop the ones already covered by spec acceptance | P2 |
| Test design timing | After development | `test-case-generation` requires DoR = ready | Tests are generated with the code; plan.md must name "the tests that prove it" | **Biggest gap.** Tests arrive too late to steer the build | Generate test cases from the **acceptance criteria and spec in Design**. The QE reviews the test design alongside spec acceptance. plan.md's *Proof* section cites the TC IDs | **P1** |
| Automation feasibility | A separate stage | Scored matrix with overrides | No equivalent | When AI writes the tests, the effort factor collapses; a separate stage adds a handoff | Fold it into test design as **layer selection** (unit/API/UI) plus a manual/exploratory flag. Keep the script as an optional check | P2 |

### 2.3 Build and Test

| Area | Original ideation | Current plugin | Playbook | Gap | Recommendation | Pri |
|---|---|---|---|---|---|---|
| Writing automated tests | A QE phase after feasibility | `automation-scripting` skill | The coding session writes tests with the code, following CLAUDE.md and skills | A separate QE scripting phase | The **coding session** writes the automated tests for its TC IDs using the automation conventions; QE reviews them in the PR. `automation-scripting` remains for backfilling regression suites | P1 |
| Verification inside the session | Not covered | Not covered | Feedback loop: one-command tests, quantifiable targets, iterate until green, paste output before "done" | Missing | Add a CLAUDE.md **verification block** template and a single test command convention to `automation-conventions.md` | P1 |
| Protecting the tests | Not covered | `check_heal_diff.py` for self-heal only | A **hook blocks test-file edits during fix tasks**; bug fixes start from a committed failing test | Only enforced in self-heal, and only after the fact | Ship a **PreToolUse hook** example that blocks assertion edits during fix and heal tasks (reusing the guardrail patterns). Note that it must go in project or managed settings, because plugin agents ignore hooks | P1 |
| Verifier | Not covered | `story-gatekeeper` (stories only) | A verifier subagent runs the app against plan.md in a fresh context and only reports | Missing for code changes | Add a `test-verifier` agent: runs the TCs named in plan.md, reports results, fixes nothing | P2 |
| Evals for our own skills | Not covered | `evals/` kit, run by hand | Evals run in CI on every change to CLAUDE.md, skills or hooks; the pass rate gates the merge; the suite keeps evolving | Manual, and the expected scores are placeholders | Add an `agent-evals` workflow for the plugin; calibrate with 20–30 real stories; **gate skill changes on the pass rate** | **P1** |

### 2.4 Pipeline, review and release

| Area | Original ideation | Current plugin | Playbook | Gap | Recommendation | Pri |
|---|---|---|---|---|---|---|
| Pipeline run | A stage | CI (not a skill) | CI | None | Keep as is | — |
| Triage | A stage | `triage-analyst`, read-only, headless in CI; code decides routing | "Start with read-only judgment steps": triage failed builds, summarise flaky tests | **Aligned** | Add its metric: share of failures triaged without paging a person | P2 |
| Self-heal | A stage | Draft PR only, guardrail in session and in the job, an approval step before it runs, Claude has no push rights | Write steps behind existing gates, always as PRs; at 3σ in Maintain, quarantine or open a revert PR | **Aligned** | Add the in-session hook (2.3). Consider routing flaky tests to **quarantine PRs** rather than a ticket | P2 |
| Defects | Raise in the tracker | `defect-raising`, duplicate check, human confirms | Small, bounded fix → a PR that starts from a **failing test**; larger → intent.md. The tracker stays the system of record through linkage | We only file tickets | Add routing: **(a)** the defect is recorded in the tracker; **(b)** for bounded bugs, a failing test is committed first, and the fix PR must make it pass without editing it; **(c)** larger bugs become an intent | P2 |
| PR review | Not in our flow | Not covered | Agentic review with `REVIEW.md` (bugs / security / compliance with spec and plan); findings inform the reviewer but don't decide; code owner approves | **Missing**, though this is where most QE value now sits | Add a **QE pass to REVIEW.md**: every AC has a test; no test was weakened or skipped; the *Proof* in plan.md was run; test data is self-contained | **P1** |
| DoD / testing complete | A final stage | `check_dod.py` (coverage, pass rate, open defects) | Eval pass rate and checks as merge gates; code owner approval; release manager for prod | A ceremony at the end | Run `check_dod.py` as a **PR or release check**. Sign-off becomes an override only, needed only when the check fails | P2 |
| Release gating | Not covered | Not covered | A hook as the approval gate; autonomy tiered by environment | Not QE-owned | Note only: QE supplies the evidence (DoD result, eval results) that the release hook reads | P3 |

### 2.5 Maintain, governance and measurement

| Area | Original ideation | Current plugin | Playbook | Gap | Recommendation | Pri |
|---|---|---|---|---|---|---|
| Production feedback | Ends at "testing completed" | Ends at DoD | Deterministic control bands → 1σ log / 2σ read-only diagnosis / 3σ PR or runbook → finding becomes an intent.md; **every incident becomes an eval** | **Missing** | Start with **QE metrics as bands**: CI failure rate, flaky rate, escaped defects. Each escaped defect adds a regression test and a story-gate eval case | P3 |
| Source of truth | Implied Jira | Local files | One source of truth per artifact (repo, legacy tool, or linkage) | Undecided | **Decide per artifact.** Suggested start: linkage, i.e. Jira or Xray stay the record, QE artifacts carry the issue key, and Jira holds the commit SHA | P1 (decision) |
| Enforcement layer | Not covered | Scripts and CI | Skills are advisory; hooks are deterministic; managed settings for non-negotiable rules | No hooks | Hooks (2.3), plus a managed-settings proposal for the platform team | P2 |
| Metrics | None | None | A leading and a lagging indicator for every play | **Missing** | Adopt the QE metric set in Section 5 | P1 |

---

## 3. Revised flow

### 3.1 Picture

```
                         ┌──────────────────────── human judgment gate ◆   automatic check ▣ ───────────┐

 PLAN      idea / ticket / incident
             └─ Claude drafts story (intent) using the QE rubric as interview questions
             └─ ▣ story check (us-quality-gate via story-gatekeeper; advisory if drafted, blocking if headless)
             └─ ◆ PO accepts story                                       artifact: story / intent.md

 DESIGN      └─ Claude drafts spec.md (policy skills)  ║  Claude drafts test design from AC
                                                       ║    (test-case-generation + layer selection)
             └─ ▣ DoR check runs on acceptance (env, test data, dependencies)
             └─ ◆ PO accepts spec; QE reviews test design in the same review
                                                       artifacts: spec.md, 03-test-cases.json

 BUILD       └─ plan mode: plan.md "Proof" cites TC IDs → ◆ engineer accepts plan
             └─ coding session writes code AND automated tests for those TCs
                  feedback loop: one test command, iterate until green
                  ▣ hook: no test or assertion edits during fix tasks
             └─ ▣ test-verifier subagent runs the Proof in a fresh context, reports only
                                                       artifacts: plan.md, diff + tests

 REVIEW      └─ ▣ agentic review (REVIEW.md, including the QE pass)   ▣ CI: tests, evals, check_dod as PR check
             └─ ◆ code owner approves                                 artifact: PR + findings

 PIPELINE    on a failed run:
             └─ ▣ triage-analyst (read-only) → ▣ routing decided by code
                    ├─ test bug (locator/timing/data) → ◆ approve → self-heal DRAFT PR → back to REVIEW
                    ├─ product bug → tracker record + failing test committed → fix PR → back to REVIEW
                    │                (bigger than one PR → new intent → PLAN)
                    ├─ flaky → quarantine PR + owner        ├─ environment → notify owner
                    └─ low confidence → person

 RELEASE     └─ ◆ release manager (the hook reads the DoD and eval evidence)

 MAINTAIN    ▣ control bands on CI failure rate, flaky rate, escaped defects
             └─ 2σ diagnose (read-only) · 3σ quarantine or revert PR
             └─ finding → new intent → PLAN        every incident → new eval and regression test
```

### 3.2 Stage by stage

| Stage | QE activity | Skill / agent | Artifact | Who decides | How it's enforced |
|---|---|---|---|---|---|
| Plan | Rubric-guided drafting; confirming story check | `us-quality-gate` (+ elicitation mode), `story-gatekeeper` | story / intent.md with AC IDs | PO | `score_gate.py`; blocking only for headless or incoming stories |
| Design | Test design from AC, with layer selection; DoR check | `test-case-generation` (+ folded feasibility), `definition-of-ready` | spec.md, `03-test-cases.json`, `02-dor-result.json` | PO accepts the spec; QE reviews the test design | Schema validation; `check_dor.py` runs on acceptance |
| Build | Tests written with the code; feedback loop; tests protected | `automation-scripting` conventions (read by the coding session), `test-verifier` (new) | plan.md with Proof citing TC IDs; diff + tests | Engineer accepts the plan | Plan mode; PreToolUse hook; single test command |
| Review | QE review pass; DoD as a check | `REVIEW.md` QE pass (new), `definition-of-done` | PR + findings, `09-dod-result.json` | Code owner | Branch protection; CI checks |
| Pipeline | Triage, self-heal, defect routing | `triage-analyst`, `self-heal-fixer`, `defect-raising` | `06-triage`, draft heal PR, `08-defects` | Approval for self-heal; person for low confidence | `triage_summary.py`, `check_heal_diff.py` (in the agent and in the job), dontAsk allowlists |
| Release | Supply the evidence | — | DoD and eval results | Release manager | Release hook (platform-owned) |
| Maintain | QE bands; incident → eval | Triage agent in read-only mode (2σ) | New intent; new eval case | Service owner / QE lead triages | Versioned `bands.yaml`; deterministic detection |

### 3.3 Human decisions: before and after

| Before (original ideation) | After (revised) |
|---|---|
| Person reviews the story | **PO accepts the story** (kept) |
| Quality gate pass/fail meeting | Automatic check; a person is only involved on fail or override |
| DoR meeting | Automatic check on spec acceptance; a person only for blockers |
| — | **PO accepts the spec; QE reviews the test design** (new, replaces the post-dev test review) |
| — | **Engineer accepts the plan** (new; the plan names the tests) |
| Feasibility sign-off | Removed (folded into test design) |
| Person reviews the scripts | Reviewed in the PR by the **code owner**, using the QE pass findings |
| Triage by a person | Automated; a person only for low confidence |
| Self-heal approval | **Kept** (approval step plus PR review) |
| Defect confirmation | Kept for tracker records; bounded fixes go through PR review instead |
| Testing-complete sign-off | Automatic check; a person only for overrides |
| — | **Release manager** (exists today; now fed QE evidence) |

There are still six judgment points, but they now sit where they add judgment rather than
along the critical path of every story.

---

## 4. Changes needed in `qe-workflow`

| # | Change | Type | Pri | Size |
|---|---|---|---|---|
| 1 | `test-case-generation`: accept a story or spec as input (drop the DoR=ready precondition); emit a *Proof* block for plan.md citing TC IDs | Edit skill | P1 | S |
| 2 | `REVIEW.md` template with a QE pass (AC→test coverage, no weakened or skipped tests, Proof executed, self-contained data) | New template | P1 | S |
| 3 | PreToolUse hook example: block assertion and test edits during fix and heal tasks; reuse the `check_heal_diff.py` patterns; document that it goes in `.claude/settings.json` or managed settings | New hook + docs | P1 | M |
| 4 | CLAUDE.md verification block and a single test command in `automation-conventions.md` | Edit template | P1 | S |
| 5 | `agent-evals` CI workflow for the plugin; replace the placeholder expectations with 20–30 QE-scored stories; gate skill PRs on the pass rate | New workflow + data | P1 | M (mostly the calibration effort) |
| 6 | Decide the source of truth per artifact; add issue-key and SHA linkage fields to the schemas | Decision + schema edit | P1 | S |
| 7 | `us-quality-gate`: elicitation mode (the rubric becomes interview questions while drafting) and an advisory vs blocking setting | Edit skill + config | P2 | M |
| 8 | Fold feasibility into test design (`suggested_layer`, `manual`/`exploratory` flag); keep `score_feasibility.py` optional | Edit skills | P2 | S |
| 9 | `defect-raising`: failing-test-first route for bounded bugs; larger bugs become an intent | Edit skill | P2 | M |
| 10 | `check_dod.py` as a PR or release status check in CI | New CI example | P2 | S |
| 11 | `test-verifier` agent (runs the Proof, reports only) | New agent | P2 | S |
| 12 | Flaky route → quarantine PR instead of a ticket | Edit triage/heal | P2 | S |
| 13 | QE control bands (`bands.yaml`) for CI failure rate, flaky rate and escaped defects; incident → eval procedure | New example | P3 | M |

### Implementation status (27 Nov 2026)

| # | Status |
|---|---|
| 1 | **Done**: test-case-generation starts from spec.md in Design and no longer waits for DoR; `implementation-plan` cites TC IDs in Proof, enforced by `check_sdlc.py plan` |
| 2 | **Done**: `dev-workflow/templates/REVIEW.md` with a QE pass, plus the `pr-review` skill and `pr-reviewer` agent |
| 3 | **Done**: `dev-workflow/hooks/guard_edits.py` (assertion changes, fix mode, protected paths), tested in a real session |
| 4 | **Done**: `dev-workflow/templates/CLAUDE.md` with a verification block |
| 5 | **Partly done**: `agent-evals` CI example; calibrating with real QE-scored stories is still to do |
| 6 | Open: team decision on the source of truth |
| 7 | **Partly done**: `intent-capture` does the rubric-guided elicitation; the advisory/blocking gate setting is still to do |
| 11 | **Done**: `test-verifier` agent |
| 8, 9, 10, 12, 13 | Not started |

Nothing gets deleted. The nine skills, three agents, scripts, schemas and CI example all
stay; they move to new positions in the flow.

---

## 5. QE metrics

Following the playbook's pattern, each change gets a leading indicator (moves early) and a
lagging indicator (confirms the outcome). Most can be read from git, PR metadata, CI logs and
the tracker.

| Area | Leading indicator | Lagging indicator |
|---|---|---|
| Story quality | Share of stories passing the check on the first attempt | Requirement rework: story or spec edits after the plan is accepted |
| Shift-left test design | Share of stories with test cases before build starts | Defects traced to missing or wrong acceptance criteria |
| Tests with the code | Share of PRs whose plan cites TC IDs; first-pass CI success for agent-written changes | Change failure rate |
| QE review pass | Share of PRs where the QE pass found nothing | Defects caught before merge vs escaped to production |
| Triage | Share of failed runs triaged without paging a person; time from failure to triage | Triage accuracy (human overrides of the agent's classification) |
| Self-heal | Time from failure to heal PR | Share of heal PRs merged without changes; share reverted |
| Defects | Time from triage to a failing test committed | Repeat defects of the same class |
| Skill evals | Eval pass rate on every skill change; time from incident to eval case | Gate decisions overridden by people |
| Maintain | Time from band breach to a triaged intent | Escaped defects over time |

---

## 6. Rollout

The phases follow the playbook's prerequisite order: start with what needs nothing first,
start read-only, then add write steps behind existing gates.

| Phase | Scope | Changes (Section 4) | Entry condition |
|---|---|---|---|
| **0: Foundations** | One pilot team, one repo | 4 (verification block), 6 (source-of-truth decision), 3 (test-protection hook) | None |
| **1: Shift left** | Pilot team | 1 (test design in Design), 2 (REVIEW.md QE pass), 5 (evals in CI), 7 (elicitation mode) | Phase 0 in place; eval cases collected |
| **2: Automate the pipeline side** | Pilot, then 2–3 teams | Turn on the CI example (read-only triage first, self-heal after 2–4 weeks of accurate triage), 9, 10, 11, 12, 8 | Triage accuracy is acceptable; self-heal approval environment configured |
| **3: Close the loop** | Teams on phase 2 | 13 (bands, incident → eval) | Rollback and quarantine routes rehearsed |

Measure before each phase begins (Section 5), so each phase has a baseline to compare against.

---

## 7. Open questions for the team

1. **Regulated sign-off.** Does our compliance regime require a named QE sign-off per story?
   If so, keep DoD as an explicit approval for regulated products only.
2. **User stories vs intent.md.** We can keep user stories as the Plan artifact. The playbook's
   point is how they are produced (by interview, corrected by the PO), not the format.
3. **Source of truth.** Repo, Jira/Xray, or linkage? This decides where `qe-artifacts` live
   and what auditors see.
4. **QE role shift.** QE time moves from writing and running scripts to designing tests in
   Design, owning the REVIEW.md QE pass, curating evals and triaging escalations. Do we need
   training, or changes to role descriptions?
5. **Who owns hooks and managed settings?** The playbook puts them with the platform team.
   QE owns the content of the test-protection rules.
6. **Pilot selection.** Pick a team with a stable test suite and good CI reports, so triage
   and self-heal have clean input.

---

*Sources: [`qe-skills-design-review.md`](qe-skills-design-review.md) (original feedback),
[`../qe-workflow/README.md`](../qe-workflow/README.md) (current plugin),
[`references/ai-native-sdlc-playbook.md`](references/ai-native-sdlc-playbook.md) (playbook notes).*
