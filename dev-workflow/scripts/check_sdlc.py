#!/usr/bin/env python3
"""Deterministic checks on SDLC artifacts (intent.md, spec.md, plan.md).

Usage:
  check_sdlc.py intent <intent.md>
  check_sdlc.py spec   <spec.md> [--intent <intent.md>]
  check_sdlc.py plan   <plan.md> --test-cases <03-test-cases.json> [--spec <spec.md>]

intent: required sections present and filled; at least one AC-n.
spec:   required sections present; "Areas of concern" filled in; AC IDs carried forward
        from the intent (none silently dropped or renumbered).
plan:   required sections present; Proof gives a command; every cited TC exists; every
        P1 scripted TC is cited; every active AC in the spec is covered by a cited TC.
Exit 0 = OK, 1 = problems found, 2 = bad usage or unreadable input. Standard library only.
"""
import json
import re
import sys

AC_LINE = re.compile(r"^\s*[-*]\s*\**(AC-\d+)\**((?:\s*\([^)]*\))?)\s*[:.)-]\s*(.*)$")
TC_REF = re.compile(r"\bTC-\d{3,}\b")
REQUIRED = {
    "intent": ["Problem", "Proposed outcome", "Acceptance criteria", "Affected users and systems",
               "Constraints", "Out of scope", "Open questions"],
    "spec": ["Summary", "Acceptance criteria", "Functional requirements", "Design",
             "Non-functional requirements", "Policy compliance", "Areas of concern", "Open questions"],
    "plan": ["Files that change", "Order of work", "Risks", "Proof"],
}
PLACEHOLDER = re.compile(r"<[^>]+>")


def sections(text):
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            current = m.group(1)
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def find_section(secs, name):
    for k, v in secs.items():
        if k.lower().startswith(name.lower()):
            return v
    return None


def meaningful(body):
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    body = PLACEHOLDER.sub("", body)
    return bool(re.search(r"[A-Za-z0-9]", body.replace("...", "")))


def acs(text):
    found = {}
    for line in text.splitlines():
        m = AC_LINE.match(line)
        if m:
            found[m.group(1)] = "withdrawn" in (m.group(2) + " " + m.group(3)).lower()
    return found


def check_sections(kind, text):
    problems = []
    secs = sections(text)
    for name in REQUIRED[kind]:
        body = find_section(secs, name)
        if body is None:
            problems.append(f"missing section '## {name}'")
        elif not meaningful(body):
            problems.append(f"section '## {name}' is empty or still a placeholder")
    return problems, secs


def cmd_intent(path):
    text = open(path, encoding="utf-8").read()
    problems, _ = check_sections("intent", text)
    if not acs(text):
        problems.append("no acceptance criteria found (expected lines like '- AC-1: Given ...')")
    return problems


def cmd_spec(path, intent_path=None):
    text = open(path, encoding="utf-8").read()
    problems, _ = check_sections("spec", text)
    spec_acs = acs(text)
    if not spec_acs:
        problems.append("no acceptance criteria found in spec")
    if intent_path:
        intent_acs = acs(open(intent_path, encoding="utf-8").read())
        for ac in intent_acs:
            if ac not in spec_acs:
                problems.append(f"{ac} from intent.md is missing in spec.md "
                                "(carry it forward, or mark it '(withdrawn)' with a reason)")
    return problems


def cmd_plan(path, tc_path, spec_path=None):
    text = open(path, encoding="utf-8").read()
    problems, secs = check_sections("plan", text)
    proof = find_section(secs, "Proof") or ""
    if not re.search(r"[Cc]ommand:\s*`[^`<]+`", proof):
        problems.append("Proof has no runnable command (expected: - Command: `<test command>`)")
    cited = set(TC_REF.findall(proof))
    data = json.load(open(tc_path, encoding="utf-8"))
    cases = {tc["id"]: tc for tc in data.get("test_cases", [])}
    for tc in sorted(cited - set(cases)):
        problems.append(f"Proof cites {tc}, which is not in {tc_path}")
    for tc_id, tc in sorted(cases.items()):
        if tc.get("priority") == "P1" and tc.get("type") != "exploratory_charter" and tc_id not in cited:
            problems.append(f"P1 test case {tc_id} ('{tc.get('title', '')}') is not cited in Proof")
    if spec_path:
        active = [a for a, withdrawn in acs(open(spec_path, encoding="utf-8").read()).items() if not withdrawn]
        covered = {ac for tc_id in cited if tc_id in cases for ac in cases[tc_id].get("covers", [])}
        for ac in active:
            if ac not in covered:
                problems.append(f"{ac} is not covered by any test case cited in Proof")
    return problems


def main(argv):
    if len(argv) < 2 or argv[0] not in ("intent", "spec", "plan"):
        print(__doc__)
        return 2
    kind, path = argv[0], argv[1]
    opts = dict(zip(argv[2::2], argv[3::2]))
    try:
        if kind == "intent":
            problems = cmd_intent(path)
        elif kind == "spec":
            problems = cmd_spec(path, opts.get("--intent"))
        else:
            if "--test-cases" not in opts:
                print("plan needs --test-cases <03-test-cases.json>")
                return 2
            problems = cmd_plan(path, opts["--test-cases"], opts.get("--spec"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read input: {e}")
        return 2
    if problems:
        print(f"{kind.upper()} CHECK FAILED ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"{kind.upper()} CHECK OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
