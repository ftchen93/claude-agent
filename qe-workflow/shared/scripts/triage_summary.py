#!/usr/bin/env python3
"""Summarise a triage file and decide, deterministically, what may run next.

Usage: triage_summary.py <06-triage-RUN.json>
Prints a Markdown summary (for a CI job summary or a chat reply). When GITHUB_OUTPUT is
set, also writes these step outputs:
  heal_eligible=true|false   at least one failure meets every self-heal rule
  heal_count=<n>
  product_bugs=<n>
  needs_human=<n>            failures routed to human-review
A failure is eligible for self-heal only if route == pipeline-self-heal, confidence is
high or medium, and sub_type is in self_heal.allowed_categories in gates.json. This
re-checks the model's routing instead of trusting it.
Exit 0 on success, 2 on invalid input.
"""
import os
import sys
from collections import Counter

from qe_common import PLUGIN_ROOT, gates_config, load_json, validate


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    data = load_json(sys.argv[1])
    errors = validate(data, load_json(PLUGIN_ROOT / "shared" / "schemas" / "triage.schema.json"))
    if errors:
        print("INVALID triage file:\n  - " + "\n  - ".join(errors))
        return 2
    allowed = set(gates_config()["self_heal"]["allowed_categories"])
    failures = data["failures"]

    def eligible(f):
        return (f["route"] == "pipeline-self-heal" and f["confidence"] in ("high", "medium")
                and f.get("sub_type") in allowed)

    heal = [f for f in failures if eligible(f)]
    downgraded = [f for f in failures if f["route"] == "pipeline-self-heal" and not eligible(f)]
    cats = Counter(f["category"] for f in failures)
    product = [f for f in failures if f["category"] == "product_bug"]
    human = [f for f in failures if f["route"] == "human-review"] + downgraded

    order = {"product_bug": 0, "test_bug": 1, "test_data": 2, "flaky": 3, "environment": 4}
    out = [f"## QE triage: run {data['run_id']}", ""]
    out.append(" | ".join(f"**{k}** {cats.get(k, 0)}" for k in order))
    out += ["", "| Test | Category | Confidence | Route |", "|---|---|---|---|"]
    for f in sorted(failures, key=lambda f: order.get(f["category"], 9)):
        cat = f["category"] + (f" ({f['sub_type']})" if f.get("sub_type") not in (None, "none") else "")
        route = f["route"] if f not in downgraded else f"~~{f['route']}~~ human-review"
        out.append(f"| {f['test']} | {cat} | {f['confidence']} | {route} |")
    out.append("")
    if product:
        out.append(f"**{len(product)} product bug(s):** run the defect-raising skill to draft defects for review.")
    if downgraded:
        out.append(f"**{len(downgraded)} failure(s) routed to self-heal did not meet the rules** "
                   "(confidence or sub-type) and need a human instead.")
    out.append(f"**Self-heal eligible:** {len(heal)}")
    print("\n".join(out))

    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a", encoding="utf-8") as fh:
            fh.write(f"heal_eligible={'true' if heal else 'false'}\n")
            fh.write(f"heal_count={len(heal)}\nproduct_bugs={len(product)}\nneeds_human={len(human)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
