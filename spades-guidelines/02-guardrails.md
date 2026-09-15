# Guardrails for AI-assisted work (reference)

> **Assistant-facing reference** — the assistant should study these and
> then consult to obtain detail to execute the steps in `00-user-setup.md`.

Guardrails constrain and guide how a Posit-Assistant-enabled Claude model behaves.
Different needs call for different mechanisms; this reference explains the four relevant
files/systems, where each guardrail belongs, and the order Posit Assistant loads them.
For the short action checklist, see `00-user-setup.md`.

> **Shared AGENTS.md template.** A template `AGENTS.md` lives in the SpaDES.ai repo
> (https://github.com/CeresBarros/SpaDES.ai, at `AGENTS.md`). Usage: copy it into the
> project root as `AGENTS.md`, then adapt paths and the repository set to the workspace.

## The four mechanisms

| Mechanism | Scope | Nature | Best for |
|---|---|---|---|
| **`AGENTS.md`** (memory) | Project root, trusted workspace only | Prose context the model reads every conversation | Project conventions, toolkit map, coding standards |
| **Skills** | User or project `skills` paths | On-demand knowledge, loaded when task matches | Domain how-to (module anatomy, testing, docs) |
| **`settings.json` `permission`** | Global or project | Hard allow/ask/deny rules the app enforces | Blocking/gating specific tools or commands |
| **`settings.json` `hooks`** | Global or project | Shell scripts run at lifecycle events | Programmable gating + injecting always-on rules |

Key distinctions:
- **AGENTS.md is not user-wide** — it loads only from a project root, only in trusted
  workspaces. There is no global memory file.
- **Skills are on-demand, not always-on** — they cannot enforce guardrails; they only
  activate when their `description` matches.
- **Permission rules are enforced** — `deny` holds even in auto/YOLO modes; grants can
  persist per project/session.
- **Hooks are programmable but fail-open** — if a hook errors or times out, the action
  proceeds. A hook is a strong nudge, not an ironclad lock. Global hooks run for every
  project (even untrusted); project hooks need a trusted workspace. Global and project
  hooks are additive (global first).

## Where each kind of guardrail belongs

| Guardrail nature | Put it in |
|---|---|
| "Behave this way" prose (succinctness, style, ecologist-friendly docs, authorship footer, commit sign-off, session-length prompts) | **SessionStart hook** (for always-on user-wide reach) and/or **AGENTS.md** (per project) |
| Hard block of a dangerous command (`rm -rf`, force-push, blanket `git add`) | **`permission` deny** rules |
| Force confirmation on a class of actions (`git commit`, outside-project file access) | **`permission` ask** rules and/or a **PreToolUse hook** |
| Per-action re-approval (re-ask every time, no persistent grant) | **PreToolUse hook** forcing `ask` (permission grants persist, so a hook is required) |
| Domain how-to that should load only when relevant | **Skill** |

## Loading / resolution hierarchy

**Memory & skills**
- `AGENTS.md` loads at conversation start in trusted workspaces.
- Skills resolve by `skills.paths` order; project overrides user overrides built-in.

**Permissions** (highest priority first):
1. Conversation-scoped approvals ("allow for conversation")
2. Project-scoped approvals ("allow for project")
3. Project config `.posit/assistant/settings.json`
4. Global config `~/.posit/assistant/settings.json`
5. Built-in security defaults (e.g. `.env`/`.Renviron` reads blocked; `deny` always
   enforced)
6. Tool default → fallback `ask`

Settings merge order overall: defaults → global → project → environment variables
(last wins), **except hooks are additive** (global then project, never overridden).

## Reference guardrail set (generic)

A recommended starting set of guardrails, described independent of any machine paths.
The two hook scripts are installed in the platform's global hooks directory (under
`~/.posit/assistant/hooks/`) and referenced from the global `settings.json`. This set is
**ecosystem-agnostic** — it serves SpaDES toolkit work unchanged.

- **`permission.bash`** — `deny` for destructive commands (`rm -rf|-r|-f *`,
  `git clean *`, force-push, `git reset --hard`) and blanket staging
  (`git add -A|.|--all`); `ask` for `git commit*`; `allow` for read-only git
  (`status`/`diff`/`log`/`show`) and `pwd`.
- **`permission.edit = ask`**, **`permission.read = allow`**.
- **SessionStart hook** — injects behavioral rules: outside-project = read-only +
  re-ask each time, verify working directory, dry-run destructive commands, specific
  staging, draft + sign off commit messages, be succinct, respect existing style,
  ecologist-friendly low-jargon docs, Claude authorship footer, and session-length
  compact/save prompts.
- **PreToolUse hook** — forces `ask` for outside-project `read`/`edit`/`bash` paths
  (each time) and for `git commit`; denies un-dry-run destructive commands as a
  backstop.

The assistant can **instantiate** this set on the user's behalf (draft the `permission`
rules and hook references, show the diff for sign-off, back up `settings.json`); the
concrete machine paths still belong in a `*.local.md` companion, and the changes take
effect in new conversations.

> For the exact files, values, and install paths used on a specific machine, keep a local,
> machine-specific **instance** of this doc rather than putting them in this shared
> document — see the **"Local instances of these guidelines"** section in
> `00-user-setup.md` for the naming and handling convention (e.g.
> `02a-implemented-reference.local.md`).

## Implementing new guardrails

1. Classify the need: enforceable (permission/hook) vs. behavioral (hook/AGENTS.md)
   vs. domain how-to (skill).
2. For enforceable rules, prefer **`permission`** for simple allow/ask/deny; use a
   **PreToolUse hook** when the decision depends on inspecting inputs or when per-action
   re-approval is needed.
3. For always-on behavioral rules, add them to the **SessionStart hook** (user-wide)
   and mirror project-specific ones in **AGENTS.md**.
4. Draft changes, review them, back up `settings.json`, then merge — do not overwrite
   unrelated keys.
5. Remember hooks **fail open**; do not rely on them as hard locks. Changes take effect
   in **new conversations**, not the current running session.

## Caveats

- Only `bash`/`read`/`edit` are gated by the example PreToolUse hook; `executeCode`
  (R/Python) and `webfetch` are not intercepted.
- No hook fires on token thresholds, so session-length management is a **behavioral**
  prompt, not an enforced action.
- `ask` can never override a `deny` or restricted-mode/workflow-mode restrictions.
