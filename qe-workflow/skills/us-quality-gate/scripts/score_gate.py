#!/usr/bin/env python3
"""Compute the user story quality gate decision from per-criterion scores.

Usage: score_gate.py <quality-report.json> [--write]
  Reads the model's criterion scores, applies weights, N/A handling, hard-fail rules
  and the pass threshold from shared/config/gates.json. Prints the result; with --write,
  updates total_score, decision and hard_fail_reasons in the file.
Exit 0 = pass, 1 = fail, 2 = invalid input.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared" / "scripts"))
from qe_common import gates_config, load_json, plugin_file, validate, write_json  # noqa: E402


def score(report):
    cfg = gates_config()["us_quality_gate"]
    rubric = load_json(plugin_file(cfg["rubric_file"]))
    max_score = rubric["scale"]["max"]
    given = {c["id"]: c for c in report["criteria"]}
    problems = []

    weighted, total_weight = 0.0, 0.0
    for crit in rubric["criteria"]:
        entry = given.get(crit["id"])
        if entry is None:
            problems.append(f"criterion '{crit['id']}' was not scored")
            continue
        s = entry["score"]
        if s is None:
            if not crit["na_allowed"]:
                problems.append(f"criterion '{crit['id']}' cannot be N/A")
            continue
        weighted += crit["weight"] * s / max_score
        total_weight += crit["weight"]
    unknown = set(given) - {c["id"] for c in rubric["criteria"]}
    for u in sorted(unknown):
        problems.append(f"unknown criterion '{u}'")
    if problems:
        return None, problems

    total = round(100 * weighted / total_weight, 1) if total_weight else 0.0
    hard_fail = []
    for rule in cfg["hard_fail"]:
        s = given[rule["criterion"]]["score"]
        if s is not None and s < rule["min_score"]:
            hard_fail.append(f"{rule['criterion']} scored {s} (minimum {rule['min_score']})")
    decision = "pass" if total >= cfg["pass_threshold"] and not hard_fail else "fail"
    return {"total_score": total, "decision": decision, "hard_fail_reasons": hard_fail,
            "pass_threshold": cfg["pass_threshold"]}, []


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    path = args[0]
    report = load_json(path)
    schema = load_json(plugin_file("shared/schemas/quality-report.schema.json"))
    errors = validate(report, schema)
    if errors:
        print("INVALID INPUT:\n  - " + "\n  - ".join(errors))
        return 2
    result, problems = score(report)
    if problems:
        print("INVALID INPUT:\n  - " + "\n  - ".join(problems))
        return 2
    print(f"score={result['total_score']} threshold={result['pass_threshold']} decision={result['decision'].upper()}")
    for r in result["hard_fail_reasons"]:
        print(f"  hard fail: {r}")
    if "--write" in sys.argv:
        report.update({k: result[k] for k in ("total_score", "decision", "hard_fail_reasons")})
        report.setdefault("decided_by", "skill")
        write_json(path, report)
    return 0 if result["decision"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
