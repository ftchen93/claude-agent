#!/usr/bin/env python3
"""Guardrail: reject a self-heal diff that touches assertions or product code.

Usage: check_heal_diff.py [<git-diff-range>]     (default: staged changes)
  e.g. check_heal_diff.py            -> git diff --cached
       check_heal_diff.py main...HEAD
Fails (exit 1) if any added or removed line looks like an assertion, if a fixed sleep
is added, if a file outside the test paths changes, or if too many files change.
Edit TEST_PATH_PATTERNS and ASSERTION_PATTERNS for your stack.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared" / "scripts"))
from qe_common import gates_config  # noqa: E402

TEST_PATH_PATTERNS = [r"(^|/)tests?/", r"(^|/)e2e/", r"(^|/)__tests__/", r"\.spec\.", r"\.test\.",
                      r"(^|/)test_[^/]+\.py$", r"(^|/)pages?/", r"(^|/)page-objects?/", r"(^|/)fixtures?/"]
ASSERTION_PATTERNS = [r"\bexpect\s*\(", r"\bassert\w*\b", r"\.should\s*\(", r"\bto(Be|Equal|Have|Contain|Match)\w*\s*\(",
                      r"\bassertThat\s*\(", r"\bAssert\.", r"\bverify\w*\s*\("]
SLEEP_PATTERNS = [r"\bsleep\s*\(", r"\bwaitForTimeout\s*\(", r"Thread\.sleep", r"time\.sleep", r"cy\.wait\(\s*\d+"]


def main():
    rng = sys.argv[1] if len(sys.argv) > 1 else None
    cmd = ["git", "diff", "--unified=0"] + ([rng] if rng else ["--cached"])
    diff = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    max_files = gates_config()["self_heal"]["max_files_changed"]

    violations, files, current = [], set(), None
    for line in diff.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            name = line[4:].strip()
            if name != "/dev/null":
                current = name[2:] if name[:2] in ("a/", "b/") else name
                files.add(current)
            continue
        if not line or line[0] not in "+-" or line.startswith(("+++", "---")):
            continue
        body = line[1:]
        if any(re.search(p, body) for p in ASSERTION_PATTERNS):
            violations.append(f"{current}: assertion line changed: {body.strip()[:100]}")
        if line[0] == "+" and any(re.search(p, body) for p in SLEEP_PATTERNS):
            violations.append(f"{current}: fixed sleep added: {body.strip()[:100]}")

    for f in sorted(files):
        if not any(re.search(p, f) for p in TEST_PATH_PATTERNS):
            violations.append(f"{f}: not a test file; self-heal must not change product code")
    if len(files) > max_files:
        violations.append(f"{len(files)} files changed, limit is {max_files}")
    if not files:
        print("No changes found in diff.")
        return 1

    if violations:
        print("SELF-HEAL REJECTED:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(f"SELF-HEAL DIFF OK ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
