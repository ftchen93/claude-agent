# dev-workflow plugin

Development-side SDLC skills that pair with [`qe-workflow`](../qe-workflow/README.md).
Together they cover the loop from Anthropic's *AI-native SDLC playbook*
([notes](../docs/references/ai-native-sdlc-playbook.md)): each stage commits an artifact
the next stage reads, people decide at a few judgment gates, and code enforces the rest.

```
PLAN     intent-capture ─────────> sdlc/<ID>/intent.md      ◆ PO accepts
           (rubric-guided interview; qe:us-quality-gate confirms)
DESIGN   spec-design ────────────> sdlc/<ID>/spec.md        ◆ PO accepts (areas of concern resolved)
           ║ in parallel: qe:test-case-generation ──> qe-artifacts/<ID>/03-test-cases.json
           ║              qe:definition-of-ready  ──> 02-dor-result.json
BUILD    implementation-plan ────> sdlc/<ID>/plan.md        ◆ engineer accepts
           (Proof cites TC IDs; check_sdlc.py enforces coverage)
         implement-with-tests ───> code + tests, Proof green (feedback loop; failing-test-first for bugs)
           guard_edits.py hook: no weakened tests · test-verifier agent: fresh-context check
REVIEW   pr-review / pr-reviewer ─> findings + REVIEW-TALLY  ◆ code owner approves
           (bugs · security · compliance with spec/plan · QE)
PIPELINE qe:testrun-triage → qe:pipeline-self-heal / qe:defect-raising   (see qe-workflow)
```

## Contents

| Kind | Name | What it does |
|---|---|---|
| Skill | `intent-capture` | Interviews the originator using the QE rubric's questions; writes `intent.md` with draft `AC-n` |
| Skill | `spec-design` | intent → `spec.md`; applies the organisation's policy skills; **Areas of concern** required; keeps AC IDs |
| Skill | `implementation-plan` | spec → `plan.md` with Files, Order, Risks, Alternatives, and **Proof** citing TC IDs |
| Skill | `implement-with-tests` | Builds code and tests together until the Proof is green; failing-test-first bug-fix mode |
| Skill | `pr-review` | Four passes from `REVIEW.md`, Important/Nit findings, machine-readable tally |
| Agent | `test-verifier` | Runs the Proof in a fresh context; reports VERIFIED/NOT VERIFIED; never fixes |
| Agent | `pr-reviewer` | Independent, read-only reviewer using `pr-review` |
| Script | `scripts/check_sdlc.py` | Deterministic checks: intent and spec completeness, AC carry-forward, plan Proof coverage vs test cases |
| Hook | `hooks/guard_edits.py` | Blocks assertion changes, any test edit in fix mode, and protected paths |
| Templates | `templates/` | `intent.md`, `spec.md`, `plan.md`, `CLAUDE.md` (with verification block), `REVIEW.md` (with QE pass) |
| Example | `examples/sdlc/PAY-101/` | A complete intent → spec → plan chain that passes every check, linked to `qe-workflow/examples/qe-artifacts/PAY-101/03-test-cases.json` |
| CI | `examples/ci/` | PR review, spec-from-intent, continuous evals ([README](examples/ci/README.md)) |

## Set up in a product repo

1. Install both plugins from this marketplace:
   ```
   /plugin marketplace add <path-or-git-url-of-this-repo>
   /plugin install dev-workflow@qe-marketplace
   /plugin install qe-workflow@qe-marketplace
   ```
2. Copy `templates/CLAUDE.md` to the repo root and fill it in: commands, conventions, and
   "things Claude gets wrong". Keep it under a page.
3. Copy `templates/REVIEW.md` to the repo root and adjust the passes.
4. **Install the edit guard as a hook.** Plugin agents ignore hooks, so it must go in
   settings: `.claude/settings.json` for the team, or managed settings if it's
   non-negotiable.
   ```json
   {"hooks": {"PreToolUse": [{"matcher": "Edit|MultiEdit|Write",
     "hooks": [{"type": "command", "command": "python3 /path/to/dev-workflow/hooks/guard_edits.py"}]}]}}
   ```
   Optionally, list protected globs in `.claude/protected-paths`.
5. Install your organisation's **policy skills** (security, compliance, brand, UX, API).
   `spec-design` applies whatever is installed, and says so when nothing is.

## How the gates are enforced

| Gate | Decided by | Enforced by |
|---|---|---|
| Intent complete | PO accepts | `check_sdlc.py intent`; qe `score_gate.py` as a confirming check |
| Spec complete and traceable | PO accepts (tech lead for higher risk) | `check_sdlc.py spec --intent`: sections, concerns, AC carry-forward |
| Plan proves every AC | Engineer accepts | `check_sdlc.py plan`: cited TCs exist, all P1 cited, all ACs covered |
| Tests not weakened | n/a (always) | `guard_edits.py` hook; `pr-review` QE pass; qe `check_heal_diff.py` for self-heal |
| Work verified | n/a | Proof output pasted; `test-verifier` agent |
| Merge | Code owner | Branch protection; review findings inform but never approve |

## What was tested

- `check_sdlc.py` and `guard_edits.py` have unit tests in `../tests/test_scripts.py`, which
  run in `.github/workflows/plugin-ci.yml`.
- **The hook in a real session:** asked to change an expected value, Claude was blocked and
  the file stayed unchanged.
- **`spec-design` headless** (spec-from-intent command): it carried every AC forward, added
  new ones, flagged nine owned concerns, ran `check_sdlc.py` itself, and got SPEC CHECK OK.
- **`pr-reviewer` headless** on a seeded PR: it found the planted assertion change and the
  untested AC, plus real bugs, and emitted a parseable tally.
- **`test-verifier` headless:** NOT VERIFIED, with per-TC evidence; modified nothing.
- **Not run end to end yet:** `intent-capture` (an interactive interview),
  `implementation-plan` and `implement-with-tests` on a real codebase. The CI workflows
  haven't run on GitHub Actions; their commands were run locally with the same flags.
