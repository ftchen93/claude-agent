# Comparing with a Company Implementation, and Whether to Adopt the AI-native SDLC

Two questions:

1. How safe is it to compare a company's internal QE implementation with the one in this
   repo?
2. Should the company's QE workflow follow Anthropic's AI-native SDLC playbook?

---

## 1. Safety of comparing a company implementation here

**One fact first: this repository is public.** Everything committed here (the plugin, the
docs, the PRs) can be seen by anyone. The current content is generic: the example stories,
IDs and data are invented, and nothing names a company. The company flow appears only at a
high level, in the design review and gap analysis. Check that you're comfortable with that
level of detail being public.

The risk comes from bringing **company material** into this setup. Here are the risks and
how to avoid each:

| Risk | Why it matters | What to do |
|---|---|---|
| **Confidentiality / IP** | Internal skills, rubrics, workflows, story examples, Jira data and internal URLs are usually company confidential | Check the company's AI-use and data-classification policy first. If unsure, ask your manager or security team |
| **Public repo** | Anything committed here is public, and git history keeps it even after deletion | **Never commit company content to this repo.** If you compare, keep it out of git, or use a private or company repo |
| **Personal vs company Claude account** | Personal and company (Team/Enterprise) accounts can have different data-retention and training settings and different contractual terms. The company's terms likely don't cover a personal account | Do work comparisons in the **company-provided** Claude account and environment, if there is one |
| **Ownership of this work** | Work assignments built in a personal account and a personal public repo may belong to the company under the employment contract | Ask whether this should move to a company repo, and whether it can stay public |
| **Secrets and personal data** | Real stories or test reports can contain customer data, credentials or hostnames | Never paste these anywhere, including into Claude, unless the environment is approved for that data class |

### Safe ways to do the comparison, from safest

1. **Bring this repo's content into the company environment.** It's generic and already
   public, so copying it in is low risk (check the open-source policy for licence and
   attribution). Run the comparison there, with the company's Claude account and repo.
   This is the cleanest option.
2. **Compare structure only, outside the company environment.** Describe the company
   version abstractly: stage names, which gates exist, which fields the schemas have, what's
   enforced by code versus by people. Leave out the actual rubric wording, examples, system
   names and data. A useful gap analysis can be done from that level of detail.
3. **Don't** paste or upload internal skill files, Jira exports or real test reports into a
   personal session or a public repo.

---

## 2. Should it follow the AI-native SDLC?

**Use it as a direction, not a standard to comply with.** Some reasons for caution:

- **It's vendor guidance.** Anthropic wrote it, and its tooling is Claude-specific. The
  *principles* are sound and largely vendor-neutral, and they match what QE good practice
  already says: shift left, build quality in, deterministic enforcement, traceability,
  evals. The *specific tools* are a choice the company should make on its own terms.
- **The playbook itself says to adopt it selectively.** It says the plays are modular,
  stages can be transformed in any order, and "most organizations sit somewhere between"
  the traditional and AI-native columns.
- **QE can't change the whole SDLC alone.** The Plan, Design and Build changes involve the
  PO, developers and the platform team. QE can adopt its own parts inside the current SDLC.

### Adopt now (QE-owned, low risk, useful even without AI)

- Test design from acceptance criteria *before* development
- A QE pass in PR review, covering every AC and no weakened tests
- Gates computed by code, with named-person overrides
- Read-only triage in CI
- Evals for our own skills
- Traceability through linked IDs and commit SHAs
- Metrics with a baseline measured first

### Adopt only once the prerequisites exist

- **Self-heal:** needs a stable suite, good test reports, and an approval step with review.
- **The fully automatic Maintain loop:** needs reliable monitoring, a rehearsed rollback and
  mature gates. The playbook itself puts this last.

### Hold back, or adapt, if

- **Regulation requires named QE sign-off.** Keep explicit approval for those products.
- **Test suites are flaky or reports are poor.** Triage and self-heal will produce noise;
  fix the basics first.
- **There's no CI test reporting, or no stable acceptance-criteria practice.** Start there.
- **The organisation isn't ready to replace user stories with intent.md.** Keep stories;
  what matters is how they're drafted, not the format.

### Recommendation

Pilot **Phase 0–1** of the gap analysis with one team. Measure the metrics before and
after. Let the results, not the playbook, decide how far to go.

---

*Related: [`qe-gap-analysis-and-revised-flow.md`](qe-gap-analysis-and-revised-flow.md) ·
[`references/ai-native-sdlc-playbook.md`](references/ai-native-sdlc-playbook.md) ·
[`agent-concepts-mapping.md`](agent-concepts-mapping.md)*
