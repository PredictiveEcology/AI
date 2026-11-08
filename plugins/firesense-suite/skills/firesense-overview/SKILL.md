---
name: firesense-overview
description: Orientation for running the fireSense fire model (SpaDES modules fireSense, fireSense_ELFs, fireSense_dataPrepFit, fireSense_ignitionFit, fireSense_spreadFit, fireSense_dataPrepPredict, fireSense_ignitionPredict, fireSense_spreadPredict, fireSense_burn, fireSense_summary; packages fireSenseUtils, clusters, fireregimetools). Use when setting up or launching a fireSense run, deciding whether a run fits or only predicts (doFit), forcing a refit, working with the spread and ignition fit ledgers (fitFileSuffix, CacheGeo spatial lookup), choosing fire years and fire causes, getting NFDB/NBAC fire data, or stopping and restarting runs. Routes to firesense-spread-fitting and firesense-hindcast-validation.
metadata:
  ecosystem: LandR
  version: "0.1"
---

# fireSense overview

fireSense simulates wildfire inside a SpaDES/LandR simulation. It fits three statistical
models per study area (ignition, escape, spread), stores the fits in shared ledgers, and
then predicts and burns fires every simulated year.

## The module family

List the parent module and you get all nine children:

```r
SpaDES.project::setupProject(
  modules = "PredictiveEcology/fireSense@development",
  ...
)
```

