---
name: implementation-plan
description: Produce plan.md, the implementation plan for an accepted spec, naming the files that change, the order of work, the risks and the Proof (the test cases that prove it, by TC ID). Use in plan mode, or when asked to plan the implementation of a spec, story or change before writing code.
---

# Implementation Plan (Build stage, before any code)

Nothing is implemented without an accepted plan. The plan's **Proof** section ties the
change to QE's test cases, so the coding session knows exactly which tests must pass.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- `sdlc/<ID>/spec.md` (accepted) and `sdlc/<ID>/intent.md`.
- `qe-artifacts/<ID>/03-test-cases.json` from **qe-workflow:test-case-generation**. If it
  doesn't exist, say so: either QE generates the cases first (preferred), or the user
  explicitly accepts a plan whose Proof lists tests you propose. Record that choice.
- The codebase (read-only) and CLAUDE.md.
- Template: `../../templates/plan.md`.

## Steps
1. Work in **plan mode** if available: read, don't edit.
2. Draft plan.md:
   - **Files that change:** every file, marked new or changed, with why.
   - **Order of work:** small steps; each names the TC IDs it makes pass.
   - **Risks** and **Alternatives considered**.
   - **Proof:** the single test command, then each cited TC with its AC and where its test
     lives (existing test, or one this change adds). List manual and exploratory TCs and who
     runs them.
3. **Challenge the plan before showing it:** what could this break, which step is riskiest,
   and what did you choose not to do? Fold the answers into Risks and Alternatives.
4. Run the traceability check, and fix the plan until it passes:
   ```bash
   python3 ../../scripts/check_sdlc.py plan sdlc/<ID>/plan.md \
     --test-cases qe-artifacts/<ID>/03-test-cases.json --spec sdlc/<ID>/spec.md
   ```
   It fails if a P1 test case isn't cited, a cited TC doesn't exist, or an AC isn't covered.
5. Iterate with the engineer until someone who never saw this conversation could implement
   the change from the plan alone.
6. When the engineer accepts it, set `Status: accepted (by <name>, <date>)`. Routine changes
   are accepted by the engineer; higher-risk ones by a tech lead or architect.
7. Next step: **implement-with-tests**.
