# Getting, creating, and loading skills

> **Assistant-facing reference** — the assistant should study these and
> then consult to obtain detail to execute the steps in `00-user-setup.md`.

Skills are specialized knowledge modules that Posit Assistant loads **on demand** when
a task matches the skill's `description`. This guide covers how to get the shared team
skills (the first option), how to create a new one only when needed, where skills live
(remote and local), and how loading and precedence work.

> **Shared skills location.** The shared skills live in the SpaDES.ai repo
> (https://github.com/CeresBarros/SpaDES.ai, in `skills/`) so everyone works from the same
> set. Clone or sync the repo into a local skills path (see "Loading / using skills"
> below).

## Existing team skills (current set)

Get these before writing new ones; they are the starting point for SpaDES toolkit work:

| Skill | Purpose |
|---|---|
| `spades-overview` | Toolkit map + `simList` mental model; routes to the others. Has `references/`. |
| `spades-module-anatomy` | Structure/editing of a SpaDES module's `.R`, metadata, events. |
| `spades-module-development` | General dev workflow: `newModule()`, coding against the toolkit, running/debugging a `simList`. |
| `spades-package-development` | Developing the SpaDES packages themselves (APIs, NAMESPACE, devtools, versioning). |
| `spades-testing` | Unit and integration tests for modules and functions. |
| `spades-code-documentation` | Comments, module metadata `desc` fields, roxygen2, NEWS. |
| `spades-module-manuals` | Per-module `.Rmd` manuals *(placeholder)*. |

## About skills

### Where skills live: remote and local

Skills can come from a **remote** source (the team skills repo) or exist **locally** on a
given machine. The shared team skills are published remotely and then synced or cloned into
a local skill path.

Posit Assistant discovers **local** skills from `skills.paths`, which defaults to (in
order):

```
~/.agents/skills
~/.posit/assistant/skills
.agents/skills
.posit/assistant/skills
```

- **`~/.agents/skills`** and **`.agents/skills`** — the shared Agent-Skills-spec
  location other tools also read; use for skills shared across tools, or as the sync
  target for skills cloned from a remote team repo.
- **`~/.posit/assistant/skills`** (user) and **`.posit/assistant/skills`** (project) —
  Posit-Assistant-specific skills.

Precedence: **project skills override user skills; both override built-in skills** of
the same name. When the same name exists in both `.posit/assistant/skills` and
`.agents/skills` at the same level, the `.posit/assistant/skills` version wins. Project
skills require a **trusted workspace**.

Choose the location by intent:
- Personal, cross-project → `~/.posit/assistant/skills/`.
- Shared with the team, committed to a repo → project `.posit/assistant/skills/` (or
  a shared `~/.agents/skills` synced from the team repo).

### Anatomy of a skill

```
skill-name/
├── SKILL.md          # required: YAML frontmatter + instructions
├── references/       # optional: longer material loaded on demand
├── scripts/          # optional: executable helpers
└── assets/           # optional: templates, data
```

`SKILL.md` frontmatter requires:
- `name` — lowercase letters/digits/hyphens, no leading/trailing or double hyphens,
  **must match the directory name**, max 64 chars.
- `description` — what it does *and when to use it*, keyword-rich, max 1024 chars.

Keep the body under ~500 lines; move detail into `references/` for progressive
disclosure. Use the `/create-skill` command for interactive guidance, or copy an
existing skill as a template.

## Creating a new skill

1. **Check the shared skills first** (see above). Create a new skill only when the task
   is not already covered by an existing team skill.
2. Pick a clear, unique `name` and matching directory.
3. Write a keyword-rich `description` so it activates on the right tasks.
4. Ground the body in **real file paths and short excerpts** from the packages under
   focus.
5. Offload long catalogs (function lists, package listings) to `references/`.
6. Validate: name matches directory, allowed characters, description ≤ 1024 chars.

## Loading / using skills

**Get the shared team skills first.** They are the primary source; new skills are
created only when a need is not already covered.

1. **Get shared skills.** Clone or sync the SpaDES.ai repo
   (`git@github.com:CeresBarros/SpaDES.ai.git`, `skills/`) into a local skills path
   (e.g. `~/.agents/skills` or a synced folder). Point `skills.paths` at that folder if
   it is not already a default location. Remember: a **project** `skills.paths`
   **replaces** (does not merge with) the global value — repeat the defaults when adding
   a custom path in project config. Pull updates periodically to stay current. The
   assistant can run this clone/sync when given permission to use `git` and write to the
   skills path; the user decides the target path and confirms discovery.
2. **Automatic loading:** the model loads a skill when a task matches its `description`.
3. **Manual loading:** invoke as a slash command `/skill-name` (unless hidden with
   `user-invocable: false`, or shadowed by a built-in command of the same name).
