#!/usr/bin/env python3
# Reference PreToolUse hook (see AGENTS-rules/enforced/suggested/module-version-bump-reminder/).
# Matcher: bash. On `git commit`, inspects the STAGED diff; if a .R file adds a `version =`
# line (the field inside a module's defineModule()), asks for confirmation with a reminder
# to check sibling-module compatibility first. Heuristic: it can also match an unrelated
# `version =` line in a .R file, which only costs one extra confirmation.
# Hooks fail open: if this script errors, the action proceeds.

import json
import re
import subprocess
import sys


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") != "bash":
        sys.exit(0)

    cmd = (payload.get("tool_input", {}) or {}).get("command", "")
    if not re.search(r"\bgit\s+commit\b", cmd):
        sys.exit(0)

    cwd = payload.get("cwd") or None
    try:
        diff = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--", "*.R"],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        ).stdout
    except Exception:
        sys.exit(0)

    current, hits = None, []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif re.match(r"^\+\s*version\s*=", line) and current:
            hits.append(current)

    if hits:
        files = ", ".join(sorted(set(hits)))
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "This commit changes a `version =` line (" + files + "). Module "
                    "major/minor versions must match across modules that run together. "
                    "Before committing, check whether sibling modules need a matching "
                    "bump and that the integration tests pass."
                ),
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
