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

**Sketch:** PreToolUse hook matching `edit|write`; inspect `tool_input.file_path`; if it
ends in `.R`, return `{"permissionDecision": "deny", "permissionDecisionReason":
"Edit .R files via bash/Python, not the editor tool — see AGENTS.md."}`.
