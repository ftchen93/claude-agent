#!/usr/bin/env python3
"""Compute feasibility scores and a default recommendation per test case.

Usage: score_feasibility.py <feasibility.json> [--write]
score = repeatability*0.30 + stability*0.20 + technical_feasibility*0.20
        + business_risk*0.20 + (6 - effort)*0.10        (range 1-5)
Default recommendation: >= 3.5 automate, 2.5-3.49 defer, < 2.5 manual.
The model may override the default only with a rationale starting "OVERRIDE:".
Exit 0 if all rows are consistent, 1 if a row differs from the default without an
OVERRIDE rationale, 2 on invalid input.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared" / "scripts"))
from qe_common import load_json, plugin_file, validate, write_json  # noqa: E402

WEIGHTS = {"repeatability": 0.30, "stability": 0.20, "technical_feasibility": 0.20, "business_risk": 0.20}


def default_recommendation(score):
    if score >= 3.5:
        return "automate"
    if score >= 2.5:
        return "defer"
    return "manual"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    path = args[0]
    data = load_json(path)
    errors = validate(data, load_json(plugin_file("shared/schemas/feasibility.schema.json")))
    if errors:
        print("INVALID INPUT:\n  - " + "\n  - ".join(errors))
        return 2
    flagged = 0
    print(f"{'TC':<10}{'score':>6}  {'default':<10}{'chosen':<12}")
    for a in data["assessments"]:
        f = a["factors"]
        s = sum(f[k] * w for k, w in WEIGHTS.items()) + (6 - f["effort"]) * 0.10
        a["feasibility_score"] = round(s, 2)
        default = default_recommendation(s)
        flag = ""
        if a["recommendation"] != default and not a["rationale"].startswith("OVERRIDE:"):
            flag = "  <- differs from default without OVERRIDE rationale"
            flagged += 1
        print(f"{a['tc_id']:<10}{s:>6.2f}  {default:<10}{a['recommendation']:<12}{flag}")
    if "--write" in sys.argv:
        write_json(path, data)
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
