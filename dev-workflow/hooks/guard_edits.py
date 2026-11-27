#!/usr/bin/env python3
"""PreToolUse hook: deterministic edit guard for Claude Code.

Blocks (exit 2, reason shown to Claude):
  1. Any edit to a path matching a glob in <project>/.claude/protected-paths
     (one glob per line, '#' comments), e.g. generated code or a frozen package.
  2. In FIX MODE, any edit to a test file. Fix mode is on when <project>/.claude/fix-mode
     exists or CLAUDE_FIX_MODE=1. Use it while fixing a bug against a committed failing
     test, and while self-healing: the agent must not be able to weaken the check.
  3. Always: an edit to a test file that removes or changes an assertion line, unless
     <project>/.claude/allow-assertion-edits exists (create it deliberately when the spec changed).

Wire it in .claude/settings.json (team) or managed settings (non-negotiable):
  {"hooks": {"PreToolUse": [{"matcher": "Edit|MultiEdit|Write",
     "hooks": [{"type": "command", "command": "python3 /path/to/guard_edits.py"}]}]}}
Plugin agents ignore hooks in their own frontmatter, so this must live in settings.

Limit: it guards Claude's file tools. Shell commands that write files (sed -i, >) are not
seen here; deny those with permission rules, or keep Bash on an allowlist.
"""
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

TEST_PATTERNS = [r"(^|/)tests?/", r"(^|/)e2e/", r"(^|/)__tests__/", r"\.spec\.", r"\.test\.",
                 r"(^|/)test_[^/]+\.py$", r"_test\.(go|py)$", r"Test\.java$"]
ASSERTION = re.compile(r"\bexpect\s*\(|\bassert\w*\b|\.should\s*\(|\bto(Be|Equal|Have|Contain|Match)\w*\s*\(|"
                       r"\bassertThat\s*\(|\bAssert\.|\bverify\w*\s*\(")


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # not our input; don't break the session
    tool = event.get("tool_name", "")
    if tool not in ("Edit", "MultiEdit", "Write"):
        sys.exit(0)
    ti = event.get("tool_input", {}) or {}
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()).resolve()
    target = Path(ti.get("file_path", ""))
    if not target.is_absolute():
        target = project / target
    try:
        rel = target.resolve().relative_to(project).as_posix()
    except ValueError:
        rel = target.as_posix()

    prot = project / ".claude" / "protected-paths"
    if prot.exists():
        for line in prot.read_text(encoding="utf-8").splitlines():
            glob = line.split("#", 1)[0].strip()
            if glob and (fnmatch.fnmatch(rel, glob) or fnmatch.fnmatch(rel, glob.rstrip("/") + "/*")):
                block(f"Blocked: '{rel}' is a protected path ({glob} in .claude/protected-paths). "
                      "Changes here need a change ticket and a person; ask the user.")

    is_test = any(re.search(p, rel) for p in TEST_PATTERNS)
    if not is_test:
        sys.exit(0)

    fix_mode = (project / ".claude" / "fix-mode").exists() or os.environ.get("CLAUDE_FIX_MODE") == "1"
    if fix_mode:
        block(f"Blocked: fix mode is on, so test files can't be edited ('{rel}'). "
              "Make the committed failing test pass by changing product code. If the test itself "
              "is wrong, stop and ask a person.")

    if (project / ".claude" / "allow-assertion-edits").exists():
        sys.exit(0)
    if tool == "Write":
        if target.exists():
            old = target.read_text(encoding="utf-8", errors="replace")
            new = ti.get("content", "")
            removed = [l for l in old.splitlines() if ASSERTION.search(l) and l not in new.splitlines()]
            if removed:
                block(f"Blocked: rewriting '{rel}' would remove or change assertion line(s), e.g. "
                      f"{removed[0].strip()[:80]!r}. Assertions change only when the spec changes; ask a person.")
        sys.exit(0)
    edits = ti.get("edits") if tool == "MultiEdit" else [ti]
    for e in edits or []:
        old_lines = [l for l in (e.get("old_string") or "").splitlines() if ASSERTION.search(l)]
        new_text = e.get("new_string") or ""
        changed = [l for l in old_lines if l not in new_text.splitlines()]
        if changed:
            block(f"Blocked: this edit removes or changes an assertion in '{rel}': "
                  f"{changed[0].strip()[:80]!r}. Assertions change only when the spec changes; ask a person.")
    sys.exit(0)


if __name__ == "__main__":
    main()
