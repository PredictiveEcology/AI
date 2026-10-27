#!/usr/bin/env python3
# Reference PreToolUse hook (see AGENTS-rules/enforced/README.md). Install at
# ~/.posit/assistant/hooks/pretool-guardrails.py (or a project-local hooks path) and
# reference it from settings.json's hooks.PreToolUse (see hooks.settings.json here).
#
# For bash/read/edit. Forces a confirmation ("ask") when:
#   * a file path targeted by read/edit is OUTSIDE the project directory, or
#   * a bash command looks like it touches a path outside the project, or
#   * a bash command is a git commit.
# It also blocks (deny) obvious un-dry-run destructive commands as a backstop to
# the permission rules.
#
# Output contract (PreToolUse): print JSON on stdout with hookSpecificOutput.
#   permissionDecision: "allow" | "ask" | "deny"
# Note: this hook can only DOWNGRADE to ask/deny; it never auto-allows a write.
# Reminder: hooks fail OPEN — if this script errors, the action proceeds.

import json
import os
import re
import sys


def emit(decision, reason=""):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Malformed payload: do nothing (fail open).
        sys.exit(0)

    project = payload.get("cwd") or os.environ.get("PA_PROJECT_DIR") or ""
    project = os.path.realpath(project) if project else ""
    tool = payload.get("tool_name", "")
    tin = payload.get("tool_input", {}) or {}

    def is_outside(path):
        if not project or not path:
            return False
        try:
            rp = os.path.realpath(os.path.join(project, os.path.expanduser(path)))
        except Exception:
            return False
        return os.path.commonpath([rp, project]) != project

    # --- read / edit: check the target path ---
    if tool in ("read", "edit"):
        path = tin.get("file_path") or tin.get("path") or ""
        if is_outside(path):
            verb = "write to" if tool == "edit" else "read"
            emit("ask", f"Path is outside the project; confirm each time before "
                        f"you {verb} it: {path}")
        sys.exit(0)  # inside project -> normal handling

    # --- bash: inspect the command string ---
    if tool == "bash":
        cmd = (tin.get("command") or "").strip()

        # Backstop deny for un-dry-run destructive commands.
        destructive = [
            r"\brm\s+-[rf]", r"\bgit\s+clean\b(?!.*\s-n\b)",
            r"\bgit\s+push\s+(--force|-f)\b", r"\bgit\s+reset\s+--hard\b",
        ]
        for pat in destructive:
            if re.search(pat, cmd):
                emit("deny", "Destructive command: run a dry run first "
                             "(e.g. rm -> list, git clean -n, git diff) and confirm.")

        # Git commit always requires confirmation.
        if re.search(r"\bgit\s+commit\b", cmd):
            emit("ask", "Commits require explicit instruction and sign-off. "
                        "Confirm the drafted commit message before committing.")

        # Blanket staging -> confirm and prefer specific paths.
        if re.search(r"\bgit\s+add\s+(-A\b|--all\b|\.(\s|$))", cmd):
            emit("ask", "Avoid blanket staging; stage specific paths instead.")

        # Heuristic: command references an absolute path or ~ outside the project.
        for token in re.findall(r"(?:~|/)[^\s'\"]+", cmd):
            if is_outside(token):
                emit("ask", f"Command references a path outside the project; "
                            f"confirm access each time: {token}")

        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
