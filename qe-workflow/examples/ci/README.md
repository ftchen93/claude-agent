# CI example: triage and self-heal on a failed test run

`qe-triage.github-actions.yml` runs the QE agents headlessly when your test workflow fails.

```
test workflow fails ──> triage job ─────────────────────────────> job summary + artifact
                         triage-analyst agent writes 06-triage
                         validate.py checks it (code)
                         triage_summary.py decides eligibility (code)
                               │ heal_eligible == true
                               v
                        self-heal job   (waits for a person to approve the "self-heal" environment)
                         self-heal-fixer agent commits on self-heal/<run-id>
                         check_heal_diff.py re-checks the branch (code)
                         the job (not Claude) pushes and opens a DRAFT PR
```

## Setup

1. Make your test workflow upload its reports (JUnit XML, Playwright or Allure) as an
   artifact, for example:
   ```yaml
   - uses: actions/upload-artifact@v4
     if: always()
     with: { name: test-results, path: test-results/ }
   ```
2. Copy `qe-triage.github-actions.yml` to `.github/workflows/qe-triage.yml` in the test
   repo and change every `CHANGE ME`: the test workflow name, the plugin repo and ref, the
   artifact name, the dependency install step and `TEST_CMD`.
3. Add the repository secret `ANTHROPIC_API_KEY`.
4. Create an environment named `self-heal` with **required reviewers**
   (Settings > Environments). Without this, self-heal would run with no approval.
5. If the plugin repo is private, check it out with a token that can read it instead of
   the default `GITHUB_TOKEN`.

## Safety design

| Risk | Control |
|---|---|
| Model misroutes a failure into self-heal | `triage_summary.py` re-checks route, confidence and sub-type against `gates.json` |
| Malformed triage output | `validate.py` fails the job |
| Heal changes assertions or product code, or adds sleeps | `check_heal_diff.py` runs inside the agent **and** again in the job on the final branch |
| Claude pushes or merges | Not in its tool allowlist. The job pushes only after the guardrail passes, and opens a **draft** PR |
| Unreviewed automatic fixes | `self-heal` environment approval, then human PR review |
| Prompt injection from fork PRs | Workflow skips runs whose head repo is not this repo |
| Runaway cost | `--max-budget-usd` on each run, job timeouts |

Headless runs use `--permission-mode dontAsk`, which **denies** any tool use outside
`--allowedTools`. Plugin agents cannot carry their own permission modes or hooks, so this
allowlist is the real boundary. Keep it tight.

## Try it locally

```bash
mkdir -p /tmp/qe-ci && cp -r qe-workflow/examples/ci/sample-report /tmp/qe-ci/test-results
cd /tmp/qe-ci
claude -p "Triage test run 4711. Reports are in ./test-results/. Write the triage file to ./qe-artifacts/runs/4711/06-triage-4711.json." \
  --plugin-dir <path-to>/qe-workflow --agent qe-workflow:triage-analyst \
  --permission-mode dontAsk --allowedTools "Skill,Read,Write,Glob,Grep,Bash(python3:*)" \
  --max-budget-usd 3
python3 <path-to>/qe-workflow/shared/scripts/triage_summary.py qe-artifacts/runs/4711/06-triage-4711.json
```

The sample report has one product bug (wrong discount), one locator drift (`#promo-input`
renamed to `data-testid="promo-code"`) and three environment failures (auth service down).

## Not tested here
This workflow was not run on GitHub Actions. The triage and self-heal commands, tool
allowlists, validation, routing and guardrail steps were all run locally with the
same arguments.
