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

**Sketch:** SessionStart hook that, for each repo under the workspace root, prints
`<repo>: branch <b> (origin=<url>, upstream=<url or none>, N ahead / M behind upstream)`.
Adapted from FOR-CAST's `session-context.sh`, credited as the source pattern.
