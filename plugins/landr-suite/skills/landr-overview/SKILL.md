---
name: landr-overview
description: Orientation and routing for the LandR ecosystem of SpaDES modules and accessory R packages (forest and forest-disturbance simulation at landscape scales). Use when starting work in ~/GitHub/LandR, when the user mentions LandR, Biomass_ modules, fireSense modules, SpaDES modules, or asks how the ecosystem fits together and which other skill applies.
metadata:
  ecosystem: LandR
  version: "1.0"
---

# LandR ecosystem overview

LandR is a suite of `SpaDES` modules plus accessory R packages that simulate forest
vegetation succession, disturbances (wildfire, climate change, insects), and carbon at
large landscape scales. The project folder is `~/GitHub/LandR` — a collection of many
independent module and package folders side by side (not one git repo). The SpaDES
toolkit lives at `~/GitHub/SpaDES/*` and is documented at
https://spades.predictiveecology.org/.

Read the ecosystem's own manual at `~/GitHub/LandR/LandR-Manual/` (start with
`index.Rmd`) for model basics.

## Mental model (SpaDES in one paragraph)

A simulation is a `simList` object built by `simInit()` and run by `spades()`. Each
**module** declares metadata via `defineModule()` (parameters, expected inputs, created
outputs) and schedules **events** with `scheduleEvent()`, handled by a
`doEvent.<Module>()` dispatcher. Modules communicate only through named objects in the
`simList` (one module's `createsOutput` is another's `expectsInput`), which is what makes
multi-module workflows composable. Expensive data steps use `reproducible::Cache()` and
`reproducible::prepInputs()`.

## Module families

See [references/module-families.md](references/module-families.md) for the catalog. In
brief: `Biomass_*` (vegetation succession, flagship `Biomass_core`), `fireSense_*` (fire
modelling as fit/predict pairs), and carbon modules (`LandR_CBM`, `LandRCBM*`, `LandRCSAM`).

## Accessory packages

- `LandR/` — core utilities (cohort data, species/ecoregion tables, layer loaders,
  assertions, maps). Imports `SpaDES.core`, `SpaDES.tools`.
- `LandR.CS/` — climate-sensitive growth/mortality (`calculateClimateEffect`).
- `fireSenseUtils/` — fire data extraction, DEoptim optimization, helpers.

## SpaDES toolkit

See [references/spades-toolkit.md](references/spades-toolkit.md) for the package/function
cheat-sheet (`SpaDES.core`, `SpaDES.tools`, `reproducible`, `Require`, `quickPlot`,
`SpaDES.project`, `SpaDES.experiment`, `SpaDES.config`, `pemisc`).

## Which skill to use

The SpaDES `spades-*` skills below come from the sister repo `SpaDES.ai` and are used
**by default** in LandR work (obtained alongside the LandR skills).

| Task | Skill |
|---|---|
| Implement/change a simulation **process** in a module's code (growth, mortality, dispersal, fire, carbon) | `landr-code-development` |
| SpaDES mental model / toolkit orientation (which `spades-*` skill applies) | `spades-overview` |
| Understand/edit a module's `.R` structure, metadata, events | `spades-module-anatomy` |
| Build, run, or debug a module or simulation (`simInit()`/`spades()`, `newModule()`) | `spades-module-development` |
| Write unit or integration tests | `testing` |
| Find an existing module, or work out whether a set of modules fits together | `spades-finding-modules` |
| A module's CI is red, or you are preparing a module PR | `spades-module-ci` |
| Run replicates, compare scenarios, sweep parameters, or test whether a change alters results | `spades-experiments` |
| Maintain LandR/LandR.CS/fireSenseUtils packages (NAMESPACE, devtools, versioning) | `landr-package-maintenance` |
| Author LandR module `.Rmd` manuals or multi-module bookdown manuals | `landr-manuals` |
| Author a SpaDES module's own `.Rmd` manual | `spades-module-manuals` *(placeholder — until written, use `landr-manuals`)* |
| Write comments, module metadata `desc` fields, roxygen2, NEWS | `code-documentation` |

Always prefer inspecting the actual files (module `.R`, `DESCRIPTION`, `tests/`) before
acting — the ecosystem is large and modules vary.
