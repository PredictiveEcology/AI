## Writing PRs, issues and comments

Colleagues read these. Length is a cost they pay, not a signal of effort.

- Lead with the outcome: what changed, and what a reviewer must do. Not the
  investigation narrative, and not what was ruled out — that belongs in a session log.
- A PR description is usually three to six sentences: the defect (`file:line`), the fix,
  how it was verified. If it needs more, the PR is probably too big.
- Plain English. No "notably", "comprehensive", "robust", "leverage". Say "the clip
  never ran", not "the clipping operation was not invoked in this code path".
- No headers, bold, tables or bullets in a short comment. Structure is for documents,
  not for three paragraphs.
- Do not pad with caveats, restated context, or a summary of what you just said.
- State status once, plainly. Never close by calling the work "ready" or "complete".

Test before posting: would a busy colleague get the point from the first two sentences?

**Why:** direct feedback from a reviewer, 2026-09-18 — AI-written PRs, issues and
comments are too long, too verbose, and the language is hard to decipher.
