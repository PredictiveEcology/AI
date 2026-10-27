# SpaDES toolkit cheat-sheet

A quick reference to the SpaDES toolkit packages and their key functions. Defer to the
package docs (https://spades.predictiveecology.org/) and the real function definitions for
detail — the toolkit evolves across versions.

## SpaDES.core — the simulation framework

The `simList` is the central object (an environment holding objects, params, the event
queue, and module functions).

- `simInit(times, params, modules, objects, paths)` — construct a `simList`; loads
  modules, runs `.inputObjects`, resolves dependencies.
- `spades(sim, debug = getOption("spades.debug"))` — run events to the end time; returns
  the `simList`. The option defaults to `1`, which prints one line per event.
- `defineModule(sim, list(...))` — module metadata (name, version, timeunit, reqdPkgs,
  parameters, inputObjects, outputObjects, documentation, citation).
- `defineParameter(name, class, default, min, max, desc)` — declare a parameter.
- `expectsInput(objectName, objectClass, desc, sourceURL)` — declare an input object.
- `createsOutput(objectName, objectClass, desc)` — declare an output object.
- `scheduleEvent(sim, eventTime, moduleName, eventType, eventPriority)` — queue an event.
- `suppliedElsewhere("obj", sim)` — in `.inputObjects`, test whether an input object is
  already supplied (by another module or the user) so a default is only built when needed.
- `sourceURL` — the `expectsInput()` metadata field giving an input's default online
  source; retrieve it with `extractURL(objectName, sim)` and pass it to `prepInputs()` for
  reproducible download.
- `P(sim)` / `params(sim)$<Module>` — read/write module parameters; `.globals` are shared
  across modules.
- `mod` and `sim$.mods$<Module>$<fn>` — access module-local objects/functions.
- Accessors: `time(sim)`, `start(sim)`, `end(sim)`, `events(sim)`, `completed(sim)`,
  `objs(sim)`.

## reproducible — caching and data prep

- `Cache(fn, ...)` — memoize a call by digest of its inputs; skip recompute if unchanged.
- `prepInputs(targetFile, url, archive, ..., fun, ...)` — download + checksum +
  post-process a dataset. Caches internally up to two levels (`useCache = 2`: the
  download/load steps), but not `postProcess()`; wrap the whole call in `Cache()` to
  cache all of it.
- `preProcess()`, `postProcess()` — the download and spatial post-processing halves.

## Require — reproducible package management

- `Require("pkg (>= x.y)")`, `Require("GitHubUser/repo@branch")` — install + load with
  version constraints. `pkgSnapshot()`, `setLibPaths()`.

## SpaDES.tools — spatial algorithms

- `spread()`, `spread2()`, `spread3()` — spatial spreading (fire, disease, dispersal).
- `adj()`, `rings()`, `cir()` (neighbourhoods), `splitRaster()`, `mergeRaster()`,
  `distanceFromEachPoint()`.

## SpaDES.project — project setup

- `newModule()`, `newProject()` are in **SpaDES.core**, not here.
- `setupProject()` — set up a whole project (download modules, install packages, prepare
  paths/params) and return objects ready for `simInit()`/`spades()`.
- Also holds parameter-sweep/replicate/`simList`-experiment capabilities formerly in the
  archived `SpaDES.experiment`.

## Other packages

- `quickPlot` — `Plot()`, `clearPlot()`: fast modular grid-based plotting.
- `SpaDES` — meta-package tying the toolkit together.
- `SpaDES.config` — project configuration.
- `SpaDES.docs` — documentation helpers (e.g. `prepManualRmds()` for LandR-Manual).
- Legacy: `SpaDES.install` (superseded by `setupProject()`), `SpaDES.addins`, `pemisc`
  (no code changes since 2022).