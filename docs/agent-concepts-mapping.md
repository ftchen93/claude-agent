# Skills and Plugins vs Classic Agent Development

How the `qe-workflow` approach (Claude Code skills, agents and plugins) relates to the
fundamentals of agent development: LLMs, prompting, context management (上下文管理), RAG,
function calling and tool use, task breakdown, memory, and workflow orchestration.

**Short answer:** it isn't a different idea. It's the same agent-building concepts, but you
**configure** them on an agent that already exists (Claude Code) instead of **coding** them
yourself on top of a raw LLM API.

## The building blocks map one to one

| Agent concept | If you build the agent yourself | Where it is in our QE plugin |
|---|---|---|
| **LLM** | Call the model API | Claude Code calls it; agents pick a model (`model: opus` / `sonnet`) |
| **Prompting** | Write system prompts and templates | `SKILL.md` and agent `.md` files are prompts: instructions, rubrics, examples |
| **Context management (上下文管理)** | Decide what goes in the context window, trim and summarise | Skills load **only when relevant** (progressive disclosure); subagents get a **fresh, separate context** (triage reads big logs there and returns only a summary) |
| **RAG** | Embed documents, retrieve the top-k chunks, put them in the prompt | No vector database: the agent **searches on demand** with Read, Grep and Glob, and `shared/references/` is a small knowledge base it reads when needed. MCP connectors (Jira, TestRail) are live retrieval |
| **Function calling / tool use** | Define JSON tool schemas and handle the calls | Built-in tools (Read, Edit, Bash…) plus MCP servers; `--allowedTools` restricts them |
| **Task breakdown** | Planner prompts, sub-task queues | One skill per stage; numbered steps inside each skill; plan mode; subagents for subtasks |
| **Memory** | A conversation buffer, a vector store, long-term memory | **Files are the memory:** `qe-artifacts/*.json` handoffs, CLAUDE.md for rules that persist, git history as the long-term record |
| **Workflow orchestration** | LangGraph, state machines, your own code | The artifact chain (each stage reads the previous file), **routing decided by scripts** (`triage_summary.py`), CI as the scheduler |
| **Guardrails** | Output validators, moderation | JSON schemas plus `validate.py`, gate scripts, `check_heal_diff.py`, tool allowlists, hooks |
| **Evaluation** | Eval harness and test sets | `evals/` with expected outcomes and a consistency check across runs |

So the whole QE plugin is an agent system. The agent loop (think → call a tool → observe →
repeat) is already built into Claude Code, so we didn't write it.

## What is actually different

**1. You configure instead of coding.** In classic agent development, you write the loop,
the tool executor, retries, context trimming and state management. Here, the harness
provides all of that, and your work is mostly writing *knowledge* (skills), *roles*
(agents) and *boundaries* (permissions, hooks, scripts). That's much faster, and domain
experts like QE engineers can maintain it, not only ML engineers.

**2. Retrieval is agentic, not RAG-first.** Classic RAG retrieves once, before the model
thinks. Here the model decides what to read, reads it, and reads more if needed. That works
well for code, logs and structured documents. You would still add real RAG (through an MCP
search tool) for a large unstructured corpus, like thousands of old defects or Confluence
pages, where searching file by file is too slow.

**3. Memory lives in files and git, not hidden state.** Every handoff is a readable file,
and every decision is committed. You lose some of the "agent remembers everything"
convenience. You gain auditability, re-runnable stages and review in PRs, which is what a
QE or regulated process needs.

**4. Code holds the decisions, not the orchestration framework.** Many agent frameworks let
the LLM decide the next step. We put the important decisions in deterministic scripts (gate
scores, routing, guardrails) and let the model do the judgment work. Anthropic's AI-native
SDLC playbook follows the same principle: "detection is deterministic", and "skills are
advisory, hooks are deterministic".

**5. The unit of reuse is different.** Classic: a Python package or a graph definition.
Here: a plugin (skills + agents + scripts) that a team installs, with versions, a
marketplace and permission controls.

## When to build it the classic way instead

Move down to the **Claude Agent SDK** or the raw API when you need:

- an agent inside your **own product or service**, like a web app or a webhook service,
  rather than a developer tool
- **custom control of the loop**, such as your own state machine, streaming UI or complex
  multi-agent graphs
- **high-volume, low-latency** calls where the harness overhead matters
- **semantic retrieval over a large corpus** (real RAG)

The skills, schemas and scripts we wrote carry over. The Agent SDK can load the same skills
and agents, so moving down a layer is incremental rather than a rewrite.

## In one line

Agent development fundamentals are the *engine parts*. Claude Code with skills, agents and
plugins is a *car built from those parts*. You're designing the route, the rules of the
road and the checkpoints, rather than building the engine. Knowing the parts still matters:
it's why we restricted tools, separated contexts, used files as memory and put the decisions
in code.

---

*Related: [`qe-skills-design-review.md`](qe-skills-design-review.md) ·
[`qe-gap-analysis-and-revised-flow.md`](qe-gap-analysis-and-revised-flow.md) ·
[`references/ai-native-sdlc-playbook.md`](references/ai-native-sdlc-playbook.md)*
