# Working with the assistant

This is practical, user-facing guidance on *how* to work with an AI coding assistant on
the SpaDES toolkit. It has two parts: (1) using the assistant responsibly for scientific
model development, and (2) day-to-day tips and tools for getting good results.

> **Which assistant this assumes.** This guidance assumes you're running Posit Assistant
> in Positron, powered by Anthropic Claude models. Slash commands (e.g. `/clear`, `/compact`, `/savememory`) 
> and UI details may
> differ in RStudio and the terminal (TUI), and in other AI coding tools and models
> (Claude Code, ChatGPT, Copilot) — but the underlying practices carry over everywhere, and
> only the exact commands and gestures need adapting. Where a command is tool-specific we've
> done our best to call it out in the portability table below.

> **You are responsible for what the assistant is instructed to do.** The assistant acts on
> instructions and content from these guidelines, the `AGENTS.md` memory, the skills, and
> your prompts. Knowing what those instructions say — including the assistant-facing `01`–`03`
> docs and the skills — is your responsibility, as is reviewing the assistant's output before
> you rely on it. Nothing here removes that responsibility.

## Using the assistant for scientific modeling

SpaDES is a framework for building simulation models, and the assistant is a tool for
*building and checking* those models — not for originating the science. That's your job.
The points below adapt the seven guidelines of Ferrari et al. (2026) — a viewpoint on
responsible generative-AI use in the ecological sciences — to this workspace. They lean on
rules already implemented in `AGENTS.md` (caching/reproducibility, respecting existing
methods, the AI-authorship footer) rather than restating them.

- **Lead with the science, then reach for the assistant.** Ground module and package
  design in domain theory and knowledge; use the assistant to implement and verify, not to
  invent the hypotheses or the model structure.
- **Prefer the simplest sufficient tool.** Don't reach for AI-driven complexity where an
  existing SpaDES toolkit function, a plain script, or a standard method already does the
  job — consistent with the workspace rule to respect existing methods and style.
- **The fundamentals of inference still apply.** When you have the assistant wrangle or
  combine data, keep sampling design, units, and metadata in view; treat merges of unknown
  provenance as exploratory, to be confirmed against known data; and keep the final say on
  parameterization yourself.
- **Protect reproducibility and transparency.** The assistant's outputs are stochastic,
  which is a reproducibility risk — lean on the existing `Cache()`/`prepInputs()`
  conventions, and disclose AI assistance via the `AGENTS.md` authorship footer. Don't paste
  sensitive or unpublished data into the assistant.
- **Keep yourself in the loop and keep building skill.** Read and understand the code the
  assistant produces rather than accepting black-box output; this pairs with the
  verification and review habits in the next section.

Reference: Ferrari et al. (2026), see sources at the end of this file.

## Working effectively with the assistant

