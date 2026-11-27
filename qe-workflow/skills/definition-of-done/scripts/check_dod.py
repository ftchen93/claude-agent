#!/usr/bin/env python3
"""Compute the Definition of Done (testing complete) decision.

Usage: check_dod.py <dod-result.json> [--write]
Checks metric thresholds from gates.json and required checklist conditions.
Exit 0 = done, 1 = not done, 2 = invalid input.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared" / "scripts"))
from qe_common import gates_config, load_json, plugin_file, validate, write_json  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    path = args[0]
    result = load_json(path)
    errors = validate(result, load_json(plugin_file("shared/schemas/dod-result.schema.json")))
    if errors:
        print("INVALID INPUT:\n  - " + "\n  - ".join(errors))
        return 2
    cfg = gates_config()["definition_of_done"]
    checklist = load_json(plugin_file(cfg["checklist_file"]))
    m = result["metrics"]
    blocking = []

    coverage = 100.0 * m["ac_covered_executed"] / m["ac_total"] if m["ac_total"] else 0.0
    if coverage < cfg["min_requirement_coverage_pct"]:
        blocking.append(f"AC coverage {coverage:.1f}% < {cfg['min_requirement_coverage_pct']}%")
    pass_rate = 100.0 * m["tests_passed"] / m["tests_executed"] if m["tests_executed"] else 0.0
    if pass_rate < cfg["min_pass_rate_pct"]:
        blocking.append(f"pass rate {pass_rate:.1f}% < {cfg['min_pass_rate_pct']}%")
    for sev, limit in cfg["max_open_defects"].items():
        n = m["open_defects"].get(sev, m["open_defects"].get(sev.capitalize(), 0))
        if n > limit:
            blocking.append(f"{n} open {sev} defect(s), allowed {limit}")

    given = {c["id"]: c for c in result["conditions"]}
    for cond in checklist["conditions"]:
        status = given.get(cond["id"], {}).get("status", "unknown")
        if cond["required"] and status != "met":
            blocking.append(f"{cond['id']}: {status}")

    decision = "not_done" if blocking else "done"
    print(f"coverage={coverage:.1f}% pass_rate={pass_rate:.1f}% decision={decision.upper()}")
    for b in blocking:
        print(f"  blocking: {b}")
    if "--write" in sys.argv:
        result.update({"decision": decision, "blocking": blocking})
        result.setdefault("decided_by", "skill")
        write_json(path, result)
    return 0 if decision == "done" else 1


if __name__ == "__main__":
    sys.exit(main())
