# LandR ecosystem — agent guide

> **This is a template.** Copy it into your workspace root as `AGENTS.md` and adapt
> the machine-specific parts (concrete repository/LandR module set and branches/versions, fork/upstream
> status, local paths, outside-folder read grants). The generic guidance below applies to
> any LandR-based workspace; the copied instance records the specifics of one machine.

This project folder (`~/GitHub/LandR`) holds the **LandR** ecosystem: a suite of
`SpaDES` modules plus accessory R packages that simulate forest and forest-disturbance
dynamics at large landscape scales (vegetation succession, wildfire, climate change,
carbon). It is a working directory that collects many independent module and package
repositories side by side — it is **not** itself a single git repository.

To learn model basics, read the `LandR-Manual/` bookdown (start at
`LandR-Manual/index.Rmd`). The SpaDES toolkit itself is documented at
https://spades.predictiveecology.org/ and lives locally at `~/GitHub/SpaDES/*`.

## Guidelines and setup

Conventions for AI-assisted work on this workspace live in the `guidelines/` folder.
The README has a short **Getting started** and **Prerequisites** overview; start at
`guidelines/00-user-setup.md` (the one-time setup checklist, which now includes
assistant-driven prompt examples for the memory/guardrails/skills steps). The `00*` docs
are **user-facing**; the numbered `01`–`03` docs are **assistant-facing** reference the
assistant consults when a checklist step needs detail:

