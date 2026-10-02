# module-version-bump-reminder

**Optional.** A PreToolUse hook that, when a `git commit` touches a module's
`defineModule()` `version` field, reminds the assistant to check sibling-module
compatibility before proceeding.

**Why:** LandR module versions carry major/minor alignment expectations across the
modules that interoperate in a simulation (see `landr-package-maintenance`'s
module-version-alignment guidance). Bumping one module's version without checking
whether sibling modules need a matching bump — or without running module integration
tests — can silently break a simulation that combines them.

**Why optional, not default:** only relevant to LandR module repos, not SpaDES toolkit
packages or other PredictiveEcology work; and detecting "this commit touches a version
field" reliably needs a diff inspection this hook has to implement per-repo layout.

## Install

1. Copy `module-version-bump-reminder.py` to a hooks folder (`~/.posit/assistant/hooks/` for user-wide, or
   `<project>/.posit/assistant/hooks/`) and `chmod +x` it.
2. Merge into the matching `settings.json` (global and project hooks are additive):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "bash",
        "hooks": [
          { "type": "command", "command": "~/.posit/assistant/hooks/module-version-bump-reminder.py" }
        ]
      }
    ]
  }
}
```

3. Takes effect in a **new conversation**. Hooks fail open: if the script errors, the
   action proceeds.

**Limit:** it looks for an added line that starts with `version =` in a staged `.R` file, which is how `defineModule()` normally lays it out. A `version` written mid-line is missed, and an unrelated `version =` line gives one extra confirmation.

Tested with sample inputs only, not yet in a live session.

Drafted with assistance from Claude (Posit Assistant).
