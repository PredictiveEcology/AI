# SpaDES toolkit — agent guide (template)

> **This is a template.** Copy it into a SpaDES workspace root as `AGENTS.md` and adapt
> the machine-specific parts (concrete repository set, default branches, fork/upstream
> status, local paths, outside-folder read grants). The generic guidance below applies to
> any SpaDES-toolkit workspace; the copied instance records the specifics of one machine.

This project folder holds the **SpaDES toolkit**: the R packages that implement Spatial
Discrete Event System and its supporting infrastructure. Such a folder is typically a
working directory that collects many independent package repositories side by side — it is
**not** itself a single git repository.

SpaDES ("Spatial Discrete Event System") composes independent **modules** into a
simulation whose event sequence emerges bottom-up from the modules assembled — there is no
central controller. This folder holds the *toolkit packages*, not modules; the LandR
ecosystem is an example of a module/model system built on this toolkit. Toolkit docs:
https://spades.predictiveecology.org/.

> **Shared team resources.** The shared conventions, this `AGENTS.md` template, guidelines,
> and skills for AI-assisted SpaDES work live in the **SpaDES.ai** repo
> (`git@github.com:CeresBarros/SpaDES.ai.git`). A workspace `AGENTS.md` is the concrete,
> machine-specific instance of this template. LandR has an equivalent repo, **LandR.ai**
> (https://github.com/CeresBarros/LandR.ai), kept for reference as an example of a
> SpaDES-based system with its own AI-assisted-development support.

## Repository set

Each package is its own git repo. In a typical setup most are **personal forks** (`origin`
= a personal fork, `upstream` = `PredictiveEcology/…`), and a few are direct upstream
clones. **Confirm the actual set for the workspace at hand rather than assuming a canonical
list** — it varies by machine and changes over time. When instantiating this template,
record the concrete table (repo, default branch, origin, upstream).

Core toolkit repos you can expect to encounter: `SpaDES`, `SpaDES.core`, `SpaDES.tools`,
`SpaDES.project`, `SpaDES.experiment`, `SpaDES.config`, `SpaDES.addins`, `SpaDES.docs`,
`SpaDES.install`, `reproducible`, `Require`, `quickPlot`, plus accessory helpers such as
`pemisc` and `fireSenseUtils`, the latter being specific to `fireSense` SpaDES modules. 
Note that default branches are mixed (`main` vs `master`), but new repositories should use `main`.

**Branch/PR workflow:** for forked repos, branch off `upstream`'s default branch, push to
`origin`, and PR to `upstream`.

## What each package does

- **`SpaDES.core`** — the framework: `simInit()`, `spades()`, `defineModule()`,
  `defineParameter()`, `expectsInput()`/`createsOutput()`, `scheduleEvent()`, `P(sim)`,
  `mod`, and accessors (`time()`/`events()`/`objs()`).
- **`SpaDES.tools`** — spatial algorithms: `spread()`/`spread2()`, `neighbourhood()`,
  `splitRaster()`/`mergeRaster()`.
- **`SpaDES.project`** — scaffolding + whole-project setup: `newModule()`, `newProject()`,
  `setupProject()`.
- **`SpaDES.experiment`** — parameter sweeps, replicates, multiple `simList`s.
- **`reproducible`** — `Cache()` (memoize expensive calls), `prepInputs()`
  (`preProcess()`/`postProcess()`) for reproducible data download/prep.
- **`Require`** — reproducible, version/branch-aware package install/load.
- **`quickPlot`** — fast modular plotting (`Plot()`, `clearPlot()`).
- **`SpaDES`** — meta-package tying the toolkit together.
- **`SpaDES.config`**, **`SpaDES.addins`**, **`SpaDES.install`**, **`SpaDES.docs`** —
  configuration, RStudio addins, install helpers, documentation site.
- **`pemisc`**, **`fireSenseUtils`**, **LandR** (the R package, not the model system) — accessory helpers used in SpaDES-based projects.

## Mental model (cheat-sheet)

A simulation is a `simList` — an environment holding objects, parameters, the event queue,
and each module's functions. `simInit()` builds it; `spades()` runs scheduled events to the
end time and returns the `simList`. Modules communicate **only through named objects in the
`simList`**: one module's `createsOutput` is another's `expectsInput`.

## Package anatomy

Each package is a standard R package: `DESCRIPTION`, `NAMESPACE` (roxygen2-generated),
`R/`, `man/`, `tests/testthat/`, `vignettes/`, `NEWS.md`, pkgdown site (`_pkgdown.yml`),
`.Rproj`, `.github/`. Documented with **roxygen2**; tested with **testthat**; the
devtools workflow (`document()`, `load_all()`, `test()`, `check()`) applies throughout.

## Conventions

- Base pipe `|>` (not magrittr `%>%`); `data.table` favored at landscape scale for
  performance/memory. Match the conventions already in the package you are editing.
- Use `Cache()`/`prepInputs()` for expensive or downloaded steps; be deliberate about
  caching stochastic events (generally do not cache them).
- **Memory-efficient R:** avoid `Map()`/`do.call()`/the `apply` family (prefer `purrr`);
  avoid `as.formula()` (captures its environment); don't define closures inside large
  environments.
- **Edit `.R` files with `bash`/Python tools, never the `edit`/`write` tools** — the editor
  can trigger format-on-save (Air-style) reformatting even when nominally disabled,
  producing large unwanted diffs. Edit `.R` via a `bash` heredoc or in-place `python3`.
- **Don't reformat or touch code unless asked.** Respect existing style; flag and get
  approval before cleanup beyond the request. For documentation-only R edits, change only
  comment/`#'` lines.
- **After any file change, verify the diff** with `git diff <file>` / `git diff --stat` and
  confirm only the requested change is present.
- **Prefer plan-then-implement** for non-trivial work; plan files live under
  `.posit/assistant/plans/`.

## Guardrails

Guardrails for AI-assisted work are ecosystem-agnostic and typically installed globally on
the machine; they serve SpaDES unchanged. See `guidelines/02-guardrails.md` for the four
mechanisms (permissions, hooks, this `AGENTS.md`, skills), where each belongs, and their
resolution order. A reference set:

- A `permission` block (deny destructive/blanket-stage, `ask` on `git commit`, allow
  read-only git + `pwd`).
- SessionStart + PreToolUse hooks — behavioral rules + per-action re-approval for
  outside-project access.

Anything outside the workspace folder is **read-only** unless the user grants write access
for a specific path (re-ask each time). Do **not** `git commit` unless explicitly
instructed; stage specific paths (never `git add -A`/`.`); dry-run destructive commands
first.

## Skills (SpaDES.ai set)

Team skills are the primary source — obtain them before writing new ones (shared repo
`CeresBarros/SpaDES.ai`, in `skills/`, synced into a local skills path such as
`~/.agents/skills`). See `guidelines/03-skills.md`. The set:

- `spades-overview` — toolkit map + `simList` mental model; entry point that routes to the
  others.
- `spades-module-anatomy` — structure/editing of a SpaDES module `.R` (metadata, events).
- `spades-module-development` — general dev workflow: `newModule()`, coding against the
  toolkit, running/debugging a `simList`, memory-efficient R, reuse/dependencies. Also
  covers package maintenance.
- `spades-package-development` — developing the SpaDES packages themselves (DESCRIPTION,
  NAMESPACE, devtools/check, NEWS, version bumps).
- `spades-testing` — unit + integration tests (`tests/testthat/`, in-memory inputs,
  asserting on `simList`).
- `spades-code-documentation` — roxygen2, in-code comments, module-metadata `desc` fields,
  NEWS craft. Respect the existing documentation style/language/jargon level (SpaDES targets
  non-programmers — primarily ecologists); check and justify any style/structure change with
  the user first. Use `@keywords internal` for internal functions whether or not exported —
  but check with the user before adding it to an **exported** function.
- `spades-module-manuals` — *(placeholder)* per-module `.Rmd` manuals.

## Generic / misc rules

- **Append an AI-usage disclaimer to all outputs.** Any output produced with AI
  assistance must carry a brief disclaimer noting that Claude (via Posit Assistant)
  helped author it — this applies to **all output types**, not just code and docs:
  commit messages, GitHub issues and PRs (title/body and comments), README and other
  project docs, code and package/module documentation, and reports. Keep it to one line,
  e.g. "Drafted with assistance from Claude (Posit Assistant)." For a whole
  repository/folder, a single repo-wide statement (e.g. in the README) that explicitly
  covers all its documents is sufficient.
- Keep punctuation **outside** text formatting unless part of a name (e.g.
  **SpaDES.project** is fine because the dot is part of the name).
- Write docs for ecologists and scientists of other disciplines that are not computer
  scientists/software engineers: minimize jargon, define any technical term you must use.
- When a session grows long, suggest the user run `/compact` and `/savememory`.

---

Drafted with assistance from Claude (Posit Assistant).
