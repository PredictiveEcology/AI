---
name: spades-module-development
description: Developing SpaDES toolkit modules and simulations in general (not LandR-specific) — scaffolding a new module with newModule(), writing defineModule metadata and event code, coding against the SpaDES toolkit (SpaDES.core, SpaDES.tools, reproducible, Require, SpaDES.project), running and debugging a simList with simInit()/spades(), composing modules through simList objects, deciding where code belongs (module vs package), reusing existing functions, managing dependencies, and writing memory-efficient R. Use when the user asks to create, develop, run, refactor, or debug a SpaDES module or simulation. For the module .R structure/metadata use spades-module-anatomy; for developing the SpaDES packages themselves use spades-package-development.
metadata:
  ecosystem: SpaDES
  version: "1.1"
---

# SpaDES module development

General guidance for building and running SpaDES modules and simulations, independent of
any particular model family. SpaDES ("Spatial Discrete Event System") composes
independent **modules** into a simulation whose event sequence emerges bottom-up from the
modules assembled — there is no central controller.

Scope boundaries:
- For the **anatomy** of a module `.R` file (defineModule metadata, doEvent dispatcher,
  event functions), use `spades-module-anatomy`.
- For a model system built on the SpaDES toolkit (e.g. **LandR**), that system may
  supply its own skills; see its documentation. This skill stays toolkit-general.
- This skill covers the **general development workflow** and coding against the toolkit.

## The mental model

A simulation is a `simList` — an environment holding objects, parameters, the event
queue, and each module's functions. `simInit()` builds it (loading modules, running their
`.inputObjects`, resolving dependencies); `spades()` runs scheduled events to the end
time and returns the `simList`. Modules communicate **only through named objects in the
`simList`**: one module's `createsOutput` is another's `expectsInput`.

## The toolkit you code against

