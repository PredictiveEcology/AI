# generated-files-guard

**Optional.** A PreToolUse hook that asks or denies before hand-editing files that
should only be produced by tooling — `NAMESPACE` and `man/*.Rd` (roxygen2-generated) in
LandR/SpaDES packages.

**Why:** a hand edit to a generated file gets silently overwritten (or drifts from the
source it's generated from) the next time `devtools::document()` runs, and the
resulting confusion is hard to diagnose after the fact.

**Why optional, not default:** teams whose workflow always runs `document()` before
committing may not need the extra prompt; some contributors intentionally hand-patch a
generated file temporarily while debugging a roxygen issue.

## Install

1. Copy `generated-files-guard.py` to a hooks folder (`~/.posit/assistant/hooks/` for user-wide, or
   `<project>/.posit/assistant/hooks/`) and `chmod +x` it.
2. Merge into the matching `settings.json` (global and project hooks are additive):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "edit|write",
        "hooks": [
          { "type": "command", "command": "~/.posit/assistant/hooks/generated-files-guard.py" }
        ]
      }
    ]
  }
}
```

3. Takes effect in a **new conversation**. Hooks fail open: if the script errors, the
   action proceeds.

Tested with sample inputs only, not yet in a live session.

Drafted with assistance from Claude (Posit Assistant).
