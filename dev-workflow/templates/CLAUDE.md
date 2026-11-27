# <Service name>

<!-- Keep this under one page. Claude reads all of it at the start of every session.
     Rule: when Claude makes the same mistake twice, the correction goes in here. -->

## Commands
- Build: `<make build>` (healthy output ends with "<Build succeeded>")
- Test: `<make test>` (unit) · `<make itest>` (integration; needs <docker>)
- Lint: `<make lint>` (zero warnings)
- Run one test file: `<npx playwright test path/to/file.spec.ts>`

## Verifying your work
- Run build, test and lint before reporting any task complete, and paste the output.
- If a test fails, fix the code, not the test. Never skip, delete or weaken a test.
- For a bug fix, first write a test that reproduces the bug, run it, confirm it fails for
  the expected reason, and commit it. Then make it pass without editing that test.

## Conventions
- <language/framework versions, patterns, naming>
- Automated tests start with their TC ID, e.g. `TC-012 rejects expired card`.

## Architecture
- <top-level folders and what lives where>

## SDLC artifacts
- Intent, spec and plan live in `sdlc/<ID>/`. QE records live in `qe-artifacts/<ID>/`.
- Don't implement without an accepted `plan.md`. Update plan.md in the same commit when you deviate.

## Things Claude gets wrong
- <e.g. Do not bump dependency versions; the platform team owns them.>