Ground all module code in the SpaDES toolkit (see documentation at
https://spades.predictiveecology.org/ and within SpaDES packages). Before using a toolkit function, check its actual
definition (its help page, `args()`, or source) rather than relying on remembered argument
names — the toolkit's functions change across versions.

- **`SpaDES.core`** — the framework: `simInit()`, `spades()`, `defineModule()`,
  `defineParameter()`, `expectsInput()`/`createsOutput()`, `scheduleEvent()`, `P(sim)` /
  `params(sim)`, `mod`, and accessors `time()`/`start()`/`end()`/`events()`/`objs()`.
- **`SpaDES.tools`** — spatial algorithms: `spread()`/`spread2()`, `neighbourhood()`,
  `splitRaster()`/`mergeRaster()`; and more.
- **`reproducible`** — `Cache()` for memoizing expensive calls; `prepInputs()`
  (`preProcess()`/`postProcess()`) for downloading and preparing external data reproducibly.
- **`Require`** — reproducible package installation/loading with version and GitHub constraints.
- **`SpaDES.project`** — scaffolding and whole-project setup: `newModule()`,
  `newProject()`, `setupProject()`; also holds the parameter-sweep/replicate capabilities
  formerly in the deprecated `SpaDES.experiment`.
- **`SpaDES.experiment`** — *deprecated*: its parameter sweeps, replicates, and
  multiple-`simList` capabilities have moved to `SpaDES.project`.
- **`quickPlot`** — fast modular plotting (`Plot()`, `clearPlot()`).

## Developing a new module

1. **Scaffold** with `SpaDES.project::newModule("<Name>", path)` — creates the module
   folder, `.R` skeleton, `.Rmd` manual, `tests/`, and `data/CHECKSUMS.txt`.
2. **Declare the module's interface first** — its inputs, outputs, and parameters, i.e.
   its contract with other modules — in `defineModule()`: `timeunit`, `reqdPkgs` (pin
   versions/branches), and the `parameters`/`inputObjects`/`outputObjects`. Design the
   inputs and outputs before the logic.
3. **Write the events**: the `init` event is mandatory, it initializes state and schedules future events;
   recurring events reschedule themselves at `time(sim) + interval`. Keep the actual
   simulation computations in named event/helper functions, not inline in the dispatcher.
4. **Always aim to provide sensible defaults** in `.inputObjects`;
   guard with `suppliedElsewhere("obj", sim)` so supplied objects are not overwritten; retrieve an input's declared online (default) source with `extractURL("obj", sim)` (reading its `sourceURL` metadata) and pass it to `prepInputs()` for reproducible download/prep.
5. **Document** parameters and every input/output `desc`, and build/update the module `.Rmd`. Also fill in the module description and keywords.

## Running and debugging a simulation

- Minimal build and run:
  ```r
  sim <- simInit(times = list(start = 0, end = 10), params = list(...),
                 modules = "<Name>", paths = list(...))
  sim <- spades(sim)
  ```
  For multi-module or whole-project runs, `SpaDES.project::setupProject()` prepares
  modules, packages, paths, and params to pass to `simInit()`/`spades()`.
- **Debug** with `spades(sim, debug = TRUE)` (traces events) and inspect the queue with
  `events(sim)` / `completed(sim)`; read/write objects via `sim$objName` and params via
  `P(sim)$x`.
- Return `invisible(sim)` from event functions to avoid printing the large `simList`.

## Coding conventions

- **Use `data.table` and the base pipe.** Favor `data.table` over `data.frame`/`tibble`
  for performance and memory at landscape scale, and the base pipe `|>` over the magrittr
  `%>%` (to decrease the number of packages needed). Match the conventions and dependencies
  already in the module/project you are working in.
- Read/write parameters via `P(sim)$x` (respects `params(sim)` overrides), state via
  `sim$objName`; keep module-local persistent state in `mod`.
- Use `reproducible::Cache()`/`prepInputs()` and related functions for expensive or downloaded steps; be
  deliberate about caching stochastic events (generally do not cache them). Note that `prepInputs()` does not cache internally and needs to be combined with `Cache()`.
- Order same-time-step events with numeric `eventPriority` (lower runs first).
- **For complex event scheduling**, a module can define explicit `eventPriority`
  variables at the top of `doEvent` and reference them in `scheduleEvent()` — clearer and
  more maintainable than scattering magic numbers. Example: `Biomass_core` defines
  `dispEvtPriority`, `GMEvtPriority`, etc.
  (https://github.com/PredictiveEcology/Biomass_core).
- Match the timestep: recurring-event intervals and per-step rates must be consistent with
  the module's `timeunit`.

## Memory-efficient coding

Landscape simulations are memory-bound, and some common R idioms leak memory by silently
capturing large environments. Prefer the following:

- **Avoid `Map()`, `do.call()`, and the `apply` family** (`sapply`/`lapply`/`mapply`/
  `apply`) — they are less memory-efficient and can leak memory, especially with
  undeclared (anonymous/inline) functions. **Use the `purrr` family instead** (`map()`,
  `map2()`, `pmap()`, `walk()`, and their typed variants).
- **Avoid `as.formula()`** — it captures its calling environment, dragging every object in
  that environment into memory. Prefer building a `call` (e.g. `call()`/`bquote()`) when a
  formula-like expression is needed.
- **Declare functions in a package or the module's `R/` folder, not inline in a large
  scope.** A closure keeps a reference to its defining environment, so a function defined
  in a large environment (e.g. a bloated `.GlobalEnv` mid-run) carries all of it into
  memory — a classic leak. Functions in `R/` or a package are sourced early, before the
  environment grows large (especially when using `setupProject()` and keeping `.GlobalEnv`
  clean); this keeps closures lean and makes the functions reusable (see "Reuse and
  dependencies").

## Interacting with other modules

- An object name in the `simList` is a **contract**: renaming or changing the
  type/shape of a shared object can break downstream modules that `expectsInput` it.
- Update both the metadata (`expectsInput`/`createsOutput`) and the code that reads/writes
  the object; confirm intended data flow with the user before rewiring a cross-module
  process.
- **Parameters and module functions are module-scoped; shared `simList` objects are
  global.** A module's parameters are visible only within that module, except those passed
  as **`.globals`** (set via `simInit(..., params = list(.globals = list(...)))`), which
  are shared across modules. A module's functions — whether defined in its `.R` script or
  its `R/` folder — are likewise available only to that module. By contrast, the objects a
  module declares through `expectsInput`/`createsOutput` live in the shared `simList` and
  can be read or written by any module.

## Change propagation and code placement

Modules and their supporting packages form an interdependent web. Before and after any
change, reason about how it ripples outward.

- **Trace propagation of every change** across three boundaries: within the module, across
  modules (via shared `simList` objects), and between modules and the packages they depend
  on. A change to a package function affects every module and script that calls it; a
  change to a shared object affects every module that consumes it.
- **Prompt the user to run integration tests periodically** — both *within* a
  module/package (unit tests) and *across* modules/packages (integration tests) — not only
  at the end. Surface this after changes that cross a boundary.
- **Evaluate where a change best belongs** -- Ask whether code should live in the **module**
  (specific to that module's behavior) or in a **package** (shared logic used across many
  modules/scripts/locations), or if it needs to be propagated across multiple places.
  If a function or code change is, or is likely to be, used/necessary in more than one
  place, prefer putting it in a package so there is a single source of truth rather than
  duplicated module-local copies. The user may not be aware of this (e.g., novice users, or users that maintain a smaller subset of modules/packages) — prompt them to consider it, evaluate where changes should be propagated to, justify why and verify with user before implementation.

## Reuse and dependencies

- **Check for existing functions before writing new ones** — Search, in order: the current
  module, other modules, the project's/related packages, then CRAN packages. Reuse or
  extend what exists rather than reimplementing it.
- **Avoid introducing new package dependencies** — in both modules (`reqdPkgs`) and
  packages (`DESCRIPTION`) — unless genuinely necessary. A new dependency is a long-term
  reproducibility and maintenance cost.
- **Flag any new dependency to the user before adding it**, with the reason it is needed
  and whether an existing dependency could serve instead.

## Testing

Scaffold `tests/` include `unitTests.R` + `testthat/`; build small in-memory inputs, call
`simInit()`/`spades()` (or a helper directly via `sim$.mods$<Module>$<fn>`), and assert on
the returned `simList`. See `spades-testing` for patterns.

<!--Note to Ceres: request input from Eliot and Alex.-->