`fireSense` has no events or parameters of its own. Set parameters on the children, by
their own names. A child you list yourself (e.g. `"PredictiveEcology/fireSense_burn@testing"`)
overrides the parent's entry. The burn module used to be called `fireSense`; it is now
`fireSense_burn`, and `fireSense_IgnitionFit`/`SpreadFit`/`IgnitionPredict`/`SpreadPredict`
are now lower camel case (`fireSense_ignitionFit`, ...). Old scripts need their `params`
keys renamed (see the parent's README).

In order:

| Module | Does |
|---|---|
| `fireSense_ELFs` | Builds the fitting units (ELFs: ecoregion polygons with enough fires), merges ELFs with too few fires into a neighbour |
| `fireSense_dataPrepFit` | Fire, vegetation and climate covariates for fitting |
| `fireSense_ignitionFit` | Ignition and escape models (xgboost, Poisson counts) |
| `fireSense_spreadFit` | Spread model (DEoptim on simulated fires) |
| `fireSense_dataPrepPredict` | Covariates for each simulated year |
| `fireSense_ignitionPredict`, `fireSense_spreadPredict` | Expected values and spread probabilities from the stored fits |
| `fireSense_burn` | All random draws (ignitions, escapes, year effects) and the fire spread |
| `fireSense_summary` | Summaries of fits and burns, and the hindcast tables |

The fitting unit is the ELF. A fit is per ELF only: an ELF is the smallest area that
captures large fires and the largest with roughly uniform spread parameters. A study
area that spans several ELFs predicts from each ELF's own fit in its own pixels; it
never fits across ELFs (`fireSense_spreadFit` stops). Some ELFs are never fitted (Arctic,
Prairie grassland, mostly-farmland ones): `fireSenseUtils::ELFsNotFitted()` is the one
list. Do not debug fit failures there.

## Does this run fit, or only predict?

`doFit` (on `fireSense_spreadFit`, `fireSense_ignitionFit`, `fireSense_dataPrepFit`):

| `doFit` | Behaviour |
|---|---|
| `FALSE` (module default) | Never fit. Stops if the ledger has no fit for this ELF, so a prediction run cannot start a multi-hour fit by accident |
| `NA` | Fit only if the ledger has no fit, then predict. The usual setting for a project run |
| `TRUE` | Always fit and replace the ledger row. Needs about 40 cores |

Convention: a run does everything that is required. Set `doFit = NA` so an ELF with no
fit gets fitted and then predicts. Fit-only and inputs-only runs are for campaigns.

`refitExisting` and `stopIfNoPreRunFit` are deprecated aliases of `doFit`.

### Stopping a run part-way (campaign phases)

Use event barriers, not custom flags:

- Inputs only (build every input and cache, 1 CPU): `.stopBefore` the
  `fireSense_spreadFit` `run` event, **and** set `times$end = times$start`. An ELF that
  already has a fit schedules no `run` event, so `.stopBefore` alone lets it run on into
  prediction.
- Fit only: `events = list(.stopAfter = list(fireSense_spreadFit = "run"))`.
- Held-out fold fit: `heldOutFold = 1` (or 2) and `.stopAfter` `crossValidate`.

Never run two jobs on the same ELF at once (for example an inputs job and a fit job).
Output files are named by ELF, not by job, and are written with `overwrite = TRUE`.
terra writes are not atomic, so one job can read the other's half-written raster. The
reproducible cache itself is locked per key and is safe.

## Ledgers: where fits live and how they are found

Each fitted ELF is one row of an `sf` ledger (`fireSenseSpreadParams_...rds`,
`fireSenseIgnitionParams_...rds`) in a shared Google Drive folder, with local copies.
See [references/ledgers-and-refits.md](references/ledgers-and-refits.md).

- **Fit reuse is spatial, not a cache key.** The ledger rows are selected by overlaying
  the study area on the ledger polygons (`reproducible::CacheGeo()`), then matched by ELF
  name. A module or package update does not force a refit. An ELF whose geometry changed
  but kept its name reuses its old fit. Before saying "this update forces refits", check
  what actually keys it.
- **To refit, start a new ledger.** Set a new `fitFileSuffix` for all the fit modules at
  once: `params = list(.globals = list(fitFileSuffix = "_myChange20261107"))`. A refit
  almost always means the algorithm or the data changed, so every old row is stale; a new
  ledger says so and stops old rows being reused by accident. `doFit = TRUE` is for one
  ELF, not for a campaign.
- Changing any of these needs a new suffix: the fire causes, the fire years, the spread
  objective or link, `wholeLandscapeSpread`, the covariates.
- One `fitFileSuffix` names both the spread and the ignition ledger, so a new spread
  suffix also refits ignition.

## Fire data, causes and years

- **Fire data comes from `fireregimetools`** (`fetch_nfdb_points()`, `fetch_nfdb_polys()`,
  `fetch_nbac_polys()` and the `load_*()` loaders). The `getFirePoints_NFDB*` functions in
  fireSenseUtils and scfmutils are the legacy it replaces: migrate callers, do not patch
  those. Its `min_size_ha` default is 1; use 0 for ignitions.
- **Causes.** `fireCauses` (default `c("natural", "unknown")`) sets the fires all three
  models use. `fireSenseUtils::fireCauseCodes()` is the one map from groups to NFDB
  `CAUSE` (N, L, U, H, ...) and NBAC `FIRECAUS` (Natural, Undetermined, Human) values.
  Human-caused fires are left out because the model has no suppression or access
  covariate. The modules check that their `fireCauses` agree.
- **Years.** `fireSenseUtils::defaultFireYears()` is 1986 to the latest year with
  historical climate. A fire year is fitted against the latest vegetation year strictly
  before it, because a year's land-cover map already shows that year's burns. Never
  hard-code the end year: it moves every year.
- **No time as a model input.** No year, trend or era covariate in any of the models,
  including tests and variants. The models forecast under future climate, and a time term
  cannot be extrapolated. Temporal trends may be reported after the fact, labelled as not
  a model term.

## Paths

- `inputPath` should vary by ELF only, not by replicate, GCM or SSP. Prepared inputs'
  cache keys include the destination folder as text, so a per-replicate input folder
  re-ran the input preparation for every replicate (about 60 h of repeated work, measured).
- Put the ledger suffix in a fit job's `outputPath`. Fits of one ELF under two suffixes
  otherwise write the same DEoptim progress file.

## Stopping and restarting

Stopping a fit is cheap. Every DEoptim generation is cached, so a relaunch on the same
ledger suffix replays the cached generations in minutes and continues. Do not wait for a
fit to end before installing a package fix: stop it, install, relaunch. Kill the job's
whole process tree by PID (DEoptim workers and forks outlive a killed parent), never by a
command-line pattern.

## Where next

| Task | Skill |
|---|---|
| Spread objective, DEoptim, links, bounds, compute for fits | `firesense-spread-fitting` |
| Hindcasts, scoring against observed fire, reporting results | `firesense-hindcast-validation` |
| Ignition and escape models and their draws | [references/ignition-escape-burn.md](references/ignition-escape-burn.md) |
| Running many jobs (queues, replicates, Slurm) | `spades-experiments` |
| Cache keys of module events | `spades-module-caching` |
