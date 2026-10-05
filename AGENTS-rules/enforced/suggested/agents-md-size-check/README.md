# agents-md-size-check

> A note at the start of a session when the assistant's project notes file (`AGENTS.md`) has grown long. The assistant re-reads that file every time, so a long one uses up your token budget.

**Optional.** A SessionStart hook that measures the project's `AGENTS.md` and, only if
it is longer than a threshold (default 200 lines, set with `AGENTS_MD_MAX_LINES`),
injects a short note with its line count and approximate token count. It prints nothing
when the file is within the limit, and it never edits anything.

**Why:** `AGENTS.md` is loaded in full at the start of every conversation, so every
extra line is a token cost paid on every turn of every session. Status logs, catalogues
and long how-tos tend to accumulate there; on-demand skills cost nothing until needed.
A hook can measure file size cheaply and reliably, which prose rules cannot.

**Why optional, not default:** the threshold is a judgement call, and a project that
legitimately needs a long memory file would get a notice every session. It is only a
nudge: the note tells the assistant to *suggest* moving content, not to do it.

**Install:**

1. Copy `agents-md-size-check.sh` to a hooks folder (`~/.posit/assistant/hooks/` for
   user-wide, or `<project>/.posit/assistant/hooks/`) and `chmod +x` it.
2. Add to the matching `settings.json` (merge; hooks from global and project are
   additive):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "~/.posit/assistant/hooks/agents-md-size-check.sh" }
        ]
      }
    ]
  }
}
```

3. Takes effect in a **new conversation**. Hooks fail open: if the script errors, the
   session proceeds without the note.

Drafted with assistance from Claude (Posit Assistant).
