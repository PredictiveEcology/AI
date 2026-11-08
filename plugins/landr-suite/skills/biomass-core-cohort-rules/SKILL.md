---
name: biomass-core-cohort-rules
description: Changing or evaluating the rules in Biomass_core (and LandR) that decide how many cohorts exist - establishment from seed, the site-shade and sufficientLight rule, minRelativeB, the +1 g/m2/yr growth floor, cohort squashing, removal of suppressed cohorts, establishment limits, and calculateSumB. Covers how to judge a rule (cohorts per species per pixel, not bias against the current model), why suppressed cohorts stack up in long runs, the existing off-by-default options (cohortSquash, cohortRemoveSuppressed, cohortEstablishmentLimit) and their side effects on LandR-CBM, what was tested and ruled out, and how to test a new rule. Use when cohortData grows too large, a species has too many or too few cohorts, a long run slows down, or someone proposes a change to establishment, competition or cohort merging. Builds on landr-code-development and its references/cohort-semantics.md.
metadata:
  ecosystem: LandR
  version: "0.1"
---

# Biomass_core cohort rules

Read `landr-code-development` first, especially its rules on mechanistic changes (check
the LANDIS-II source and history, get the user's approval) and
`references/cohort-semantics.md` (when cohorts are created, at what age, and which
situations put young and old cohorts in one pixel group). This skill adds what was
learned from trying to limit cohort numbers in 1000-year runs.

## The problem you will see

In long runs, `cohortData` keeps growing: cohorts per pixel group rose from about 2 to
about 23 over 1000 years on one landscape, and time per year doubled. Most of the new
rows are **stacks of suppressed cohorts of one species in one pixel group**, recruited
one per succession step, each growing at the +1 g/m2/yr floor until it dies of age.

They are not only a cost. In fire-free stands those stacks are the advance
regeneration that decides which species takes over. Removing or merging them changes
the model, not just its speed.

## How to judge a rule (convention)

Judge a cohort rule by **how many cohorts each species gets per occupied pixel over
time**, and by the rows it keeps. Report the change in landscape biomass or species
share only as context.

Why: the current model is itself wrong here. It gives 3 to 6 cohorts per stand of a
shade-intolerant pine and about 30 of a very tolerant fir. "Distance from the current
model" therefore measures how much you kept of a defect, not quality. As a rough target
on one test landscape, the modellers agreed on about 2 cohorts for a shade-intolerant
pine, 4 for a mid-tolerant Douglas-fir and 6 for a tolerant fir.

Always also:

- Run without fire **and** with fire (for example fire return intervals of 150 and 500
  years). With frequent fire almost every rule is within noise; the differences show
  in fire-free stands.
- Look at **each species' own** biomass and occupancy over time. A rule cut one
  tolerant species' own biomass by 58 % while the landscape metric hid it, because that
  species was 10 % of landscape biomass.
- Count species-decades where a species goes locally extinct.

## Why the stacks form

Short version; detail with file references in
[references/why-cohorts-stack.md](references/why-cohorts-stack.md).

1. **The light rule thinks a young stand is open for decades.** `LandR::calcSiteShade()`
   computes shade from the stand's biomass divided by `maxMaxB`, the largest `maxB` of
   **any** species in the ecoregion group. A new stand starts at `initialB = 10` and
   takes 40 to 50 years to reach the first `minRelativeB` threshold (0.15) of that
   maximum. Every succession step in that window adds a cohort of every intolerant
   species whose seed arrives.
2. **Suppressed recruits do not die.** A recruit under any canopy grows at the floor,
   `pmax(1, aNPPAct - mAge)` (`Biomass_core.R`, growth and mortality), so its biomass
   equals its age. In one run 99.8 % of age-11 cohorts had B = 11. Lone cohorts of the
   same species grow normally, so the growth code itself is fine.
3. **The most tolerant class is never shut off.** With the default `sufficientLight`
   table, tolerance-5 species establish at shade 2 and above, so they recruit
   continuously under a canopy.

## Options that already exist

All are `NA` (off) by default, and all change results. Extend these rather than
adding a parallel mechanism.

| Parameter | What it does | Side effects |
|---|---|---|
| `cohortEstablishmentLimit = c(interval, minCohorts)` | a species with more than `minCohorts` older cohorts in a pixel group establishes from seed only when `time(sim)` is a multiple of `interval`; `Inf` = hard cap | serotiny and resprouting not limited; LandR-CBM unaffected |
| `cohortEstablishmentLimit = c(interval, m1, ..., m5)` | per shade-tolerance class (newer versions; check the parameter description) | `c(Inf, 1, 2, 3, 4, 5)` gave about 2 / 4 / 6 cohorts for the three species above, 46-64 % of rows, fire-free biomass -10 to -26 % over 600-1000 years, no change at a 150-year fire interval |
| `cohortRemoveSuppressed = c(relativeB, minAgeFrac)` | removes a cohort below `relativeB` of its pixel group's B and older than `minAgeFrac` x longevity; never a species' last cohort | LandR-CBM unaffected |
| `cohortSquash = c(interval, width, ...)` | merges same-species cohorts up to `width` years younger when a cohort reaches a multiple of `interval` | **breaks LandR-CBM**, which maps each cohort to a CBM growth curve |

What each rule did in the test simulator, and what was ruled out:
[references/rules-tested.md](references/rules-tested.md).

## Testing a new rule

- Build a small paired simulator from Biomass_core's own growth, mortality, light and
  establishment functions, started from a saved real `cohortData`. Run each rule and
  the baseline with common random numbers over several seeds, so the difference is
  the rule and not the draw. Confirm the baseline arm reproduces saved results with
  `identical()` before trusting any comparison.
- Measure run-to-run noise first (no fire: about 1.3 % of landscape biomass on the
  test landscape) and report effects against it.
- A rule that wins on the simulator still needs a full run with the same fits, the same
  code and only the option changed. A comparison against an older run, made with older
  code, cannot show the option's effect.
- Follow the `spades-experiments` skill's controlled-comparison design for that full
  run.

## Other Biomass_core facts that bite cohort work

- `minCohortBiomass` must be lower than `initialB` (init stops otherwise). With
  `initialB = 10` there is no room to raise it.
- Growth has no age term; only age-related mortality does. A cohort cut back to a
  given B regrows exactly like a young cohort of that B, then dies on its original age
  schedule.
- `calculateSumB()` follows LANDIS-II: cohorts younger than `successionTimestep` do not
  add to the stand total, but every cohort, young or old, sees that total. Before the
  fix (Biomass_core #112) young cohorts saw 0 and grew almost as if unshaded.
- `speciesEcoregion$year` is in `time(sim)` units. Before Biomass_core #124, `Init`
  renumbered it to `year - min(year)`, which applied the wrong years' traits whenever
  the table had more than one year. Single-year tables (every run so far) were not
  affected.
- A species present in `species` but missing from `speciesEcoregion` used to produce an
  all-`NA` row through a right join in
  `LandR::modifySpeciesAndSpeciesEcoregionTable()`. If `min(speciesEcoregion$year)`
  is `NA`, look there first.

Growth curves and competition between species, which decide whether two species can
coexist at all: [references/growth-and-competition.md](references/growth-and-competition.md).
