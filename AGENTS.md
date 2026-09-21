# PredictiveEcology agent guide (template)

> **This is a template.** Copy it into your workspace root as `AGENTS.md` and adapt the
> machine-specific parts (concrete repository set, branches/versions, fork/upstream
> status, local paths, outside-folder read grants). The generic guidance below applies to
> any workspace using this repo's conventions; the copied instance records the specifics
> of one machine. Include only the ecosystem-specific section(s) relevant to your
> workspace (LandR, SpaDES toolkit, or both) — drop the other if your workspace doesn't
> touch it.

This file is the project-memory template shared by the `AI` repo
(`PredictiveEcology/AI`) across PredictiveEcology's AI-assisted-development work. It
currently covers two ecosystems built on the SpaDES toolkit — **LandR** (forest
landscape simulation) and the **SpaDES toolkit** itself — and is structured so other
team conventions (e.g. data visualization, report writing) can be added as their own
sections later without redesigning this template.

## Guidelines and setup

Conventions for AI-assisted work live in this repo's `guidelines/` folder. Start at
`guidelines/00-user-setup.md` (the one-time setup checklist, including assistant-driven
prompt examples for the memory/guardrails/skills steps). The `00*` docs are
**user-facing**; the numbered `01`–`03` docs are **assistant-facing** reference the
assistant consults when a checklist step needs detail:

