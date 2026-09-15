---
name: spades-module-anatomy
description: Structure and editing conventions for any SpaDES module — the module .R file (defineModule metadata, defineParameter, expectsInput, createsOutput, doEvent dispatcher, Init and event helpers), the R/ helpers, data/CHECKSUMS.txt, and accompanying files. Use when reading, creating, or modifying a SpaDES module's .R code, adding parameters or inputs/outputs, or wiring up events. For building/running/debugging a module or simulation use spades-module-development; for developing the SpaDES packages themselves use spades-package-development.
metadata:
  ecosystem: SpaDES
  version: "1.0"
---

# SpaDES module anatomy

Each SpaDES module lives in its own folder `<Module>/` with a consistent layout. Read the
real files before editing — modules vary widely in size (some flagship modules run to a
couple thousand lines).

## Files in a module folder

- `<Module>.R` — the module (metadata + events). **Primary file.**
- `<Module>.Rmd` / `.md` / `.html` — module manual.
- `R/` — module-local helper functions, sourced into the module during `simInit`.
- `tests/unitTests.R` + `tests/testthat/` — tests (see `spades-module-development`).
- `data/` with `CHECKSUMS.txt`, `citations/`, `citation.bib`, `figures/`, `tables/`.
- `NEWS.md`, `LICENSE`, `README.md`, `<Module>.Rproj`.

## Structure of `<Module>.R`

Everything in the file is sourced during `simInit` into the `simList`. Three parts:

### 1. `defineModule()` metadata

```r
defineModule(sim, list(
  name = "<Module>",
  description = "...",
  keywords = c("..."),
  authors = c(person(...), ...),
  childModules = character(0),
  version = list(`<Module>` = numeric_version("0.0.1")),
  timeframe = as.POSIXlt(c(NA, NA)),
  timeunit = "year",
  citation = list("citation.bib"),
  documentation = list("README.md", "<Module>.Rmd"),
  reqdPkgs = list("data.table", "reproducible", "SpaDES.core", "SpaDES.tools"),
  parameters = rbind(
    defineParameter("someParam", "logical", FALSE, NA, NA, desc = "..."),
    defineParameter(".plotInitialTime", "numeric", NA, NA, NA, desc = "..."),
    defineParameter(".plotInterval", "numeric", NA, NA, NA, desc = "...")
  ),
  inputObjects = bindrows(
    expectsInput("someInput", "data.table", desc = "...", sourceURL = "")
  ),
  outputObjects = bindrows(
    createsOutput("someOutput", "data.table", desc = "...")
  )
))
```

- **Parameters** with names starting `.` are SpaDES housekeeping (`.plotInitialTime`,
  `.plotInterval`, `.saveInitialTime`, `.useParallel`, `.plots`). Keep `min`/`max` as `NA`
  when not numeric.
- **`reqdPkgs`** may pin GitHub packages with `User/repo@branch (>= version)`.
- Every `expectsInput`/`createsOutput` needs a `desc`; keep object names consistent
  across modules so chains connect (one module's `createsOutput` is another's
  `expectsInput`).

### 2. `.inputObjects` function (optional)

Defines default/derived inputs when the user (or another module) does not supply them; runs during `simInit`.
Use `reproducible::Cache()` and `prepInputs()` for expensive data prep. Guard with
`suppliedElsewhere("objName", sim)` to avoid recomputing supplied inputs. Retrieve the
URL declared in an input's `sourceURL` metadata with `extractURL("objName", sim)`, and
pass it to functions like `prepInputs()` to download and prepare the data.

### 3. `doEvent.<Module>()` dispatcher

```r
doEvent.`<Module>` <- function(sim, eventTime, eventType, debug = FALSE) {
  switch(eventType,
    init = {
      sim <- Init(sim)
      sim <- scheduleEvent(sim, P(sim)$.plotInitialTime, "<Module>", "plot", .last())
      sim <- scheduleEvent(sim, start(sim), "<Module>", "someRecurringEvent", 6)
    },
    someRecurringEvent = {
      sim <- SomeRecurringEvent(sim)
      sim <- scheduleEvent(sim, time(sim) + P(sim)$someTimestep,
                           "<Module>", "someRecurringEvent", 6)
    },
    plot = { ... },
    save = { ... }
  )
  return(invisible(sim))
}
```

- `init` typically calls an `Init(sim)` function then schedules recurring events.
- Recurring events reschedule themselves at `time(sim) + interval`.
- Numeric `eventPriority` orders same-time events (lower runs first); modules often define
  explicit priority variables at the top of `doEvent`.
- Read/write params via `P(sim)$x` and `params(sim)$<Module>$x`.

### Event/Init helper functions

Below `doEvent`, the file defines `Init()`, per-event functions, and small helpers. In
tests, access them as `sim$.mods$<Module>$<fn>` when they are not exported.

## Editing conventions

- When adding an input/output, update **both** the metadata block and the code that
  reads/writes it, plus the module `.Rmd` and `data/CHECKSUMS.txt` if a data file changes.
- Bump `version` in the metadata and add a `NEWS.md` entry for behavioral changes.
- Use `newModule()` from `SpaDES.project`/`SpaDES.core` to scaffold a brand-new module.
- For coding style and dependency preferences (e.g. `data.table`, base pipe `|>`), see
  `spades-module-development`.
