---
name: landr-code-development
description: Developing, maintaining, and improving the R code that implements LandR SpaDES modules and the LandR-specific mechanisms behind them — implementing or changing simulation processes, but also refactoring, debugging, optimizing, and generally maintaining module .R and R/ helper code, the accessory packages (LandR, LandR.CS, fireSenseUtils), cohort/pixel-group/species-ecoregion data structures, and how modules interact through the simList, all coded against the SpaDES toolkit. Use when the user asks to write, change, fix, improve, or refactor LandR module or package code, implement or adjust a simulation process, or make modules interact. For pure structure/metadata edits use spades-module-anatomy; for tests use testing; for docs use code-documentation.
metadata:
  ecosystem: LandR
  version: "1.1"
---

# LandR code development

This skill governs **writing, changing, maintaining, and improving the R code** of LandR
modules and the LandR-specific mechanisms behind them — not just the module scaffolding.
It spans a range of work:

- **Implementing or changing simulation processes** — the ecological/disturbance logic
  (growth, mortality, dispersal, regeneration, fire, carbon, climate effects).
- **Maintenance and improvement** — debugging, refactoring, optimizing, or otherwise
  tidying existing module and accessory-package code without necessarily changing what
  it models.
- **LandR-specific mechanisms** — the data structures and utilities particular to LandR
  (cohort data, pixel groups, species/ecoregion tables, kNN/CASFRI layer loaders,
  `LandR`/`LandR.CS`/`fireSenseUtils` helpers) rather than generic SpaDES machinery.

For the module file layout and metadata mechanics, use `spades-module-anatomy`; this
skill assumes that structure. The behavioral rules below (process knowledge rests with
the user; changes to existing code need approval and justification; flag process-logic
violations) apply to any of the work above, and most strongly whenever the change touches
what the simulation actually models.

## Build on the general SpaDES skill

LandR modules are built on the SpaDES toolkit, so **the general SpaDES development
guidance applies here and is not repeated**. Follow the `spades-module-development` skill
for all of it, in particular:

- The **SpaDES toolkit** you code against (`SpaDES.core`, `SpaDES.tools`, `reproducible`,
  `Require`, `SpaDES.project`, `quickPlot`) and the develop/run/debug workflow.
- **How modules interact** — communicating only through named `simList` objects, where an
  object name is a contract (`createsOutput` ↔ `expectsInput`); update both metadata and
  code, and confirm cross-module data flow with the user before rewiring it.
- **Change propagation and code placement** — trace changes within a module, across
  modules, and between modules and packages; prompt periodic within- and across-module/
  package integration tests; decide module-vs-package placement.
- **Reuse and dependencies** — check for existing functions before writing new ones; avoid
  and flag new dependencies.
- **Memory-efficient coding** — prefer `purrr` over `Map`/`do.call`/`apply`; avoid
  `as.formula` and closures over large environments; declare functions in packages or the
  module `R/` folder.

This skill adds only what is **LandR-specific** on top of that. For the SpaDES toolkit
source, see `~/GitHub/SpaDES/*` and the `landr-overview` skill's
`references/spades-toolkit.md`.

## LandR module code and mechanisms

- LandR process code lives in `<Module>.R` (below `doEvent`: `Init()` and per-event
  functions like `MortalityAndGrowth()`, `Dispersal()`) and in `R/` helpers. Read these
  real files before editing — modules vary widely in size and idiom.
- LandR shared `simList` objects that act as inter-module contracts include `cohortData`,
  `pixelGroupMap`, and `rstCurrentBurn`; changing their shape can break downstream modules
  (see the cohortData/pixelGroupMap rules below).
- The **timestep** comes from the module's `timeunit` and recurring `scheduleEvent`
  interval (e.g. `time(sim) + P(sim)$successionTimestep`); LandR growth/mortality are
  yearly even when succession events are ~decadal (see the process-logic checks below).

## LandR coding standards and practices

Conventions observed across LandR module and package code. Follow them and match
existing usage in the file you are editing.

### data.table and the base pipe (core LandR idioms)

- **Use `data.table` extensively; avoid `data.frame`/`tibble` and tidyverse idioms** — a
  deliberate LandR choice for performance and memory at landscape scale.