- `guidelines/00b-user-guidelines.md` — day-to-day guidance on *working with the assistant*:
  responsible use for ecological modeling (adapting Ferrari et al. 2026) and prompting/
  context habits (adapting Anthropic's Claude Code best practices), with a cross-tool
  command portability table. User-facing prose.
- `guidelines/01-project-setup.md` — project-folder and repository-set setup. Assistant-facing.
- `guidelines/02-guardrails.md` — guardrails (permissions, hooks, this `AGENTS.md`). Assistant-facing.
- `guidelines/03-skills.md` — getting, creating, and loading skills. Assistant-facing.

**Shared vs local guidelines.** The `00`/`00b`/`01`–`03` docs are shared and **path-agnostic**.
Each machine also keeps **local instances** — files named `*.local.md` (e.g.
`guidelines/02a-implemented-reference.local.md`) that record concrete, machine-specific
paths and config. Local instances are kept **out of the shared guidelines** and are not
published as team templates; see the "Local instances of these guidelines" section in
`guidelines/00-user-setup.md`. Treat any `*.local.md` file as personal and machine-bound.

**Shared skills.** Team skills are the primary source and should be obtained before
writing new ones. They live in the LandR.ai repo
(https://github.com/CeresBarros/LandR.ai, in `skills/`) and are cloned/synced into a
local skills path (e.g. `~/.agents/skills` or `~/.posit/assistant/skills/`). See
`guidelines/03-skills.md`.

## Repository layout

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

## SpaDES concepts (cheat-sheet)

A simulation is a `simList` object. Modules declare metadata and schedule *events*.
The overall sequence of events is **not** defined centrally: it **emerges bottom-up**
from the combination and ordering of modules and the events each schedules. There is no
top-down master script dictating the order — assembling modules together produces the
simulation's behavior.

Key functions (from `SpaDES.core` unless noted):

- `simInit()` — build a `simList` from modules, params, objects, paths.
- `spades()` — run the simulation by processing scheduled events to the end time.
- `defineModule()` — module metadata block (see anatomy below).
- `defineParameter()`, `expectsInput()`, `createsOutput()` — declare params, inputs, outputs.
- `scheduleEvent()` — queue an event at a future sim time.
- `P(sim)` — module parameters; `mod` / `sim$.mods$<Module>` — module environment/functions.
- `Cache()`, `prepInputs()`, `preProcess()`, `postProcess()` — from `reproducible`
  (caching + data download/prep).
- `spread()`/`spread2()` — from `SpaDES.tools`: spatial spreading functions (e.g. fire
  spread, insect spread) using percolation/diffusion-like processes (not raster
  splitting/merging).
- `Require()` — from `Require` (version-aware package install/load).
- `setupProject()` — from `SpaDES.project`: sets up a whole project (downloads modules,
  installs packages, prepares paths/params) and returns objects ready to pass to
  `simInit()`/`spades()`, greatly simplifying running a multi-module simulation.

## Module anatomy

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

## Running & testing a module

- Run: `simInit(times, params, modules = "<Module>", objects, paths)` then `spades(mySim)`.
- Unit tests use `testthat`, driven from `tests/unitTests.R`; each test builds small
  in-memory rasters/`data.table`s, calls `simInit()`/`spades()` (or a helper directly
  via `sim$.mods$<Module>$<fn>`), and asserts on the result.

## Conventions

- Packages documented with **roxygen2**; tests with **testthat**.
- Use `Cache()`/`prepInputs()` for expensive data steps.
- Module manuals are `.Rmd`, aggregated into multi-module manuals via bookdown.
- **Don't reformat or touch code unless asked.** By default, respect the existing coding
  style and tools as much as possible when changing code. Where reformatting, cleanup, or
  improvements beyond the user's request seem necessary, flag them, justify why, and get
  user approval before implementing them. When only adding/editing documentation or
  comments, change nothing else: keep existing function signatures, brace style (don't add
  braces to single-line `if`/`else`), operator spacing, and blank-line layout — only
  comment/`#'` lines should change.
- **Edit R files with `bash`/Python tools, never the `edit`/`write` tools.** Writing an
  `.R` file through the editor tools can trigger format-on-save (Air-style) reformatting —
  even when Air is nominally disabled — producing large unwanted whitespace/brace/argument
  diffs. Edit `.R` files via a `bash` heredoc or an in-place `python3` script instead, so
  the formatter never runs.
- **Prefer a plan-then-implement flow.** For non-trivial work, design the approach before
  editing (see `guidelines/00b-user-guidelines.md`); plan files live under
  `.posit/assistant/plans/`.
- **Document R functions with `#'` roxygen blocks**, regardless of whether the code lives
  in a package or a module's `R/`. See the `landr-code-documentation` skill for roxygen
  craft (internal helpers get `@keywords internal` + `@noRd`; use `@inheritParams` to avoid
  duplicating parameter docs; preserve `@author`; never reorder function arguments).
- **After any file change (R or otherwise), verify the diff matches the request.** Run
  `git diff <file>` and `git diff --stat` and confirm the change touched only what the user
  asked for — no incidental reformatting, deletions, or unrelated edits. For
  documentation-only R edits, `git diff <file> | grep '^[+-]' | grep -v '^[+-]#'` should
  return nothing (only comment/`#'` lines changed).

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

## Skills

Team skills are the primary source — obtain them before writing new ones. LandR work
depends on **two sister skill repos** (see `guidelines/03-skills.md`):

**LandR skills** — https://github.com/CeresBarros/LandR.ai, in `skills/`:
- `landr-overview` — ecosystem map and SpaDES mental model; entry point/router.
- `landr-code-development` — implementing/changing simulation processes in module code.
- `landr-testing` — unit and integration tests for modules/functions.
- `landr-package-maintenance` — maintaining LandR/LandR.CS/fireSenseUtils packages.
- `landr-manuals` — LandR module `.Rmd` manuals and multi-module bookdown manuals.
- `landr-code-documentation` — comments, module metadata `desc` fields, roxygen2, NEWS.

**SpaDES toolkit skills** — https://github.com/CeresBarros/SpaDES.ai, in `skills/`.
These are **defaults for LandR work**, obtained with the LandR skills:
- `spades-overview` — SpaDES toolkit orientation and routing.
- `spades-module-anatomy` — structure/editing of a SpaDES module's `.R`, metadata, events.
- `spades-module-development` — build/run/debug a module or simulation.
- `spades-module-manuals` — per-module SpaDES manuals (**placeholder, not yet written**;
  until written, `landr-manuals` is the operative skill for LandR module manuals).

The remaining SpaDES.ai skills (`spades-testing`, `spades-code-documentation`,
`spades-package-development`) target SpaDES **package** development and are optional — for
LandR tasks the LandR equivalents above take precedence.