A handful of habits that make the assistant more useful, adapted from Anthropic's ["Best practices for Claude Code"](https://code.claude.com/docs/en/best-practices). Each point pairs a short principle with a table of how to put it
into practice. The commands shown are Posit Assistant commands; the closing portability
table says which ones transfer to other tools -- following [Posit Assistant Commands reference](https://assistant.posit.co/docs/features/commands/).

**1. Explore first, then plan, then code.** Have the assistant research and plan before it
implements, so you don't end up with a tidy solution to the wrong problem.

| Phase | What to do |
| --- | --- |
| Explore | Ask the assistant to read the relevant module/package and explain it, making no changes. |
| Plan | Ask for a written implementation plan (files to touch, event flow) before editing. |
| Implement | Approve the plan, then have it code and verify against the plan. |
| Skip | For a one-sentence diff (typo, log line, rename) skip planning and ask directly. |

**2. Give the assistant a way to verify its work.** Hand it a check it can run itself, and
ask it to show you the evidence rather than just claim success.

| Strategy | Weak prompt | Stronger prompt |
| --- | --- | --- |
| Provide verification criteria | "add a helper to validate input codes" | "add a helper to validate input codes; example cases: `abc` valid, `""` invalid. Run the testthat tests after." |
| Verify against a run | "make the module run" | "run `simInit()`/`spades()` on the test setup, show the error, fix the root cause, and rerun to confirm." |
| Show evidence, don't assert | "did it work?" | "show the test output / the command you ran and its result, not just a claim of success." |

**3. Be specific in your prompts.** The more you scope the task, point to sources,
reference existing patterns, and describe the symptom, the fewer corrections you'll need.

| Strategy | Weak prompt | Stronger prompt |
| --- | --- | --- |
| Scope the task | "add tests for the module" | "write a testthat test for `<fn>` covering the empty-input edge case; build a small in-memory `data.table`." |
| Point to sources | "why is this parameter here?" | "look through this module's git history and summarize how `<param>` came to be a parameter." |
| Reference existing patterns | "add a new data-prep module" | "look at an existing data-prep module for the pattern and follow it for the new one." |
| Describe the symptom | "fix the caching bug" | "`Cache()` re-runs every time here; check the args passed to it, write a failing test, then fix." |

**4. Give it rich content.** Hand the assistant real material instead of describing it:
reference a file by path so it reads it; paste or drag in a screenshot or figure; give a URL
for a package or API reference; or paste/pipe command output such as an error log.

**5. Manage context aggressively.** A full context window makes results worse, so reset and
condense often.

| Command | When to use it |
| --- | --- |
| `/clear` | Between unrelated tasks; starts a new conversation (keeping model, thinking effort, and web-search settings). |
| `/compact` | Mid-task when context is filling; optionally `/compact <focus>` to steer the summary, e.g. `/compact focus on the simList parameter changes`. |
| `/microcompact` | To trim token usage by replacing tool results with placeholders (runs locally, no model call). |
| Conversation history / branching | To revisit or fork from an earlier point (Posit Assistant's nearest analogue to Claude Code's `/rewind` — see portability table). |
| `/savememory` | To checkpoint durable project facts to `AGENTS.md` before clearing. |

`/compact` and `/savememory` also appear in the workspace guardrail hook, which nudges you
to run them when a session grows long.

**6. Course-correct early, and use subagents for investigation.** Redirect the assistant as
soon as it drifts, and delegate wide reads so your main conversation stays focused.

A *subagent* is a separate, short-lived assistant that the one you're talking to can launch
to do a focused job — for example reading many files to answer a single question — in its own
context window, returning only a summary. You don't create subagents yourself in Posit
Assistant; you just ask for one, e.g. "use a subagent to find every module that reads
`<objectName>`", and its exploration stays out of your main conversation.

| Situation | Action |
| --- | --- |
| Assistant drifts off task | Stop it (Esc), then redirect with a corrected prompt. |
| Two corrections haven't fixed it | `/clear` and restart with a better prompt incorporating what you learned. |
| Need a wide codebase investigation | Ask the assistant to use a subagent so exploration doesn't fill the main context. |
| Change looks done | Ask for a fresh-context subagent to review the diff for gaps before accepting. |

**7. Watch for common failure patterns.** When you spot one of these, apply the fix.

| Failure pattern | Fix |
| --- | --- |
| Kitchen-sink session (unrelated tasks pile up) | `/clear` between unrelated tasks. |
| Correcting in circles | After two failed corrections, `/clear` and re-prompt more specifically. |
| Over-specified `AGENTS.md` | Prune ruthlessly; move must-happen rules into hooks. |
| Trust-then-verify gap | Always give a check (tests/run/screenshot); don't ship what you can't verify. |
| Infinite exploration | Scope investigations narrowly or hand them to a subagent. |

**What transfers to other tools.** The practices above are generic; the exact commands are
not. This table classifies each item so that, if you're working in RStudio, the TUI, or a
different assistant, you know what to adapt.

| Item | Command name | Behaviour | Portability note |
| --- | --- | --- | --- |
| `/clear` | Shared token, different meaning | Tool-specific | In Posit Assistant `/clear` starts a new conversation (keeping settings); in Claude Code it resets context within the same session. Same intent, different mechanics. Most chat LLMs (ChatGPT, Copilot) have no typed command — you open a new chat. Practice generic; command not. |
| `/compact`, `/compact <focus>` | Shared Claude↔Posit | Broadly similar | Both summarize to shrink context, and both accept a focus. Other LLMs compact automatically with no user command. Command name shared; manual trigger not universal. |
| `/microcompact` | Posit-Assistant-specific | Posit-Assistant-specific | Placeholder-swaps tool results locally to save tokens; no direct single-command Claude Code equivalent. Concept (shrink context) generic. |
| `/savememory` | Posit-Assistant-specific | Posit-Assistant-specific | Writes to `AGENTS.md` memory. Claude Code uses `/memory` + `CLAUDE.md`; other tools differ or lack it. The idea (persist durable facts) is generic. |
| `/rewind` (Esc Esc) | Claude-Code-specific | Claude-Code-specific | Checkpoint rewind of conversation/code is a Claude Code feature. In Posit Assistant use `/microcompact` and conversation history/branching instead. |
| `Esc` to interrupt | Tool-specific keybinding | Concept generic | Interrupting a running turn exists in most assistants; the exact key or gesture varies (Positron chat vs TUI vs a terminal tool). |
| Plan mode (point 1) | Different entry | Concept generic | Posit Assistant has Plan mode (`/plan`); Claude Code enters it with `Shift+Tab`. The explore→plan→code discipline is generic. |
| Subagents (point 6) | Capability, not a user command | Assistant-invoked | You ask the assistant to delegate; you don't type a command. Claude Code additionally lets power users define agent files — that authoring step is Claude-Code-specific and not available in Posit Assistant. |
| Prompt examples (points 2–3, 7) | n/a | n/a | Pure prompt-writing advice — fully generic across assistants; only the SpaDES content is workspace-specific. |

## Sources

- Anthropic. "Best practices for Claude Code." https://code.claude.com/docs/en/best-practices
- Posit Assistant. "Commands." https://assistant.posit.co/docs/features/commands/
- Ferrari, N. C., Conklin, E. E., Fitch, A. A., Gannon, D. G., Macedo, R., Place, A.,
  Sachs, H. R., Seo, E., Weldy, M. J., & Betts, M. G. (2026). Thinking Outside the Black
  Box: Seven Guidelines for GenAI Use in the Ecological Sciences. *Ecology and Evolution*,
  16(8), e74118. https://doi.org/10.1002/ece3.74118
