# SpaDES toolkit cheat-sheet

The SpaDES packages live at `~/GitHub/SpaDES/*` and are documented at
https://spades.predictiveecology.org/. This is a quick reference; defer to the package
docs for detail.

## SpaDES.core — the simulation framework

The `simList` is the central object (an environment holding objects, params, the event
queue, and module functions).

- `simInit(times, params, modules, objects, paths)` — construct a `simList`; loads
  modules, runs `.inputObjects`, resolves dependencies.
- `spades(sim, debug = FALSE)` — run events to the end time; returns the `simList`.
- `defineModule(sim, list(...))` — module metadata (name, version, timeunit, reqdPkgs,
  parameters, inputObjects, outputObjects, documentation, citation).
- `defineParameter(name, class, default, min, max, desc)` — declare a parameter.
- `expectsInput(objectName, objectClass, desc, sourceURL)` — declare an input object.
- `createsOutput(objectName, objectClass, desc)` — declare an output object.
- `scheduleEvent(sim, eventTime, moduleName, eventType, eventPriority)` — queue an event.
- `P(sim)` / `params(sim)$<Module>` — read/write module parameters.
- `mod` and `sim$.mods$<Module>$<fn>` — access module-local objects/functions.
- Accessors: `time(sim)`, `start(sim)`, `end(sim)`, `events(sim)`, `objs(sim)`.

## reproducible — caching and data prep

- `Cache(fn, ...)` — memoize a call by digest of its inputs; skip recompute if unchanged.
- `prepInputs(url, targetFile, fun, ...)` — download + checksum + post-process a dataset.
- `preProcess()`, `postProcess()` — the download and spatial post-processing halves.

## Require — reproducible package management

- `Require("pkg (>= x.y)")`, `Require("GitHubUser/repo@branch")` — install + load with
  version constraints. `pkgSnapshot()`, `setLibPaths()`.

## SpaDES.tools — spatial algorithms

- `spread()`, `spread2()`, `spread3()` — spatial spreading (fire, disease).
- `neighbourhood()`, `splitRaster()`, `mergeRaster()`, `distanceFromEachPoint()`.

## Other packages

- `quickPlot` — `Plot()`, `clearPlot()`: fast modular grid-based plotting.
- `SpaDES.project` — `newProject()`, `newModule()`: scaffolding.
- `SpaDES.experiment` — `experiment()`, `simInitAndExperiment()`: parameter sweeps,
  replicates, `simLists`.
- `SpaDES.config` — R6 project configuration.
- `pemisc` — miscellaneous Predictive Ecology helpers.
