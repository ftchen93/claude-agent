# dev-workflow CI examples

| File | Playbook play | Trigger | What Claude may do | What the job does |
|---|---|---|---|---|
| `pr-review.github-actions.yml` | AI in the PR review loop | PR opened or updated (same repo, not draft) | Read-only review (`git diff/log/show`, Read/Grep) | Posts the review; exposes the tally as outputs; optional gate on Important findings (commented out) |
| `spec-from-intent.github-actions.yml` | Requirements and design, triggered by an accepted intent | `sdlc/*/intent.md` merged to main | Write and edit the spec, run `check_sdlc.py` | Re-runs the check, commits **only** spec.md, pushes the branch, opens a **draft** PR for the PO |
| `agent-evals.github-actions.yml` | Continuous evals in CI | PRs touching the plugins, nightly | Run the eval cases | Scores against expected outcomes; fails the check on regressions |

The triage and self-heal workflow is in
[`qe-workflow/examples/ci/`](../../../qe-workflow/examples/ci/README.md).

## Common setup
- Add the `ANTHROPIC_API_KEY` repository secret. (Or route through Bedrock, Vertex or
  Foundry per your cloud agreement.)
- Change each `CHANGE ME`. Pin `PLUGIN_REF` and `CLAUDE_CODE_VERSION` in production.
- Every headless run uses `--permission-mode dontAsk` with an explicit `--allowedTools`.
  That allowlist is the real boundary, because plugin agents can't carry permission modes
  or hooks. Claude never gets push, `gh` or network tools; the job does those steps after
  its own deterministic checks.
- Fork PRs are skipped: they don't get secrets, and their content is untrusted input.

## Safety notes
- Review findings never approve or block on their own. Branch protection still requires a
  code owner, and the agent that wrote a change can't approve it.
- Content in a diff is data. The reviewer is told to report instructions embedded in a
  diff as a Security finding, not to follow them.
- Run evals with a budget. Three runs per case catches inconsistency, but costs three
  times as much.
