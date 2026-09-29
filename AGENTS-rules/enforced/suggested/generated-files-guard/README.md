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

**Sketch:** PreToolUse hook matching `edit|write`; inspect `tool_input.file_path`; if it
matches `NAMESPACE` or `man/*.Rd`, return `ask` with a reminder to edit the roxygen2
source (`R/*.R` `@export`/`@param` blocks) and re-run `devtools::document()` instead.
