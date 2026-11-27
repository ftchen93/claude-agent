---
name: pr-review
description: Review a pull request or diff against REVIEW.md in four passes (bugs, security, compliance with spec and plan, QE test adequacy), with findings ranked Important or Nit and a machine-readable tally. Use when asked to review a PR, a branch, a diff or changes before merge.
---

# PR Review (Deploy stage)

Every PR gets the same review passes. Findings **inform** the human reviewer: they never
approve or block on their own, and the agent that wrote the code can't approve it.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- The diff: a PR number (fetch it with the available GitHub tools) or a branch range
  (`git diff <base>...<head>`).
- `REVIEW.md` at the repo root. If it's missing, use `../../templates/REVIEW.md` and say so.
- If they exist: `sdlc/<ID>/spec.md` and `plan.md` (find the ID from the branch name, the
  PR title or the plan), plus `qe-artifacts/<ID>/03-test-cases.json`.
- CLAUDE.md, for conventions.

## Steps
1. Read REVIEW.md and run each pass it defines. With the template, those are Bugs,
   Security, Compliance and QE.
2. For the **QE pass**, check mechanically where you can:
   - Map the spec's AC IDs to tests in the diff or suite (by TC ID in test titles).
     List any AC with no test.
   - Look at every removed or changed line in test files. Flag any removed or changed
     assertion, skip, `.only`, raised timeout or fixed sleep.
   - Check that the Proof output is in the PR description or comments.
3. For each finding give: pass, severity (Important or Nit), `file:line`, what's wrong, why
   it matters, and a concrete fix. Keep within the nit cap; skip what REVIEW.md says not to
   report.
4. End with the tally line exactly as REVIEW.md specifies, e.g.
   `REVIEW-TALLY: important=1 nit=3 qe_gaps=1`.
5. Post the review as a PR comment only if the user asks. If a mistake has now been
   flagged a second time across PRs, suggest the CLAUDE.md line that would prevent it.

## Rules
- Review the change, not the author. Be specific; no generic advice.
- Don't push fixes during a review unless asked (e.g. an `@claude` request on a comment).
