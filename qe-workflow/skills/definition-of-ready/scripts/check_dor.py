#!/usr/bin/env python3
"""Compute the Definition of Ready decision.

Usage: check_dor.py <dor-result.json> [--write]
Any required condition with status other than 'met' blocks. 'unknown' blocks too:
if nobody can show it is met, it is not met. Exit 0 = ready, 1 = blocked, 2 = invalid.
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
    errors = validate(result, load_json(plugin_file("shared/schemas/dor-result.schema.json")))
    checklist = load_json(plugin_file(gates_config()["definition_of_ready"]["checklist_file"]))
    given = {c["id"]: c for c in result.get("conditions", [])}
    for cond in checklist["conditions"]:
        if cond["id"] not in given:
            errors.append(f"condition '{cond['id']}' not assessed")
    if errors:
        print("INVALID INPUT:\n  - " + "\n  - ".join(errors))
        return 2

    blocking = []
    for cond in checklist["conditions"]:
        status = given[cond["id"]]["status"]
        if cond["required"] and status != "met":
            blocking.append(f"{cond['id']}: {status}")
        elif not cond["required"] and status in ("not_met", "unknown"):
            print(f"  warning (optional): {cond['id']} is {status}")
    decision = "blocked" if blocking else "ready"
    print(f"decision={decision.upper()}")
    for b in blocking:
        print(f"  blocking: {b}")
    if "--write" in sys.argv:
        result.update({"decision": decision, "blocking": blocking})
        result.setdefault("decided_by", "skill")
        write_json(path, result)
    return 0 if decision == "ready" else 1


if __name__ == "__main__":
    sys.exit(main())
