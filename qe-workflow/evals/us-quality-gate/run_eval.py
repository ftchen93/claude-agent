#!/usr/bin/env python3
"""Compare us-quality-gate results with expected outcomes.

Usage: run_eval.py <out-dir>      (produced by run_skill.sh)
For each case it checks, across all runs:
  - decision matches expected        (accuracy)
  - total_score inside score_range   (calibration)
  - same decision on every run, score spread <= 10 points   (consistency)
  - expected hard-fail criteria fired, expected N/A criteria scored null
Exit 0 if every check passes, 1 otherwise.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_SPREAD = 10


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    out = Path(sys.argv[1])
    all_ok = True
    rows = []
    for case in sorted((HERE / "cases").iterdir()):
        exp = json.loads((case / "expected.json").read_text())
        reports = sorted((out / case.name).glob("run-*/qe-artifacts/**/01-quality-report.json"))
        if not reports:
            rows.append((case.name, "NO RESULTS", ""))
            all_ok = False
            continue
        data = [json.loads(r.read_text()) for r in reports]
        problems = []
        decisions = [d.get("decision") for d in data]
        scores = [d.get("total_score") for d in data]
        if any(s is None for s in scores):
            problems.append("score_gate.py was not run in some runs")
            scores = [s for s in scores if s is not None]
        wrong = sum(1 for d in decisions if d != exp["decision"])
        if wrong:
            problems.append(f"decision wrong in {wrong}/{len(data)} runs (expected {exp['decision']})")
        lo, hi = exp["score_range"]
        outside = [s for s in scores if not lo <= s <= hi]
        if outside:
            problems.append(f"scores {outside} outside [{lo}, {hi}]")
        if len(set(decisions)) > 1:
            problems.append(f"inconsistent decisions {decisions}")
        if scores and max(scores) - min(scores) > MAX_SPREAD:
            problems.append(f"score spread {max(scores) - min(scores):.1f} > {MAX_SPREAD}")
        for d in data:
            reasons = " ".join(d.get("hard_fail_reasons", []))
            for crit in exp.get("expected_hard_fail", []):
                if crit not in reasons:
                    problems.append(f"expected hard fail on {crit} not raised")
            by_id = {c["id"]: c for c in d.get("criteria", [])}
            for crit in exp.get("expected_na", []):
                if by_id.get(crit, {}).get("score", 0) is not None:
                    problems.append(f"{crit} should be N/A (null)")
        problems = list(dict.fromkeys(problems))
        status = "PASS" if not problems else "FAIL"
        all_ok &= not problems
        rows.append((case.name, f"{status}  runs={len(data)} scores={scores}", "; ".join(problems)))

    for name, status, detail in rows:
        print(f"{name:<30} {status}")
        if detail:
            print(f"{'':<30}   {detail}")
    print("\nOVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
