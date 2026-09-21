# Cohort semantics: ages, pixel groups, and the leading-proportion options

Precise behaviour behind the `cohortData` / `pixelGroupMap` rules in the main skill.
These are the details that decide whether a change to cohort handling does anything at
all, and they are easy to get wrong from first principles.

## How old is a new cohort?

Two different answers, and the difference matters.

**Regeneration during succession.** `Biomass_core` creates cohorts at
`age = successionTimestep + 1`, and `ageReclassification()` then sets *every* cohort
with `age <= successionTimestep + 1` to that same value
(`Biomass_core/R/age-cohorts.R:45-75`), squashing duplicates by species within a pixel
group. With the usual `successionTimestep = 10`, new cohorts appear at age 11 and age
annually from there. This is the LANDIS-II behaviour that stops an explosion of age-1
cohorts.

**After disturbance.** `LandR::addCohorts()` sets `age := 1L` for post-disturbance
cohorts (`LandR/R/cohorts.R:83`).

The consequence is the part people miss: **in an undisturbed run, no cohort is ever
younger than `successionTimestep`.** Code that acts only on younger cohorts has nothing
to act on. Disturbance is what creates them.

And one step further: stand-replacing disturbance (`Biomass_regeneration`) leaves no
survivors, so a burned pixel's new age-1 cohorts sit in a pixel group by themselves.
Mixed-age pixel groups — young and old cohorts together — come from **partial**
mortality (`Biomass_regenerationPM`). Any rule about how cohorts of different ages
interact within a pixel group is exercised only in that case.

When testing a change to cohort handling, say which of these three situations it acts
in before measuring anything.

## Keeping cohortData and pixelGroupMap in step

- Go through `updateCohortData()`, which returns both in one list; never modify them
  separately.
- Regenerate groups with `generatePixelGroups()` whenever cohort composition changes.
- Re-assert with `assertPixelCohortData()` after each modification, gated behind
  `getOption("LandR.assertions")`.
- `cohortDefinitionCols` can differ between modules. If a change could make two modules
  disagree about what a cohort is, flag it rather than proceeding.

## The two leading-proportion options

These look like one threshold and are two. Both live in `LandROptions()`
(`LandR/R/options.R`) and are read through functions in `LandR/R/leadingProportions.R`
— never hard-code the number.

| Option | Default | Question it answers |
|---|---|---|
| `LandR.mixedwoodProp` | `0.75` | Is this stand mixedwood, or broadleaf- or conifer-dominated? A *group* share. |
| `LandR.leadingSpeciesProp` | unset, falls through to `mixedwoodProp` | Which single species leads this stand? A *one-species* share. |

Read them with `mixedwoodProp()` and `leadingSpeciesProp()`. The 0.75 default follows
the EOSD / NFI rule of 75% basal area (volume for photo plots).

Which one a call needs depends on `mixedType`:

- `mixedType = 2` asks the mixedwood question — conifer group versus broadleaf group —
  so it uses `mixedwoodProp()`.
- Every other `mixedType` asks about a single species, so it uses
  `leadingSpeciesProp()`.

Because `mixedType = 2` is the default in every caller, a user who sets
`LandR.leadingSpeciesProp` expecting to change the leading-species rule may be
surprised that it does not apply. LandR warns in that case.

Two details inside the mixedwood test (`.isMixedwood()`):

- **Broadleaf share is summed across species** — *Populus*, *Betula*, *Acer* and the
  rest together — not taken per species.
- **Deciduous conifers are conifers.** *Larix* is `Type == "Conifer"` in
  `sppEquivalencies_CA`, so it counts on the conifer side. The test uses
  `Type %in% "Deciduous"` rather than `==` so a species missing from `sppEquiv`, with
  `Type` `NA`, does not silently become broadleaf.

`vegLeadingProportion = 0` is a sentinel meaning "no Mixed class at all", not a
threshold of zero.

## Subsample size

`LandR.subsetDataSize` (default `500L`) is the single place the statistical-model
subsample size is written down; read it with `subsetDataSize()`. Module parameters
such as `subsetDataBiomassModel` default to that function rather than to a literal, so
a user can still override per module but there is one default to change.
