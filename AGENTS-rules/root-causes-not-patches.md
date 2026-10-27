## Root causes, not patches

Fix the defect where it lives. A workaround in the calling script is not a fix: if the
defect is in a package, fix it in the package, with a regression test, even when one
project script is the only thing currently hurting.

Name the root cause explicitly, with `file:line`, before proposing a fix. If you cannot
point at the line, you have not found it yet.

Never stack a patch on a patch. Two workarounds for one symptom means stop and go find
the real cause.

Before inventing a mechanism, look for the project's existing one — test helpers,
conventions, utilities, options. Reaching for a new dependency or a subprocess is
usually a sign that the existing idiom went unread.

**Why:** a patch at the call site leaves the defect in place for the next caller, and
hides it from the tests that would have caught it.
