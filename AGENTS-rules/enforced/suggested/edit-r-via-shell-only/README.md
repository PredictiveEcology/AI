# edit-r-via-shell-only

**Optional.** A PreToolUse hook that denies the editor's `edit`/`write` tools against
`*.R` files, forcing changes through `bash` (heredoc) or a Python one-liner instead.

**Why:** some editor configurations trigger format-on-save (Air-style) reformatting even
when nominally disabled, turning a one-line change into a large, unwanted diff. This is
already stated as a *behavioral* rule in the LandR/SpaDES `AGENTS.md` template; this
hook makes it mechanical instead of relying on the assistant to remember.

**Why optional, not default:** it only matters on machines/editors that actually
reformat on save. If yours doesn't, the behavioral rule alone is enough, and the hook
just adds friction to ordinary `edit` calls on `.R` files.

## Install

1. Copy `edit-r-via-shell-only.py` to a hooks folder (`~/.posit/assistant/hooks/` for user-wide, or
   `<project>/.posit/assistant/hooks/`) and `chmod +x` it.
2. Merge into the matching `settings.json` (global and project hooks are additive):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "edit|write",
        "hooks": [
          { "type": "command", "command": "~/.posit/assistant/hooks/edit-r-via-shell-only.py" }
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
