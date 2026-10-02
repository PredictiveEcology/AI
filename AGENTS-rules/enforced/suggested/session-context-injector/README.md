# session-context-injector

**Optional.** A SessionStart hook that prints a short summary of *environment facts* —
current repo, branch, whether it's a fork, ahead/behind status against upstream — rather
than *behavioral rules* (which `default/hooks/session-guardrails.sh` already covers).

**Why:** this workspace collects many repos side by side, mixing forks (`origin` =
personal fork, `upstream` = `PredictiveEcology`) and direct clones, with mixed default
branches (`main` vs `master`). A quick per-session summary reduces the chance of
branching off the wrong base or assuming a branch name that isn't this repo's default.

**Why optional, not default:** it's specific to multi-repo, fork-based workspaces like
this one; a single-repo or non-git workflow gains nothing from it, and it adds a small
amount of startup latency (running `git status`/`git remote -v` per repo).

## Install

1. Copy `session-context-injector.sh` to a hooks folder (`~/.posit/assistant/hooks/` for user-wide, or
   `<project>/.posit/assistant/hooks/`) and `chmod +x` it.
2. Merge into the matching `settings.json` (global and project hooks are additive):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "~/.posit/assistant/hooks/session-context-injector.sh" }
        ]
      }
    ]
  }
}
```

3. Takes effect in a **new conversation**. Hooks fail open: if the script errors, the
   action proceeds.

It reads only the git repositories directly under the project folder, never fetches, and shows ahead/behind against the tracked branch as last fetched.

Tested with sample inputs only, not yet in a live session.

Drafted with assistance from Claude (Posit Assistant).
