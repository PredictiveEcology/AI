#!/usr/bin/env python3
# Reference PreToolUse hook (see AGENTS-rules/enforced/suggested/edit-r-via-shell-only/).
# Matcher: edit|write. Denies the editor's edit/write tools on *.R files so the change is
# made via bash/Python instead (editor format-on-save can reformat a whole file).
# Hooks fail open: if this script errors, the action proceeds.

import json
import sys


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("edit", "write"):
        sys.exit(0)

    tin = payload.get("tool_input", {}) or {}
    path = tin.get("file_path") or tin.get("path") or ""

    if path.endswith(".R"):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Do not edit .R files with the editor tool (format-on-save can "
                    "reformat the whole file). Make the change via a bash heredoc or "
                    "python3, then check `git diff` shows only the intended change: "
                    + path
                ),
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