- **`copy()` a `data.table` before modifying** when the original must stay intact — not
  always needed, but prevents silently mutating a table in place (especially objects that
  come from the `simList` and are read by other modules).
- **`setkey()` before joins and use `nomatch = 0`** to drop unmatched rows — faster binary
  joins, and makes "unmatched" explicit instead of silently producing `NA` rows.
- **Use the `..colnames` pronoun and `.SD`/`by=` for group-wise aggregation** rather than
  explicit loops.
- **Use the base pipe `|>`** (not the magrittr `%>%`).

### Parameters and inputs

- **Read parameters via `P(sim)$x`, never `sim$x`** — respects `params(sim)` overrides.
- **Avoid changing parameters from within a module** unless truly necessary; prefer
  changing the default parameter value instead.
- **Use `suppliedElsewhere("obj", sim)` in `.inputObjects`** to fall back to defaults only
  when the user/parent did not supply an object (avoids cache misses).
- **Validate parameter combinations early and warn or stop** (e.g. a very large
  `successionTimestep` warns about consequences).

### cohortData / pixelGroupMap management (LandR-specific, high-risk)

- **Never modify `cohortData` and `pixelGroupMap` separately — go through
  `updateCohortData()`**, which returns both together in one list
  (`list(cohortData = ..., pixelGroupMap = ...)`) so they update in the same step and
  cannot drift out of sync.
- **Regenerate pixelGroups with `generatePixelGroups()` whenever cohort composition
  changes.**
- **Squash young cohorts into one per species/pixelGroup** to prevent age-1 cohort
  explosion (LANDIS-II behavior). `ageReclassification()` acts on
  `age <= successionTimestep + 1`, which is also the age at which `Biomass_core`
  creates new cohorts — so in an undisturbed run nothing is ever younger than that.
  See `references/cohort-semantics.md`.
- **Track burned pixels (`treedFirePixelTableSinceLastDisp`) to avoid double-counting**
  between fire and dispersal.
- **Read the leading-proportion thresholds through `mixedwoodProp()` /
  `leadingSpeciesProp()`**, never as literals — they are two different questions that
  share one argument name (`references/cohort-semantics.md`).

### Assertions and defensive checks

- **Gate expensive assertions behind `getOption("LandR.assertions", ...)`** so production
  runs can skip them.
- **Re-assert `cohortData` and `pixelGroupMap` integrity after each modification** — no
  duplicate rows by the cohort-defining columns, and `pixelGroupMap` IDs aligned with
  `cohortData` (`assertPixelCohortData()`).
- **Validate input schema with `LandR::assertColumns()`** (names + types) before use.
- **Check ecoregionGroup consistency across `ecoregionMap`/`speciesEcoregion`/`cohortData`
  with `assertERGs()`**.

### Numerics, units, timestep

- **Store age/biomass/ANPP as integers; convert with `asInteger()` (rounds), not
  `as.integer()` (truncates)** to avoid systematic bias.
- **Compare floats/probabilities with `fpCompare` operators** (e.g. `%>>%`) instead of
  `>`/`==`.
- **Document timestep semantics explicitly** — e.g. growth/mortality are yearly even when
  succession events are ~decadal.

### Caching / reproducibility

- Follow the general caching guidance in `spades-module-development` (`Cache`,
  `prepInputs`, and not caching stochastic events). LandR-specific: **use `.useCache` to
  cache `.inputObjects`/`init`** and tag caches with the module
  (`cacheTags <- c(currentModule(sim), "init")`).

### Messaging and errors

- **`message()` for info, `warning()` for cautions, `stop()` for fatal** — and validate
  inputs with `stop()` at the top of functions before expensive work. See
  `spades-module-development` for the general tradeoffs between the three (what each does
  during and after a run); **consult the user and state the tradeoff** before choosing one
  over another, especially for warnings that could go unnoticed in a long batch/HPC run.
- **Prefix messages with context** (module name, pixel group) for traceability across
  millions of pixels.
