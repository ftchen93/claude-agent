# claude-agent
To learn and build claude agent

## Contents

- [`qe-workflow/`](qe-workflow/README.md): Claude Code plugin with Quality Engineering
  skills for the SDLC: user story quality gate, Definition of Ready, test case generation,
  automation feasibility and scripting, test run triage, pipeline self-heal, defect raising
  and Definition of Done.
- [`docs/qe-skills-design-review.md`](docs/qe-skills-design-review.md): design review of the QE-workflow-as-skills approach.
- [`docs/qe-gap-analysis-and-revised-flow.md`](docs/qe-gap-analysis-and-revised-flow.md): gap analysis of the QE workflow against the playbook, with a revised flow, change backlog, metrics and rollout.
- [`docs/agent-concepts-mapping.md`](docs/agent-concepts-mapping.md): how skills, agents and plugins map to classic agent development concepts (prompting, context, RAG, tools, memory, orchestration).
- [`docs/comparison-safety-and-adoption.md`](docs/comparison-safety-and-adoption.md): how to compare with a company implementation safely, and how far to adopt the AI-native SDLC.
- [`docs/references/ai-native-sdlc-playbook.md`](docs/references/ai-native-sdlc-playbook.md): reference notes on Anthropic's *AI-native SDLC playbook*, with a map to `qe-workflow`.
- [`dev-workflow/`](dev-workflow/README.md): Claude Code plugin with the development-side
  SDLC skills that pair with `qe-workflow`: intent capture, requirements and design spec,
  implementation plan with test Proof, build with tests, agentic PR review, an edit-guard
  hook, and CI examples.
- `tests/`: unit tests for every deterministic script, run by `.github/workflows/plugin-ci.yml`.
- `.claude-plugin/marketplace.json`: makes this repo installable as a plugin marketplace
  (both plugins).

All examples (stories, IDs, names, systems) are invented. Nothing here describes a real
company.
