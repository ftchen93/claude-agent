---
name: intent-capture
description: Interview the originator of an idea, ticket or incident and write it up as intent.md, a version-controlled proto-spec with draft acceptance criteria. Use when someone has a new idea, feature request, problem, ticket or user story to write up, or asks to draft or refine a user story or requirement.
---

# Intent Capture (Plan stage)

Turns an idea into `sdlc/<ID>/intent.md`, in the originator's own words, ready for the PO
to accept. This replaces writing a user story by hand and then gating it: quality is built
in while drafting, by asking the questions the quality gate would otherwise ask later.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- The originator's description, a ticket (fetch it if a tracker tool is available), or an
  incident finding.
- The template: `../../templates/intent.md`.

## Steps
1. Let the originator describe the problem in their own words. Don't ask for formal
   language.
2. **Interview until the idea is concrete.** Ask one or two questions at a time, in this
   order, and skip what's already answered. These map to the QE quality rubric criteria:
   1. **Role and value:** who is affected, and what does better look like for them?
      How will we measure success?
   2. **Acceptance criteria:** walk through the main scenario, then ask what happens when
      the input is invalid, the user isn't allowed, or a dependency is down. Write each as
      Given/When/Then.
   3. **Testability:** replace vague words ("fast", "easy", "secure") with a number or an
      observable result.
   4. **Business rules and data:** limits, formats, rounding, permissions, exact error
      messages.
   5. **Scope:** what is explicitly out of scope? Is it small enough for one sprint?
   6. **Dependencies:** which systems, teams, feature flags and environments are involved?
   7. **Non-functional:** only if relevant: performance, security, accessibility, compliance.
3. Write `sdlc/<ID>/intent.md` from the template. Number the criteria `AC-1..n`. Put
   anything the originator couldn't answer under **Open questions**. Don't invent answers.
4. Show it to the originator and correct anything Claude misunderstood.
5. Run the structural check and fix any problems:
   ```bash
   python3 ../../scripts/check_sdlc.py intent sdlc/<ID>/intent.md
   ```
6. If the `qe-workflow` plugin is installed, run its **us-quality-gate** skill on
   intent.md as a **confirming** check. If it fails, the author questions show what the
   interview missed; ask them and update the file.
7. Tell the originator the next step: commit intent.md and ask the PO to accept it, by
   merge or review. **Don't commit or open a PR unless asked.**

## Rules
- The originator's words beat Claude's assumptions. Mark guesses as open questions.
- Keep the IDs stable. Later stages carry `AC-n` forward unchanged.
- Incidents and tickets that arrive without a person (e.g. from monitoring) still go
  through PO review before commit.
