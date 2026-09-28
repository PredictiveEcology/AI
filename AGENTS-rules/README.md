# AGENTS-rules

Short, single-topic behavioural rules for an AI assistant, published one per file so
you can take the ones you agree with and leave the rest.

`AGENTS.md` is per-project and is always part team convention, part personal working
style. There is no one file that suits everybody, so this folder makes the unit of
sharing a **rule** rather than a file. Nobody adopts someone else's `AGENTS.md`; they
adopt `root-causes-not-patches` because they read it and agreed.

## Using them

Three ways, from crudest to cleanest. All three work; pick by what your tool supports.

1. **Paste.** Copy the rules you want into your project `AGENTS.md`. Works everywhere.
   Each rule is a few lines, so the file stays readable.
2. **Inject.** Have a SessionStart hook concatenate a chosen subset. This is the
   always-on, user-wide path described in `guidelines/02-guardrails.md`, and one edit
   then changes every project.
3. **Import**, where the tool supports including a file from a memory file. Claude Code
   does, with `@~/.agents/rules/root-causes-not-patches.md` in `CLAUDE.md`; whether
   Posit Assistant's `AGENTS.md` supports an equivalent has not been confirmed, so
   check before relying on it.

## Where a rule belongs, versus a guideline or a skill

Four mechanisms carry instructions to an assistant. They differ by **who reads it** and
**when**.

| | Read by | When | Example |
|---|---|---|---|
| `guidelines/` | You | Once, when setting up or when you want advice on working with the assistant | "Explore, then plan, then code" |
| `AGENTS.md` + these rules | The assistant | Every conversation, unconditionally | "Fix the defect where it lives" |
| `skills/` | The assistant | Only when the task matches the skill's `description` | "How to reproduce a failing module CI job" |
| `settings.json` permissions and hooks | The app | At the moment of an action; enforced, not advisory | deny `rm -rf` |

Guidelines are about the setup and about working with the assistant. Rules and skills
are about the work itself. `guidelines/02-guardrails.md` covers the fourth column.

**Rule or skill?** Two tests, and they agree in almost every case.

- **Can you name the trigger?** "When writing a PR", "when a module's CI is red" — that
  is a skill. If it has to hold on every turn, it is a rule.
- **What happens if the assistant does not think to look it up?** A skill loads when its
  description matches the task; if the match fails, nothing is lost but a lookup. A rule
  has to be in force on the turn where the assistant is about to do the wrong thing, and
  it is precisely then that it will not occur to anyone to go and read it.

A rule is three to six lines. If yours needs two hundred, it is a skill with a rule on
the front — write both and have the rule point at the skill. `session-log.md` here is
that shape.

## Adding a rule

- One rule per file, named for the behaviour, not the symptom.
- State the rule, then **why** — a rule without its reason gets dropped the first time
  it is inconvenient. Where the reason is a specific incident, name it.
- Keep it short enough to paste without thinking about it.
- Do not add a rule the shared `AGENTS.md` template already carries (it already covers
  not reformatting unasked, verifying the diff after a change, specific staging, and
  the memory-efficient-R conventions). `guidelines/00b-user-guidelines.md` warns that
  an over-specified memory file stops being read, and that warning applies here too.

## The current set

| Rule | In one line |
|---|---|
| `root-causes-not-patches.md` | Fix the defect where it lives, and name it with `file:line` first. |
| `verify-dont-infer.md` | Run the controlled comparison before blaming the environment. |
| `shared-ci-actions.md` | Use the organisation's shared CI actions at the shared ref; never hand-patch a copy. |
| `writing-for-humans.md` | PRs, issues and comments are short and plain, because colleagues pay for length. |
| `session-log.md` | Keep a durable session record from the start, not at the end. |
