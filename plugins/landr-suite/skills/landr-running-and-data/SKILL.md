---
name: landr-running-and-data
description: Running LandR vegetation workflows (Biomass_speciesData, Biomass_borealDataPrep, Biomass_speciesParameters, Biomass_speciesFactorial, Biomass_regeneration, Biomass_core) and choosing their data. Covers dataYear and SCANFI years, the simInit error when modules disagree on dataYear or sppEquivCol, pairing vegetation years with fire or climate years, land cover and forest land (class 240, forestLandFrom, the FAO layer and its cost), species equivalence, running Biomass_borealDataPrep nested inside another module, running with unmerged fixes through an integration branch, and what long runs cost. Use when setting up or debugging a LandR run, picking data years, a run stops at simInit with a parameter mismatch, data prep is slow, or results change after a module update. For changing Biomass_core cohort or establishment rules use biomass-core-cohort-rules; for module code use landr-code-development.
metadata:
  ecosystem: LandR
  version: "0.1"
---

# Running LandR and choosing its data

This skill is for people who run the `Biomass_*` modules. It does not repeat the module
map (`landr-overview`) or the coding rules (`landr-code-development`). Read the module's
`defineModule()` parameter descriptions before trusting anything here: they are the
current truth, and the line numbers below drift.

## dataYear: one value for every module

Several modules declare a `dataYear` parameter: `Biomass_speciesData`,
`Biomass_borealDataPrep`, `Biomass_core`, and outside the Biomass family also
`fireSense_dataPrepPredict` and `burnSummaries`. They all default to 2020.

- **Symptom:** `simInit()` stops with a `paramCheckOtherMods` error naming `dataYear`.
  **Cause:** you set `dataYear` for one module only, or with different values, or one
  module in the project has a different default (one fire module defaulted to 2011
  until late 2026). **Fix:**
  set it once, for all of them, in `params$.globals`:
  `params = list(.globals = list(dataYear = 2015))`, which sets each module's own
  parameter of that name.
- The check is an error only in recent module versions. Older versions warn
  (`Biomass_borealDataPrep`) or say nothing, and then each module quietly reads a
  different year. If you mix old and new module versions in one `modulePath`, a run that
  used to work can start stopping at `simInit()`. Update all of them together, or none.
- The same check, as an error, covers `sppEquivCol`, `vegLeadingProportion`,
  `cohortDefinitionCols` and (in `Biomass_core`) `initialB`. Set these through
  `.globals` too.
- The check compares with `identical()`, so `2020L` (integer) and `2020` (numeric)
  differ. The error then lists "2020, 2020", which looks like a bug in the check. Look
  for an integer default in one module. Pass numerics.

SCANFI years: V1 has 2000, 2010, 2020; V2 has 1985 to 2025 in steps of 5
(`LandR:::.scanfi_v2_years`). `LandR::prepRawBiomassMap()` stops on a year the source
does not provide, so 1987 is an error, not the nearest year. Details and the history of
older year checks: [references/data-years.md](references/data-years.md).

## Vegetation year versus fire and climate year

A SCANFI layer for year Y is made from imagery of year Y, so it already shows the burns
of year Y. Pair it with fires and climate of year Y + 1, not of year Y.

- To relate vegetation to fire (fitting, validation, hindcasts): for each fire year use
  the latest vegetation data year **strictly before** it. With data years from 1985, the
  first usable fire year is 1986. `fireSenseUtils::dataYearBefore()` implements this.
- To start a simulation at year T: use the latest data year **not after** T
  (`fireSenseUtils::dataYearFor()`). The simulation then makes its own vegetation.
- A climate series must cover the fire years, not the vegetation years. A run with
  vegetation from 1985 needs climate from 1986.

This is a convention adopted after an information leak, not a property of the code.
Using same-year vegetation and fire lets a model "predict" fires that the vegetation map
has already recorded.

## Land cover and forest land

- **Class 240** in the LandR land cover means "forest land that is currently not
  treed": a pixel in the FAO forest layer, or treed in another land-cover year, that is
  not treed in `dataYear`. `Biomass_borealDataPrep` fills those pixels with a forest
  type by nearest neighbour (`LCCClassesToReplaceNN = 240`).
