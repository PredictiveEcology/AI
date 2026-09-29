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

**Sketch:** PreToolUse hook matching `bash`; if the command is `git commit` and the
staged diff touches a `version =` line inside a `defineModule()` call, `ask` with a
reminder to check sibling-module version alignment and integration tests first.