- `guidelines/00b-user-guidelines.md` — day-to-day guidance on *working with the
  assistant*: responsible use for ecological/scientific modeling (adapting Ferrari et al.
  2026) and prompting/context habits (adapting Anthropic's Claude Code best practices),
  with a cross-tool command portability table. User-facing prose.
- `guidelines/01-project-setup.md` — project-folder and repository-set setup.
  Assistant-facing.
- `guidelines/02-guardrails.md` — guardrails (permissions, hooks, this `AGENTS.md`).
  Assistant-facing.
- `guidelines/03-skills.md` — getting, creating, and loading skills. Assistant-facing.

**Shared vs local guidelines.** The `00`/`00b`/`01`–`03` docs are shared and
**path-agnostic**. Each machine also keeps **local instances** — files named
`*.local.md` (e.g. `guidelines/02a-implemented-reference.local.md`) that record
concrete, machine-specific paths and config. Local instances are kept **out of the
shared guidelines** and are not published as team templates; see the "Local instances of
these guidelines" section in `guidelines/00-user-setup.md`. Treat any `*.local.md` file
as personal and machine-bound.

**Shared skills.** Team skills are the primary source and should be obtained before
writing new ones. They live in this repo (`PredictiveEcology/AI`, in `skills/`) and are
cloned/synced into a local skills path (e.g. `~/.agents/skills` or
`~/.posit/assistant/skills/`). See `guidelines/03-skills.md`.

---

## LandR ecosystem

*Include this section if your workspace holds LandR modules/packages.*

A LandR project folder (e.g. `~/GitHub/LandR`) holds the **LandR** ecosystem: a suite of
`SpaDES` modules plus accessory R packages that simulate forest and forest-disturbance
dynamics at large landscape scales (vegetation succession, wildfire, climate change,
carbon). It is a working directory that collects many independent module and package
repositories side by side — it is **not** itself a single git repository.

**Hierarchy: LandR is an application built on the SpaDES toolkit, not part of it.**
`SpaDES`/`SpaDES.core` and its companion packages (see the "SpaDES toolkit" section below)
are the general-purpose discrete-event simulation framework; LandR modules and accessory
packages are one model system written *using* that framework, specific to forest-landscape
simulation. Toolkit changes can affect any model system built on it; LandR-specific changes
(cohort data, species/ecoregion mechanics, `Biomass_*`/`fireSense_*` process logic) affect
only LandR. Keep this direction of dependency in mind when tracing a change's blast radius
or deciding which skill applies.

To learn model basics, read the `LandR-Manual/` bookdown (start at
`LandR-Manual/index.Rmd`). The SpaDES toolkit itself is documented at
https://spades.predictiveecology.org/ and, if present as a sibling, typically lives at
`~/GitHub/SpaDES/*`.

### Repository layout

The lists below are a **starting point, not a fixed set**. They enumerate families of
modules and packages that are either at the core of LandR or heavily used in LandR
simulations. A given workspace may hold only some of them, and will often also hold:

- **other PredictiveEcology / collaborator repos** — additional modules and packages
  maintained by or available through the PredictiveEcology group and its collaborators
  (e.g. the `SCFM` family of fire modules, and more) that are not listed here; and
- **user-specific repos** — modules and packages the individual user maintains or finds
  relevant to their own work, which may not be part of the shared ecosystem at all.

LandR is open source: anyone can write their own modules and link them to these. Confirm
the actual repository set for the workspace at hand (see `guidelines/01-project-setup.md`)
rather than assuming the families below are exhaustive.

- **Module versions**: major/minor versions must stay aligned across modules in a workflow
  (e.g. the `Biomass_*` family), so an unrelated module may need a version bump just to keep
  pace — but only after confirming compatibility with modules that did change, primarily via
  module integration tests. See `landr-package-maintenance`'s "Module version alignment"
  section.
- **Modules** (`<project>/<ModuleName>/`) — SpaDES module folders. Common core families:
  - `Biomass_*` — forest biomass succession (LANDIS-II–style): flagship `Biomass_core`,
    data-prep (`Biomass_borealDataPrep`, `Biomass_speciesData`, `Biomass_sppEcoreg*`),
    parameterization, fuels, regeneration, validation, summary.
  - `fireSense_*` — fire modelling, organized as fit/predict pairs for ignition, escape,
    spread, and size, plus data-prep and summary modules.
  - Carbon: `LandR_CBM`, `LandRCBM*`, `LandRCSAM`.
- **Accessory R packages:**
  - `LandR/` — core utilities: cohort-data helpers, species/ecoregion tables,
    kNN/CASFRI/Pickell layer loaders, assertions, study-area/map utilities. Imports
    `SpaDES.core`, `SpaDES.tools`. roxygen2 docs; no test suite yet.
  - `LandR.CS/` — climate-sensitive growth/mortality (`calculateClimateEffect`).
  - `fireSenseUtils/` — fire data extraction, DEoptim optimization, helpers. Has a
    small `tests/testthat/` suite.
- **`LandR-Manual/`** — bookdown manual aggregating per-module manuals.

### Module anatomy

Each module folder is consistent:

- `<Module>.R` — `defineModule(sim, list(...))` metadata
  (`parameters`/`inputObjects`/`outputObjects`) followed by
  `doEvent.<Module>()` (a `switch(eventType, init = {...}, ...)` dispatcher),
  an event function for initialization, and per-event helper functions.
  Distinguish **events** from **event functions**: an event is the named case in the
  `switch` (its name is the value of the `eventType` argument, e.g. `init`, which must be
  spelled exactly). The **event function** it calls can be named anything — by convention
  the `init` event calls a function named `Init()`, but that name is not required.
- `<Module>.Rmd` / `.md` / `.html` — module manual (bookdown-style, auto-generated badges).
- `R/` — module-local helper functions.
- `tests/unitTests.R` (entry point using `test_dir()`) + `tests/testthat/test-*.R`.
- `data/` (with `CHECKSUMS.txt`), `citations/`, `citation.bib`, `figures/`,
  `NEWS.md`, `LICENSE`, `<Module>.Rproj`.

### Running & testing a module

- Run: `simInit(times, params, modules = "<Module>", objects, paths)` then `spades(mySim)`.
- Unit tests use `testthat`, driven from `tests/unitTests.R`; each test builds small
  in-memory rasters/`data.table`s, calls `simInit()`/`spades()` (or a helper directly
  via `sim$.mods$<Module>$<fn>`), and asserts on the result.

### LandR conventions

- Packages documented with **roxygen2**; tests with **testthat**.
- Use `Cache()`/`prepInputs()` for expensive data steps.
- Module manuals are `.Rmd`, aggregated into multi-module manuals via bookdown.
- **Document R functions with `#'` roxygen blocks**, regardless of whether the code lives
  in a package or a module's `R/`. See the `code-documentation` skill for roxygen craft
  (internal helpers get `@keywords internal` + `@noRd`; use `@inheritParams` to avoid
  duplicating parameter docs; preserve `@author`; never reorder function arguments).

### LandR skills

- `landr-overview` — ecosystem map and SpaDES mental model; entry point/router.
- `landr-code-development` — implementing/changing simulation processes and
  LandR-specific mechanisms (cohorts, pixel groups, species/ecoregion) in module code;
  builds on `spades-module-development`.
- `landr-package-maintenance` — maintaining LandR/LandR.CS/fireSenseUtils packages.
- `landr-manuals` — LandR module `.Rmd` manuals and multi-module bookdown manuals.

These sit alongside the shared `testing` and `code-documentation` skills, and the SpaDES
toolkit skills below (used **by default** in LandR work).

---

## SpaDES toolkit

*Include this section if your workspace holds SpaDES toolkit packages.*

A SpaDES toolkit project folder holds the R packages that implement Spatial Discrete
Event System and its supporting infrastructure. Such a folder is typically a working
directory that collects many independent package repositories side by side — it is
**not** itself a single git repository.

SpaDES ("Spatial Discrete Event System") composes independent **modules** into a
simulation whose event sequence emerges bottom-up from the modules assembled — there is
no central controller. This section covers the *toolkit packages*, not modules; LandR is
an example of a module/model system built on this toolkit. Toolkit docs:
https://spades.predictiveecology.org/.

### Repository set

Each package is its own git repo. In a typical setup most are **personal forks**
(`origin` = a personal fork, `upstream` = `PredictiveEcology/…`), and a few are direct
upstream clones. **Confirm the actual set for the workspace at hand rather than assuming
a canonical list** — it varies by machine and changes over time. When instantiating this
template, record the concrete table (repo, default branch, origin, upstream).

Core toolkit repos you can expect to encounter: `SpaDES`, `SpaDES.core`, `SpaDES.tools`,
`SpaDES.project`, `SpaDES.experiment`, `SpaDES.config`, `SpaDES.addins`, `SpaDES.docs`,
`SpaDES.install`, `reproducible`, `Require`, `quickPlot`, plus accessory helpers such as
`pemisc` and `fireSenseUtils`, the latter being specific to `fireSense` SpaDES modules.
Note that default branches are mixed (`main` vs `master`), but new repositories should
use `main`.

**Branch/PR workflow:** for forked repos, branch off `upstream`'s default branch, push to
`origin`, and PR to `upstream`.

### What each package does

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
- **`pemisc`**, **`fireSenseUtils`**, **LandR** (the R package, not the model system) —
  accessory helpers used in SpaDES-based projects.

### Mental model (cheat-sheet)

A simulation is a `simList` — an environment holding objects, parameters, the event queue,
and each module's functions. `simInit()` builds it; `spades()` runs scheduled events to the
end time and returns the `simList`. Modules communicate **only through named objects in the
`simList`**: one module's `createsOutput` is another's `expectsInput`.

### Package anatomy

Each package is a standard R package: `DESCRIPTION`, `NAMESPACE` (roxygen2-generated),
`R/`, `man/`, `tests/testthat/`, `vignettes/`, `NEWS.md`, pkgdown site (`_pkgdown.yml`),
`.Rproj`, `.github/`. Documented with **roxygen2**; tested with **testthat**; the
devtools workflow (`document()`, `load_all()`, `test()`, `check()`) applies throughout.

### SpaDES toolkit skills

- `spades-overview` — toolkit map + `simList` mental model; entry point that routes to
  the others.
- `spades-module-anatomy` — structure/editing of a SpaDES module `.R` (metadata, events).
- `spades-module-development` — general dev workflow: `newModule()`, coding against the
  toolkit, running/debugging a `simList`, memory-efficient R, reuse/dependencies.
- `spades-package-development` — developing the SpaDES packages themselves (DESCRIPTION,
  NAMESPACE, devtools/check, NEWS, version bumps). **Stub, not yet populated.**
- `spades-module-manuals` — per-module `.Rmd` manuals. **Placeholder, not yet written**
  (until written, `landr-manuals` is the operative skill for LandR module manuals).

These are **defaults for LandR work** as well, obtained alongside the LandR skills.

---

## Shared conventions (both ecosystems)

- Use `data.table` and the base pipe `|>` (not magrittr `%>%`); favored at landscape
  scale for performance/memory. Match the conventions already in the package/module you
  are editing.
- Use `Cache()`/`prepInputs()` for expensive or downloaded steps; be deliberate about
  caching stochastic events (generally do not cache them).
- **Memory-efficient R:** avoid `Map()`/`do.call()`/the `apply` family (prefer `purrr`);
  avoid `as.formula()` (captures its environment); don't define closures inside large
  environments.
- **Don't reformat or touch code unless asked.** By default, respect the existing coding
  style and tools as much as possible when changing code. Where reformatting, cleanup, or
  improvements beyond the user's request seem necessary, flag them, justify why, and get
  user approval before implementing them. When only adding/editing documentation or
  comments, change nothing else: keep existing function signatures, brace style (don't add
  braces to single-line `if`/`else`), operator spacing, and blank-line layout — only
  comment/`#'` lines should change.
- **Edit `.R` files with `bash`/Python tools, never the `edit`/`write` tools.** Writing an
  `.R` file through the editor tools can trigger format-on-save (Air-style) reformatting —
  even when Air is nominally disabled — producing large unwanted whitespace/brace/argument
  diffs. Edit `.R` files via a `bash` heredoc or an in-place `python3` script instead, so
  the formatter never runs.
- **Prefer a plan-then-implement flow.** For non-trivial work, design the approach before
  editing (see `guidelines/00b-user-guidelines.md`); plan files live under
  `.posit/assistant/plans/`.
- **After any file change, verify the diff matches the request.** Run `git diff <file>`
  and `git diff --stat` and confirm the change touched only what the user asked for — no
  incidental reformatting, deletions, or unrelated edits. For documentation-only R edits,
  `git diff <file> | grep '^[+-]' | grep -v '^[+-]#'` should return nothing (only
  comment/`#'` lines changed).

## Guardrails

Guardrails for AI-assisted work are ecosystem-agnostic and typically installed globally on
the machine; they serve both LandR and the SpaDES toolkit unchanged. See
`guidelines/02-guardrails.md` for the four mechanisms (permissions, hooks, this
`AGENTS.md`, skills), where each belongs, and their resolution order. A reference set:

- A `permission` block (deny destructive/blanket-stage, `ask` on `git commit`, allow
  read-only git + `pwd`).
- SessionStart + PreToolUse hooks — behavioral rules + per-action re-approval for
  outside-project access.

Anything outside the workspace folder is **read-only** unless the user grants write access
for a specific path (re-ask each time). Do **not** `git commit` unless explicitly
instructed; stage specific paths (never `git add -A`/`.`); dry-run destructive commands
first.

## Skills (shared set)

Team skills are the primary source — obtain them before writing new ones (shared repo
`PredictiveEcology/AI`, in `skills/`, synced into a local skills path such as
`~/.agents/skills`). See `guidelines/03-skills.md`.

- `testing` — unit + integration tests (`tests/testthat/`, in-memory inputs, asserting on
  `simList`) for modules, toolkit packages, and accessory packages.
- `code-documentation` — roxygen2, in-code comments, module-metadata `desc` fields, NEWS
  craft. Respect the existing documentation style/language/jargon level (both ecosystems
  target non-programmers — primarily ecologists and other scientists); check and justify
  any style/structure change with the user first. Use `@keywords internal` for internal
  functions whether or not exported — but check with the user before adding it to an
  **exported** function.

The ecosystem-specific skills (LandR, SpaDES toolkit) are listed in their sections above.

## Generic / misc rules

- **Append an AI-usage disclaimer to all outputs.** Any output produced with AI
  assistance must carry a brief disclaimer noting that Claude (via Posit Assistant)
  helped author it — this applies to **all output types**, not just code and docs:
  commit messages, GitHub issues and PRs (title/body and comments), README and other
  project docs, code and package/module documentation, and reports. Keep it to one line,
  e.g. "Drafted with assistance from Claude (Posit Assistant)." For a whole
  repository/folder, a single repo-wide statement (e.g. in the README) that explicitly
  covers all its documents is sufficient.
- Keep punctuation **outside** text formatting, unless the punctuation is part of a
  word. For example, write **formatted text**. (period outside the bold), not
  **formatted text.** — but **SpaDES.project** is fine because the dot is part of the
  name.
- Write docs for ecologists and scientists of other disciplines that are not computer
  scientists/software engineers: minimize jargon, define any technical term you must use.
- When a session grows long, suggest the user run `/compact` and `/savememory`.

---

Drafted with assistance from Claude (Posit Assistant).
