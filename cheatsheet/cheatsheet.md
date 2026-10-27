# Posit Assistant cheat sheet (SpaDES / LandR)

*Draft. Commands are limited to ones documented in this repo; check `/` in the assistant for the full current list.*

## Useful commands

| Command | Use it to |
|---|---|
| `/plugin` OR `/marketplace` | Add a marketplace (e.g. `PredictiveEcology/AI`), install, update or remove plugins (see `guidelines/03-skills.md`). |
| `/plan` | Enter plan mode: explore and write a plan for approval before any change. |
| `/compact` | Condense a long conversation to save tokens. |
| `/savememory` | Checkpoint what was learned into `AGENTS.md` so a new conversation can start fresh. |
| `/create-skill` | Get guided help writing a new skill (only if no team skill covers the need). |
| `/skill-name` | Load a named skill manually, e.g. `/testing`. |

Habits that save tokens: ask narrow questions, start a fresh conversation for an
unrelated task, and run `/compact` then `/savememory` when a session gets long.

## When a guardrail blocks something

| Situation | What you will see | Why | What to do |
|---|---|---|---|
| A command matches a `deny` rule (`rm -rf`, force-push, `git reset --hard`, `git add -A`) | The call is refused with no prompt | Destructive or blanket actions are blocked on purpose | Ask for the safer, narrower equivalent (list first, name specific paths), or do it yourself outside the assistant if it is truly needed |
| A command or edit matches an `ask` rule (`git commit`, edits) | A permission prompt | Higher-risk actions need your confirmation | Read what is being asked, then approve once, approve for the session, or decline |
| A hook asks or denies (a path outside the project, an un-dry-run destructive command, a commit) | A message from the hook explaining the rule | The always-on guardrails in `AGENTS-rules/enforced/default/` | Confirm if it is what you meant. If the rule is wrong for your case, change the rule rather than working around it |
| The assistant will not touch a path | A refusal citing a permission boundary | Outside the project folder is read-only unless you grant it | Grant access for that specific path only if appropriate; re-grant is needed each time |
| Edits to `.R` files go through the shell | The assistant uses `bash` or Python instead of the editor tool | Format-on-save can reformat whole files | Nothing to do; check `git diff` afterwards |
| A hook note says `AGENTS.md` is long | A short size notice at session start | `AGENTS.md` is read every conversation, so size costs tokens | Ask the assistant to propose moving detail into a skill or reference file |

Hooks fail open: if one errors, the action proceeds, so do not treat them as locks.
Guardrail and hook changes apply only in a **new conversation**.

## Where to look next

- Setup: `guidelines/00a-quickstart.md`
- Mechanisms and where each guardrail lives: `guidelines/02-guardrails.md`
- The rules themselves: `AGENTS-rules/README.md` and `AGENTS-rules/enforced/README.md`
- Skills and plugins: `guidelines/03-skills.md`

Drafted with assistance from Claude (Posit Assistant).
