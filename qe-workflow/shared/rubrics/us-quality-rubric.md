# User Story Quality Rubric

Machine-readable weights live in `us-quality-rubric.json`. This file is the scoring guide
the model follows. **Change weights in the JSON, not here.**

Each criterion is scored 0–4. Criteria marked N/A-allowed can be scored `null` when they
genuinely do not apply (e.g. no UI in a backend story); their weight is then dropped from
the total.

| Score | Meaning |
|---|---|
| 0 | Missing entirely |
| 1 | Mentioned but unusable (vague, contradictory) |
| 2 | Present but has gaps a tester would need to ask about |
| 3 | Good: a tester could design tests with at most minor questions |
| 4 | Excellent: complete, precise, nothing to ask |

## Criteria and anchors

### role_and_value (weight 10)
- 0: no role or purpose. 2: role present, value implied. 4: role, capability and measurable value.

### acceptance_criteria (weight 25) — hard fail below 2
- 0: none. 1: restates the story title. 2: happy path only. 3: happy + main negative paths.
- 4: Given/When/Then, each criterion independently verifiable, edge cases covered.

### testability (weight 20) — hard fail below 2
- Penalise unquantified adjectives: "fast", "intuitive", "secure", "user-friendly", "etc.".
- 4: every expected outcome can be observed and asserted.

### business_rules_and_data (weight 15)
- Validations, limits, formats, rounding, permissions, error messages.

### scope_clarity (weight 10)
- 4: explicit in-scope / out-of-scope list and sized to one sprint.

### dependencies_and_assumptions (weight 10)
- Upstream/downstream systems, feature flags, data migrations, other teams.

### non_functional (weight 5, N/A allowed)
### ux_reference (weight 5, N/A allowed)

## Evidence rule
Every score must quote or point to the text that justifies it. A score with no evidence
is treated as 0 by reviewers. For scores below 3, state the specific question the author
must answer to raise it.
