# agents-md-token-efficiency

> A short set of habits you can paste into your notes file so the assistant reads less and replies more briefly, which saves your token budget.

**Optional.** Prose rules to paste into a project `AGENTS.md` so the assistant works in
a token-efficient way. Unlike the other `suggested/` entries this is not a hook or a
`permission` rule: nothing here can be enforced mechanically. Size-aware gating is not
available in `permission`, and a hook cannot know in advance how much a call will return.
So it is advisory text, kept here with the enforced content because it is the companion to
[`agents-md-size-check`](../agents-md-size-check/README.md).

**Why:** token budgets are limited, and most waste comes from a few habits: reading
whole files when a section would do, doing broad exploration in the main conversation,
and letting one conversation run on across unrelated tasks.

**Why optional, not default:** it is a working-style preference, and it adds lines to
`AGENTS.md` itself. Take it only if token use matters to you.

**Use:** paste the block below into `AGENTS.md` (under a conventions heading). Keep it
as is or trim it; each rule stands alone.

```markdown
### Token efficiency

- **Locate, then read.** Search for the relevant lines first, then read only that range
  (`offset`/`limit`). Read a small file whole; do not read a large one whole.
- **Do not raise output limits routinely.** Increase `max_output_bytes` only for a
  specific range that needs it.
- **Delegate broad exploration.** For open-ended "where is X / how does Y work" questions
  across many files, use an `explore` subagent so only its summary enters this
  conversation.
- **Batch independent tool calls** in one response; keep narration between calls to
  one short sentence.
- **Keep replies short.** Do not restate output the user can already see.
- **Keep memory lean.** If `AGENTS.md` grows long, suggest moving rarely-needed detail
  into a skill or reference file. Do not trim it without asking.
- **Suggest a fresh conversation** (or `/compact` and `/savememory`) when the work
  moves to an unrelated task or the conversation has grown long.
```

Drafted with assistance from Claude (Posit Assistant).
