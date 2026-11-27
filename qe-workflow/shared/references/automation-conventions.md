# Automation Conventions (TEMPLATE: fill in for your team)

The automation-scripting and pipeline-self-heal skills follow this file. Replace each
placeholder with your real conventions; until then the skills ask before assuming.

- **Framework and language:** <e.g. Playwright + TypeScript / Selenium + Java / pytest>
- **Test repo and path:** <repo name, e.g. tests/e2e/<feature>/>
- **Pattern:** <page object / screenplay / plain>, with an example file path
- **Locator strategy (in order of preference):** <data-testid > role > label > css; never xpath by index>
- **Waits:** explicit waits only; no fixed sleeps
- **Test data:** <factories / API seeding / fixtures path>; tests create and clean up their own data
- **Naming:** test title starts with the TC ID, e.g. `TC-012 rejects expired card`
- **Tags:** <@smoke @regression @story:PAY-1234>
- **Assertions:** <library>; one behaviour per test
- **Secrets:** read from environment or vault, never hard-coded
- **Run locally:** `<command>`
- **Lint/format:** `<command>`
