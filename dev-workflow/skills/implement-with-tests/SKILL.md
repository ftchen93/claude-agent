---
name: implement-with-tests
description: Implement an accepted plan.md, writing the code and its automated tests together and iterating until the Proof passes, with a failing-test-first mode for bug fixes. Use when asked to implement, build or code a planned change, or to fix a bug.
---

# Implement with Tests (Build and Test stages)

Code and its tests are written together, and the session checks its own work before a
person sees it. **What reaches the reviewer has already passed the Proof.**

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- An **accepted** `sdlc/<ID>/plan.md`. If there's no accepted plan, stop and run
  **implementation-plan** first.
- `qe-artifacts/<ID>/03-test-cases.json` for the cited TCs (steps, data, expected results).
- CLAUDE.md, for the commands, the verification rules and the conventions.
- If `qe-workflow` is installed, its `shared/references/automation-conventions.md`.

## Feature mode (default)
1. Follow the plan's Order of work. After each step, run the tests it names.
2. For each TC the plan says this change adds, write the automated test:
   - The title starts with the TC ID.
   - Every `expected` item becomes an assertion.
   - The test creates and cleans up its own data.
   - Waits are explicit; never use fixed sleeps.
3. **Feedback loop:** run the Proof command. Fix the code, re-run, and repeat until it's
   green. Run build and lint too.
4. If you deviate from the plan (a file not listed, a step changed), record it in plan.md's
   **Deviations** in the same commit.
5. Before reporting done, paste the literal output of the Proof command, build and lint.
   If the `test-verifier` agent is available, have it run the Proof in a fresh context and
   include its report.

## Bug-fix mode (failing test first)
1. Write a test that reproduces the bug. Run it, and confirm it **fails for the expected
   reason**. Show the output.
2. Ask the user to commit the failing test, or commit it yourself if asked.
3. Turn on fix mode, so the edit-guard hook (if installed) blocks test edits:
   create `.claude/fix-mode`.
4. Make the test pass by changing **product code only**. If you believe the test itself is
   wrong, stop and ask.
5. Run the full Proof or suite, paste the output, then delete `.claude/fix-mode`.

## Rules
- Never skip, delete or weaken a test to get green. Never change an expected value unless
  the spec changed.
- Don't add retries to hide flakiness. Report it.
- Commit or open a PR only if the user asks.
