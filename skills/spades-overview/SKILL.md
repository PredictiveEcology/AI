---
name: spades-overview
description: Orientation and routing for the SpaDES toolkit — the R packages that implement Spatial Discrete Event System (SpaDES.core, SpaDES.tools, reproducible, Require, SpaDES.project, quickPlot, and companions). Use when starting work in a SpaDES toolkit workspace, when the user mentions SpaDES, a simList, modules, or the toolkit packages, or asks how the toolkit fits together and which other spades-* skill applies.
metadata:
  ecosystem: SpaDES
  version: "1.0"
---

# SpaDES toolkit overview

SpaDES ("Spatial Discrete Event System") is a set of R packages for building and
running spatial simulations from independent, composable **modules**. This is the
*toolkit* — the framework and its supporting packages — not a particular model. Model
systems (e.g. LandR, for forest landscapes) are built *on top of* the toolkit and supply
their own modules and skills. Toolkit docs: https://spades.predictiveecology.org/.

A SpaDES toolkit workspace is typically a folder holding many independent package repos
side by side (not one git repo). Confirm the actual set present rather than assuming one.

## Mental model (SpaDES in one paragraph)

A simulation is a `simList` object built by `simInit()` and run by `spades()`. Each
**module** declares metadata via `defineModule()` (parameters, expected inputs, created
outputs) and schedules **events** with `scheduleEvent()`, handled by a
`doEvent.<Module>()` dispatcher. The overall event sequence is **not** defined centrally —
it emerges bottom-up from the modules assembled and the events each schedules. Modules
communicate only through named objects in the `simList` (one module's `createsOutput` is
another's `expectsInput`), which is what makes multi-module workflows composable. Expensive
or downloaded data steps use `reproducible::Cache()` and `reproducible::prepInputs()`.

## The packages

See [references/spades-toolkit.md](references/spades-toolkit.md) for the package/function
cheat-sheet. In brief:

- **`SpaDES.core`** — the framework: `simInit()`, `spades()`, `defineModule()`, events,
  parameters, and `simList` accessors.
- **`SpaDES.tools`** — spatial algorithms (`spread()`/`spread2()`, neighbourhoods, raster
  split/merge).
- **`reproducible`** — `Cache()` and `prepInputs()` for reproducible caching and data prep.
- **`Require`** — reproducible, version/branch-aware package install and load.
- **`SpaDES.project`** — scaffolding and whole-project setup (`newModule()`,
  `newProject()`, `setupProject()`); also holds the parameter-sweep/replicate capabilities
  formerly in the deprecated `SpaDES.experiment`.
- **`quickPlot`** — fast modular plotting (`Plot()`, `clearPlot()`).
- Companions: `SpaDES` (meta-package), `SpaDES.config`, `SpaDES.addins`, `SpaDES.install`,
  `SpaDES.docs`, and accessory helpers such as `pemisc`.

## Which skill to use

| Task | Skill |
|---|---|
| Build, run, refactor, or debug a module or simulation; code against the toolkit | `spades-module-development` |
| Understand or edit a module's `.R` structure, metadata, or events | `spades-module-anatomy` |
| Develop or maintain the SpaDES toolkit packages themselves (APIs, NAMESPACE, devtools, versioning) | `spades-package-development` |
| Write unit or integration tests | `spades-testing` |
| Write comments, module metadata `desc` fields, roxygen2, NEWS | `spades-code-documentation` |
| Author a per-module `.Rmd` manual | `spades-module-manuals` |

Always prefer inspecting the actual files (module `.R`, `DESCRIPTION`, `tests/`) and the
real function definitions before acting — the toolkit is large and evolves across versions.
