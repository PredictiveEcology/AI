# AGENTS-rules/enforced

A second kind of unit in this library. The prose rules one level up
(`root-causes-not-patches.md` and its siblings) are *advisory* — the assistant reads
them and is expected to comply, but nothing stops it acting otherwise. The files here
are *enforced* — Posit Assistant's `permission` rules and `hooks` mechanisms, which the
app applies at the moment of an action (`permission`) or as a strong, fail-open nudge
(`hooks`). See `guidelines/02-guardrails.md` for the full mechanism reference.

Where a prose rule is pasted into `AGENTS.md` or injected by a hook, an `enforced/` file
is **copied into `settings.json`** (global `~/.posit/assistant/settings.json` for
user-wide reach, or project `.posit/assistant/settings.json` for one workspace) or
placed in a hooks directory and referenced from there. Always show the user the exact
diff to `settings.json` and get sign-off before writing — these are config changes, not
text a user can simply choose to ignore, and `default/` here means "recommended
content", not "apply without asking."

## `default/`

The reference guardrail set already described in `guidelines/02-guardrails.md` and
installed on the team's machines:

- `default/permissions.settings.json` — the `permission` block: deny destructive bash
  (`rm -rf`/`-r`/`-f`, `git clean`, force-push, `git reset --hard`) and blanket staging
  (`git add -A`/`.`/`--all`); `ask` for `git commit`; `allow` for read-only git
  (`status`/`diff`/`log`/`show`) and `pwd`; `edit = ask`, `read = allow`.
- `default/hooks/session-guardrails.sh` — SessionStart hook: injects the behavioral
  rules (outside-project read-only + re-ask, verify working directory, dry-run
  destructive commands, specific staging, draft + sign off commits, succinctness,
  respect existing style, ecologist-friendly docs, authorship footer, session-length
  prompts).
- `default/hooks/pretool-guardrails.py` — PreToolUse hook: forces `ask` for
  outside-project `read`/`edit`/`bash` paths (every time, since permission grants
  persist but this must not) and for `git commit`; denies un-dry-run destructive
  commands as a backstop to the permission rules.
- `default/hooks.settings.json` — the `hooks` block wiring the two scripts in (uses
  `~`-relative paths; adjust to the actual install location).

## `suggested/`

Optional guard scripts, each independent — take any subset. Adapted (not copied
verbatim) from FOR-CAST's `ai_workflows` `r-project-core` plugin
(https://github.com/FOR-CAST/ai_workflows), credited as the source of the pattern.
Each subfolder has its own short README explaining what it blocks/warns and why it's
optional rather than default.

| Rule | What it does |
|---|---|
| `edit-r-via-shell-only` | PreToolUse deny/redirect: editor `edit`/`write` tools against `*.R` files are blocked; `.R` files must be changed via `bash`/Python (format-on-save can silently reformat otherwise). |
| `generated-files-guard` | PreToolUse ask/deny on hand-editing roxygen2-generated files (`NAMESPACE`, `man/*.Rd`) in LandR/SpaDES packages. |
| `long-run-interlock` | Warn/block starting a new `spades()`/simulation run, or mutating a module's library, while another long run may still be in progress on a shared machine. |
| `module-version-bump-reminder` | On a `git commit` that touches a module's `defineModule()` `version` field, remind the assistant to check sibling-module compatibility first (see `landr-package-maintenance`'s version-alignment guidance). |
| `session-context-injector` | SessionStart hook that summarizes repo/branch/fork state (not behavioral rules) — environment facts, complementing rather than duplicating `default/hooks/session-guardrails.sh`. |
| `agents-md-size-check` | SessionStart hook that notes when the project `AGENTS.md` exceeds a line threshold (default 200), since it is loaded in full every conversation. Silent otherwise. |
| `agents-md-token-efficiency` | Paste-ready prose block for `AGENTS.md` (targeted reads, subagent delegation, batching, lean memory). Advisory only; companion to the size check. |

## Adding an enforced rule

1. Classify: hard block/gate → `permission`; needs to inspect inputs or force
   per-action re-approval → hook. See `guidelines/02-guardrails.md`'s "Implementing new
   guardrails" section.
2. Draft the exact snippet and its destination file (global vs. project
   `settings.json`, global vs. project-local hooks path).
3. Show the user the drafted content and destination; get sign-off.
4. On approval, merge into `settings.json` without overwriting unrelated keys; back it
   up first. Remember: hooks are additive (global then project) and changes take effect
   in a **new conversation**, not the current one.