- **Respect `LandR.verbose` for log verbosity.** Level semantics are still being pinned
  down (see LandR.ai issue #3).
- **Colour messages with `crayon` by message type, consistently** — observed convention:
  `crayon::green()` for regeneration/progress, `crayon::magenta()` for summary
  statistics/counts, `crayon::red()` for error/warning conditions. Being formalized in
  LandR.ai issue #4.

### Naming / style / dependencies

LandR-specific conventions (general style and dependency rules are in
`spades-module-development`):

- **camelCase column names consistently** (`speciesCode`, `ecoregionGroup`, `pixelGroup`);
  `.`-prefixed private params (`.plots`, `.useCache`).
- **PascalCase for major event functions, camelCase for minor events/helpers.**
- **Pin `reqdPkgs` to `PredictiveEcology/…@development (>= …)`** for LandR/dev packages.
- **In accessory packages: `@importFrom` (not `library()`), and declare NSE symbols via
  `utils::globalVariables()`** to keep `R CMD check` clean.

### Performance at landscape scale

- **Save/restore `data.table` threads with `on.exit()`** to coexist with explicit
  parallelism.
- **Chunk large operations (`cutpoint`) and index raster values once** rather than repeated
  `getValues()`.
- **Take care expanding `cohortData` to pixel level** — do it only for processes that
  genuinely act at pixel scale (spatially-explicit processes like dispersal and fire).
- Some modules compile hot loops with `compiler::cmpfun()`; whether this is still
  beneficial under modern R is unverified (see LandR.ai issue #2) — do not add it reflexively.

### Cross-module consistency to flag

- `cohortDefinitionCols` can diverge between modules; if a change could make module
  definitions of a cohort inconsistent, flag it to the user rather than proceeding.

## `Biomass_core` and its LANDIS-II ancestry

`Biomass_core` was originally ported from the **LANDIS Biomass Succession Extension
v3.2.1**, which itself runs on **LANDIS-II Core Model v6.0**. Before proposing any
**mechanistic** change to `Biomass_core` (a change to what a growth/mortality/succession
process actually computes, not a refactor/perf/doc change), thoroughly evaluate the
original source first:

- Extension source and its history: https://github.com/LANDIS-II-Foundation/Extension-Biomass-Succession
- Core model source and its history: https://github.com/LANDIS-II-Foundation/Core-Model-v6

The current logic and any deviations from the original C#/VB implementation are often only
findable in **commit history**, not the latest code — check history, not just the default
branch tip. Treat this as an extension of "process knowledge rests with the user" below:
**consult the user carefully before implementing any mechanistic change**, present what the
LANDIS-II source does, and confirm whether the intended change is a deliberate departure
from that ancestry or should match it.

## Process knowledge rests with the user

This is the central working rule of this skill.

- **The user owns the process/phenomenon knowledge.** They must be specific about *what
  simulation process* is being implemented (which ecological or disturbance phenomenon,
  at what spatial/temporal scale, with what inputs and outputs). The AI may contribute
  more *programming* knowledge, but the user is the authority on the science being
  modelled.
- If a request is vague about the process ("improve the growth code"), **ask the user to
  specify the phenomenon and its intended behavior** before writing code. Do not invent
  ecological behavior.
- The user does not need to know *how* to program the process — that is where the AI
  helps — but they must know *what* they are asking for.

## Get approval and justify changes to existing code

- **Changes to existing code must be approved by the user and thoroughly justified.**
  Before editing working module code, explain what will change, why, and what downstream
  effects it may have (including on other modules via shared `simList` objects). Present
  the change and wait for approval rather than applying it unilaterally.
- Prefer the smallest change that implements the requested process; do not refactor
  surrounding code opportunistically.

## Flag requests that violate process/phenomenon logic

When a request appears to contradict expected ecological, physical, or simulation logic,
**stop and flag it** to the user rather than implementing it silently. Examples of things
to catch:

- **Timestep/rate mismatches** — e.g. code that ages a tree by 3 years on every
  yearly timestep, or applies an annual mortality rate once per decade without rescaling.
- **Units/scale errors** — mixing per-pixel and per-hectare quantities, or per-timestep
  and per-year rates.
- **Impossible states** — negative biomass/age, cohorts older than the simulation,
  regeneration without a seed source, fire spreading with zero spread probability.
- **Broken conservation** — carbon or biomass created or destroyed without a
  corresponding flux.

Describe the concern in plain terms, state what you expected instead, and ask the user to
confirm or correct before proceeding. The user has final say on the science — but a likely
process-logic error should never be coded up without being surfaced first.
