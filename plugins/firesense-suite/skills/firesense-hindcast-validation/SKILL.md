---
name: firesense-hindcast-validation
description: Validating a fire simulator (fireSense, scfm or any other) against observed fire with hindcasts and in-sample checks. Use when setting up fireSense hindcast jobs (fireSenseUtils::hindcastSetup, hindcastObserved), scoring simulated against observed fire regimes with the fireSimulator_validation module (gates, CRPS skill tests, nulls), choosing which fires count as observed (causes, ELF core, burnable pixels, 50 ha), summarising replicate runs (medians, single-run 2.5-97.5% ranges, observed rank), interpreting area ratios and top-10 fire scores, or building results tables and report pages.
metadata:
  ecosystem: LandR
  version: "0.1"
---

# Hindcast validation of fire models

A hindcast simulates a past year from the fitted models and compares the simulated fire
regime with what was observed. The question is not "did we predict 2015" but "is the
observed record a plausible draw from the model".

## Order of checks

1. **In-sample first.** Fit, then simulate the fit's own fires with the fit's own data
   (`fireSense_spreadFit` does this after a fit: `simulateMembers`, `sim$spreadFitSizes`).
   This should have no bias. If in-sample area is off, the problem is the fit or the
   objective, not the data or the prediction path. Do not treat a full hindcast as
   in-sample: it adds drawn ignitions and escapes, prediction covariates and the whole
   landscape.
2. **Spread alone.** `hindcastSetup(year, ignitions = "observedEscapes")` spreads each
   year's observed escapes, which separates spread error from ignition and escape error.
3. **Full hindcast.** Predicted ignitions and escapes, then spread.

## Setting up a fireSense hindcast

`fireSenseUtils::hindcastSetup(year)` returns the `times`, `modules` and `params` to use in
`setupProject()`. It holds the year's vegetation static, draws that year's climate
(`climateYear` with `samplingRange = year`), and runs the replicates as decimal years
(10 by default; 20 with `allSets = TRUE`, one per fitted parameter set). It runs the
climate and fireSense modules only, not the vegetation modules.

- A hindcast only predicts: `doFit = FALSE`. It stops if the ledger has no fit for the ELF.
  Point it at the ledger it should test (`fitFileSuffix`).
- **Vegetation is from before the fire year.** A land-cover map of year Y already shows
  year Y's burns as lost biomass, which leaks the answer. A placebo test confirmed it:
  spatial skill appeared against the same year's fires and vanished against the next
  year's. Both the fit and the prediction use the latest vegetation year strictly before
  the fire year. Hindcast results made with same-year vegetation are not usable.
- About 20 replicates per ELF-year is the convention. With 4 runs, the range of an area
  ratio was 0.4-2.3.

## What counts as observed

The observed side must use the fit's own definitions, or the ratios measure the
mismatch. `fireSenseUtils::hindcastObserved()` does this: it reuses the helpers the fit
uses. Its rules:

- inside the ELF core only (the buffer is excluded);
- the fit's fire causes (`fireCauses`, default natural and unknown);
- area burned on burnable pixels (what the simulation can burn), with the polygon area kept
  beside it;
- fires of at least `escapeSizeHa` (50 ha) for sizes and escapes, as in the fit.

Incident: the fit's observed fires were 1.8-8x the scorer's, because the fit counted fires
outside the core and human-caused fires while the scorer did not. Another: the fit
counted escapes from NFDB points, the scorer from NBAC polygons. Align definitions
before reading any ratio.

## Scoring: the fireSimulator_validation module

Validation metrics are model-agnostic and live in the `fireSimulator_validation` SpaDES
module, not in fireSenseUtils, so scfm and other simulators can use them. The scoring
functions take plain tables and rasters; one adapter file reads fireSense outputs. Keep
fireSense objects and ledger assumptions out of metric functions.

- **Gates** (pass/fail, no null), among them: the scoring pipeline reproduces the fit's
  objective; area within 0.25-4x observed; the fit's fires carry at least half the observed
  area; the large fires within 10x; each link of ignitions x escape rate x area
  per escape within 0.25-4x.
- **Skill tests**: CRPS skill on log(1 + x) for annual ignitions, escape rate, annual area,
  the size distribution, and the ranking of years, against nulls: N1, the ELF's own history
  (every year, the scored one included, so the model must beat a null that has seen the
  answer); N2, a regression on the ELF's mean climate; N0, the model's own runs assigned
  to the wrong years, as a floor only. Pooled over ELFs, with a bootstrap over ELFs and years. A few
  years per ELF have no power on their own.
- Dropped as verdicts: log score (punishes narrow ensembles without limit), CRPS on raw
  hectares, pixel AUC, per-ELF PIT, a lognormal null fitted to all years (circular
  in-sample), a permutation null on year ranking (any climate-driven model beats it).
- **A null must not reuse the scored year's observations.** A spatial null built from the
  scored year's own fires carries their size and shape and is circular. Use other years'
  fires, rotated or flipped, area-matched.

## Summarising runs

- **Medians, not means**, for central tendency in every test, gate, table and summary. Fire
  area is heavy-tailed: a few runaway replicates gave mean area ratios of 20-100x. A ratio of
  totals is fine where it is not a summary across runs.
- **Show the range of single runs.** The observation is one realisation, so compare it
  with the spread of single runs, each scored on its own: write "median run (2.5%-97.5% of
  runs)", e.g. "area 1.46 [0.62, 3.60]". A bootstrap interval of the median says only how well
  the median is estimated; it may go beside, never instead. Differences of 20-30% between
  fits of one ELF are often inside run noise: say when both intervals contain the other.
- **Observed rank among runs** is the calibration number. Near 0% or 100% means the
  observation lies outside what the model produces. With 20 runs the range ends are rough;
  you need at least 39 runs before "outside the 95% range" means p < 0.05.
- **Judge the regime, not the years.** One year too low and another too high is fine; the
  target is the right distribution of years and fire sizes. Matching years one by one needs
  covariates the model does not have. Do not use "the five big years" or "sum of yearly
  medians" as a pass rule.
- **Check quiet and busy years separately.** Totals can match while the model compresses
  the differences between years.

## Traps

- **Check the swept parameter reached the simulator.** A sweep over the link shape showed a
  clear pattern that was entirely a driver bug: the parameter was never passed, so every arm
  ran the default. Confirm outputs differ between settings before interpreting, and retract
  every number made before a fix.
- **"Top 10" must mean the same thing everywhere.** The sum and the median of the 10 largest
  fires differ about 2x. Use the sum, in-sample and in hindcasts alike.
- **Compare like with like.** Scores before and after a change in cause filter, buffer
  design or runaway handling are not comparable.
- **Score each ELF as soon as its fit ends.** Chain fit -> hindcast -> score per ELF (and per
  arm of an experiment) instead of waiting for a whole campaign.

## Reporting

- Every computation behind a report lives in module code (a PR), so anyone can rerun it
  without an assistant; only assembling the page happens outside.
- Module figures go through `SpaDES.core::Plots()`; its `.plots` parameter chooses screen or
  png.
- Results tables are sortable by any column (ELF, arm, each score). Give each cell a numeric
  sort value (the median for "x [lo-hi]" cells) and sort ELF ids numerically.