- **`forestLandFrom`** (`LandR::prepInputs_SCANFI_LCC_FAO()`,
  `prepInputs_NTEMS_LCC_FAO()`) defaults to `"both"`: the FAO forest layer **and** the
  land cover of every `forestLandYears` year. Nobody tuned that default for any workflow.
  `"fao"` or `"lccYears"` alone is far cheaper. Compare the land cover each choice gives
  on your study area before changing it.
- **Cost:** measured on one study area, each call took about 27 minutes (FAO crop and
  project about 12 minutes, the other years' land cover about 11). A workflow that calls
  it once per data year paid that five times for the same answer. LandR now caches each
  input on the study area's geometry, but only when caching is on. If your run turns
  `reproducible` caching off (for example `spades.useCache = "eventsOnly"`), set
  `options(LandR.forestLandUseCache = "always")` or the work repeats on every call.
- **Land cover can change during a run.** A land-use or harvest module may change it.
  Do not compute anything once per run from land cover and reuse it across years
  unless the reuse is keyed on the land cover actually passed in.

More on class 240, wetlands, and the deciduous cover weight:
[references/land-cover.md](references/land-cover.md).

## Species

- `sppEquiv` is the table that maps species names between data sources; help is at
  `?sppEquivalencies_CA` (alias `?sppEquiv`). `sppEquivCol` picks the naming column
  (default `"LandR"`). It must be the same in every module.
- `options(LandR.mergeHybridSpruce = ...)` decides where hybrid white x Engelmann spruce
  goes: `"engelmann"` (default), `"white"`, or `NA` (keep separate). It changes which
  species exist in the run.
- `Biomass_speciesData` with its default `types = "SCANFI"` does the same work as
  `Biomass_borealDataPrep`'s own SCANFI fallback. You can leave it out of a project. Use a
  `Biomass_borealDataPrep` recent enough to handle a study area with no tree species
  (it used to error in `NAcover2zero(NULL)`).
- `Biomass_speciesParameters` with `PSPdataTypes = "all"` needs permission to restricted
  provincial plot data. `"dummy"` or the public sets (`c("BC", "NB", "QC", "NFI")`) do
  not.

## Biomass_borealDataPrep run inside another module

Some modules (for example `fireSense_dataPrepFit`) build `cohortData` for several data
years by running `Biomass_borealDataPrep` in a nested `simInitAndSpades()`, once per
year, with the parent's parameters and `dataYear` replaced.

- The nested module's code is read when each nested `simInit()` runs, not when the
  outer run starts. Editing or checking out `Biomass_borealDataPrep` while an outer run
  is between data years gives that run mixed code. Change module folders only when no
  run is in data prep.
- The nested runs are cached on their inputs and a digest of the module code. Changing
  the module's code reruns every data year.
- If the module is not in your `modulePath`, the parent may download its
  `@development` head into a `submodules` folder, which is not the version you pinned.

## Running with fixes that are not merged yet

LandR changes often wait for review across many repos. A convention that works:

- For each repo, an integration branch = `development` + the open PR branches you need,
  updated by merging forward. Never force-push it; runs and other people use it.
- Never merge a **draft** PR into it. In one incident a draft merged automatically and
  every run stopped in `Biomass_core` init the next morning.
- An integration branch that is not kept current is worse than none: one was found 38
  commits behind `development` with none of the fixes it existed to carry.
- A module pin such as `Biomass_core@branch` does not re-download a module already in
  `modulePath`. Check the checkout yourself: `git -C modules/<m> log -1` against the
  remote branch head. Package pins have the same trap; see `spades-running-projects`.
- When the PRs merge, point the pins back to `development`.

## What long runs cost

Measured on 1000-year runs of one large landscape:

- `cohortData` grew to about 11 million rows in 467,000 pixel groups; cohorts per pixel
  group rose from about 2 to about 23. Time per simulated year doubled (12 to 25 s);
  `Biomass_core` growth and mortality became the largest per-year cost.
- Saved outputs were 4.5 GB per run, 1.3 GB of it `cohortData` saved every 100 years.

Most of that growth is stacks of suppressed cohorts. Options that limit it are off by
default and change results; see `biomass-core-cohort-rules` before turning one on.

## Before you report a result change

- Say which module versions ran (`git log -1` in each module folder) and which LandR.
- Check `dataYear`, `sppEquivCol` and `successionTimestep` are what you think in
  `params(sim)`, not only in your script.
- For a before/after comparison, follow the `spades-experiments` skill's controlled
  comparison design (frozen start state, same seeds, caching off).
