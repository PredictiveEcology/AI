#!/usr/bin/env bash
# Reference SessionStart hook (see AGENTS-rules/enforced/README.md). Install at
# ~/.posit/assistant/hooks/session-guardrails.sh (or a project-local hooks path) and
# reference it from settings.json's hooks.SessionStart (see hooks.settings.json here).
#
# Prints behavioral guardrails to stdout; on SessionStart,
# plain stdout is injected as additional context for the model every session.
# It does not (and cannot) enforce anything — enforcement lives in permission
# rules and the PreToolUse hook. Keep this list short; it is prepended to context.

cat <<'GUARDRAILS'
# Working guardrails (user-wide)

## Filesystem
- The project/workspace folder is the working area. Before accessing files or
  folders OUTSIDE it, ask first. Treat anything outside the project as READ-ONLY
  unless the user grants write access for a specific path, and re-ask each time —
  a prior grant does not carry over to a later action.
- Before running shell commands, verify the current working directory is the
  intended one (e.g. check `pwd`); do not assume.

## Destructive actions
- Always dry-run potentially destructive commands first (e.g. `rm` -> list what
  would be removed; `git clean -n`; show `git diff` before reverting). Present the
  dry-run result and get confirmation before the real action.

## Git
- Do NOT `git commit` unless explicitly instructed. Even when instructed, confirm
  before committing.
- Stage changes as specifically as possible: name individual paths rather than
  `git add -A`/`git add .`.
- DRAFT commit messages and ask the user to sign off before committing.
- Add the Claude authorship footer (see below) to commit messages.

## Writing & code
- Be succinct everywhere: code, prose, comments, commit messages, issue
  descriptions, and documentation. Prefer the shortest clear version.
- Respect the existing coding style, methods, and structure. If a change in
  style/approach seems warranted, justify why and ask before applying it.
- Write documentation for ecologists who are not computer scientists: minimize
  jargon, and define any technical term you must use.

## Authorship footer
- On commit messages, on code/package/module documentation, and on project README
  files, add a brief statement noting Claude (via Posit Assistant) assisted in
  authoring. Keep it to one line, e.g.:
  "Drafted with assistance from Claude (Posit Assistant)."

## Session length
- Watch the conversation length. When it is getting long, proactively suggest the
  user run `/compact` and `/savememory` to condense context and checkpoint
  progress to memory. (You cannot run these yourself — offer the choice.)
GUARDRAILS
