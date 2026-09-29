# long-run-interlock

**Optional.** A PreToolUse hook that warns or blocks starting a new `spades()`/
simulation run, or mutating a module's library (editing its `R/` code or reinstalling
its dependencies), while another long run may still be in progress on a shared machine.

**Why:** SpaDES/LandR simulation runs can take hours; starting a second run, or editing
a module's code mid-run, risks corrupting shared state (a module's library, cached
objects, output directories) that the first run is still using.

**Why optional, not default:** requires a way to detect "a run may be in progress" that
is specific to how a given team runs simulations (a lock file, a known PID, a running-job
registry) — there is no single mechanism that generalizes across setups, so this is a
pattern to adapt rather than a ready-made script.

**Sketch:** PreToolUse hook matching `bash|executeCode`; if the command looks like it
starts a `spades()`/simulation run, check for a project-specific lock/marker; if present,
`ask` with a reminder to confirm no other run is using the same module library or output
paths.
