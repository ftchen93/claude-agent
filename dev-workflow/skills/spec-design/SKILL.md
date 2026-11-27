---
name: spec-design
description: Turn an accepted intent.md into spec.md, a requirements and design spec that applies the organisation's policy skills and flags areas of concern for the product owner. Use when asked to write a spec, requirements, design or technical design from an intent, story or ticket.
---

# Requirements and Design (Design stage)

Produces `sdlc/<ID>/spec.md` from an accepted intent. Policy is applied **while** the spec is
written, not discovered in review weeks later. The PO reviews the spec; they don't write it.

Paths are relative to this skill's directory. Resolve them to absolute paths, and run
each script as one simple command (no `cd`, `&&`, `;` or pipes), so it also works in
headless runs that only allow simple commands. If one command is denied, retry it as a
single simple command before concluding that commands are blocked.

## Inputs
- `sdlc/<ID>/intent.md`, accepted by the PO. If its status isn't accepted, say so and ask
  whether to continue as a draft.
- The organisation's policy skills (security, compliance, brand, UX, API design). Use every
  one that applies. If none are installed, say so in **Policy compliance**.
- The codebase, read-only, to fit the design to what exists.
- Template: `../../templates/spec.md`.

## Steps
1. Read intent.md and the relevant code. Don't edit code in this stage.
2. Write spec.md from the template:
   - Write each criterion as `- AC-n: <text>`. Labels such as (new) go after the colon.
   - **Carry every AC forward with the same ID.** Sharpen the wording if needed, but never
     renumber. New criteria get the next free number. Criteria you think should go are
     marked `(withdrawn)` with a reason; the PO decides.
   - Trace each functional requirement to AC IDs.
   - In **Policy compliance**, list each policy skill applied and how the design complies.
   - **Areas of concern is required.** Flag every contradiction between policies, every
     open question that blocks design, and every risky assumption, each with the person who
     must decide. These are what an analyst would have escalated.
   - **Test strategy notes:** risky areas, test data needs and environments for QE.
3. Run the structural and traceability check:
   ```bash
   python3 ../../scripts/check_sdlc.py spec sdlc/<ID>/spec.md --intent sdlc/<ID>/intent.md
   ```
4. Present the areas of concern first, then a summary. The PO resolves each concern with
   its owner before engineering sees the spec.
5. Next step for the user:
   - the PO accepts the spec (escalating to a tech lead for higher-risk work)
   - in parallel, QE runs **qe-workflow:test-case-generation** from this spec, and
     **qe-workflow:definition-of-ready**
   - after that, **implementation-plan**

## Rules
- A person always decides whether the spec goes to build.
- Never resolve a policy conflict yourself by picking one policy. Flag it.
