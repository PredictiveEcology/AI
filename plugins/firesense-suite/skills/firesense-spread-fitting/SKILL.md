---
name: firesense-spread-fitting
description: Fitting and changing the fireSense spread model (fireSense_spreadFit, fireSenseUtils objective functions, clusters DEoptim). Use when running or debugging a spread fit, changing the objective (CRPS terms, crpsWeights, DEoptimTests), the spread link (powerLaw, p_c calibration, powerLawShape / delta, yearSpreadSD year effect), whole-landscape versus buffered fire simulation, spread-probability gates, parameter bounds, the DEoptim population, stop rule and convergence, emulator-seeded starts, or judging and comparing fits. Also covers fit compute (workers, memory per worker, BLAS threads, hyperthreading) and the objectives already tried and ruled out.
metadata:
  ecosystem: LandR
  version: "0.1"
---

# fireSense spread fitting

The spread model gives each pixel a spread probability from its covariates (fuel classes,
stand age, non-forest cover, a drought index). `fireSense_spreadFit` finds the
coefficients with DEoptim: every candidate parameter set simulates every observed
escaped fire of the fit years many times (`objfunFireReps`, default 50), and the
objective scores the simulated fires against the observed ones. Read
`firesense-overview` first for ledgers and `doFit`.

Check defaults against the module's `defineParameter()` text on the `development`
branch before quoting them: they change often, and the descriptions record why.

## The model

- **Link** (`spreadLink = "powerLaw"`, default):
  `p = p_c - (p_c - floor) * exp(-sign(x) * |x / gamma|^shape)`, with `x` the linear
  predictor. It comes from percolation: fire size grows like `(p_c50 - p)^-gamma` near the
  threshold. `fireSenseUtils::calibratePowerLaw()` simulates fires on the ELF's own
  flammable map once per ELF and gives `p_c50` (the spread probability at which half the
  fires burn a quarter of the largest flammable patch, about 0.22-0.32) and `gamma`.
  `p_c` is fitted, bounded above by `p_c50 + powerLawPcMargin`, so a fit never tries
  thresholds far above the ELF's own.
- **`gamma` is fixed, not fitted**: it is exactly confounded with the scale of the
  coefficients. Iterating it changes nothing.
- **`powerLawShape` (delta) is fixed.** Fits are indifferent to it in-sample: every delta
  from 0.5 to 3 reproduced area and the largest fires equally well. Most pixels sit near
  `p_c` or at 0, so the link behaves as a switch and delta is not identified. The
  convention is delta < 1 for headroom: at the median pixel, 9-12% of the range is left
  below `p_c` at 0.5 against 0-4% at 1, so drought can still raise burnability. See the
  retraction in [references/ruled-out.md](references/ruled-out.md) before quoting
  any delta result.
- **Year effect** (`yearSpreadSD`): one draw per year, added to `x`, so all of a year's
  fires burn hotter or cooler together. Without it the model cannot produce the observed
  spread of big and small years. Its bounds (`yearSpreadSDBounds`, 0-10) are wide on
  purpose: fits reached earlier bounds of 1 and 5.
- **Bounds are wide; only signs are constrained.** A binding bound changes the estimate.
  The only prior knowledge imposed is the sign of `youngAge` (<= 0), the drought indices
  (>= 0) and fuel biomass terms. If an estimate sits near a bound, widen the module
  default (`upperAndLowerVal`, `upperAndLowerValFuel`), do not tune it per run.
- Climate covariates are rescaled with fixed ranges (`fireSenseUtils::climateCovRanges`),
  not the polygon's own range, so coefficients compare across ELFs.

## The objective

`DEoptimTests = "crps"` (default) is a sum of proper scores, weighted by `crpsWeights`
(`fireSenseUtils::crpsWeightsDefault()`):

| Term | Scores |
|---|---|
| `fire` | per-fire CRPS on log size, each observed fire against its own replicates |
| `adTest` | Anderson-Darling on the pooled size distribution |
| `areaDist` | share of area burned by fires up to each size |
| `totalArea` | CRPS of log total area |
| `top10` | CRPS of the 10 largest fires (their sum) |
| `annualArea` | mean over years of CRPS of log annual area; weight 0 by default |

Convention: a production objective includes the annual-area term (give it a weight),
because the model must reproduce variability between years, not only the total.

Only fires that reach `escapeSizeHa` (50 ha) are fitted; each simulated fire first grows
to that size, then spreads normally.

### Whole landscape, not buffers

The old design simulated each year's fires only inside buffers around the observed fires.
A fire that reached an open buffer edge was "cut" and scored as at least the observed
size. Measured: 6-15% of simulated fires were cut, carrying 22-31% of simulated area and
about a third of each replicate's 10 largest fires. Unbounded, cut fires grew 1.4-2x, so
buffered fits burned 1.2-1.4x too much once predicted on the whole landscape.

`wholeLandscapeSpread = TRUE` (with `fireSense_dataPrepFit`'s
`wholeLandscapeSpreadCovariates = TRUE`) spreads every fire on the whole ELF. It is
affordable because the spread probability is computed lazily: the linear predictor once
per year, `p` only on the cells a fire reaches (`SpaDES.tools::spreadCpp(link = )`). Cost
was 0.5-1.2x a buffered evaluation, with identical burned cells. Needs
`spreadLink = "powerLaw"` and `penaliseRunaways = FALSE`, and a new `fitFileSuffix`.

### Gates are a speed device only

Gates (`spreadProbGateTest`) refuse a year whose spread-probability map is clearly
hopeless, without simulating it. A gate must never change the answer. Incident: a small
year failed the "not spread out enough" check once delta passed 0.75, scored the floor,
and made a cliff in the objective; at some parameter sets the gates refused 30-75% of
years. `gateRefusal = "simulate"` simulates and scores those years like any other; with
it, no gate runs. Likewise, verbosity and plotting settings must never change what runs.

## DEoptim

- **Population size = workers.** `nCoresNeeded` is NP; `clusters` sets NP to the workers it
  builds (default `fireSenseUtils::deoptimPopulationSize()`: 30-50 by parameter count). More
  members than workers wastes time; do not propose load-balanced scheduling.
- **Idle cores are expected.** A generation waits for its slowest member, so reserved cores
  run 33-50% busy. That is not free capacity. Smaller NP over more ELFs at once beats a
  bigger NP.
- **Stop rule** (`clusters::deoptimConvergence()`): stop when, over the last `window`
  generations (300), the population median improved less than 1 SE **and** its spread
  (MAD) changed less than 10%, never before `minGenerations` (350). Change only `window`
  and `minGenerations`: tighter SE or MAD thresholds may never be met on a noisy objective.
  Do not cap generations to meet a deadline. A fit forced to 3000 generations (stopped by
  the rule at 930) improved its median 0.4% and held-out scores were within noise.
- **Judge fits by the population median, never the best member.** The objective is
  stochastic; "best" is the luckiest draw and jumps at every rescore. Compare fits at
  like-for-like generation counts.
- **Rescoring:** the surviving population is re-evaluated every 10 generations
  (`clusters.deoptimRescoreEvery`), about 10% of wall time, by design.
- **Every generation is cached**, so a stopped fit resumes. But any change to the
  objective function's body changes the generation keys and restarts at generation 1.
  Batch objective changes.
- `strategy = 6` with `p = 0.1` did best in a settings study. Keep DEoptim's `c = 0`
  when several generations run per DEoptim call (see ruled-out notes on NaN trials).
- **Emulator start** (`initialPopMethod = "emulator"`): a Gaussian-process search
  (about 1,000-1,600 real evaluations) picks a good, spread-out starting population.
  It reached a given median in 30-45% fewer generations. On its own it found a nearby
  but worse basin, so it is only a start. It falls back to the default above
  `emulatorMaxParams` parameters.

## Reading a fit

- **Unidentified is not unimportant.** Fuel classes are collinear, so many coefficient
  combinations give nearly the same spread probabilities. A sign-unstable fuel
  coefficient means the data cannot apportion the effect among classes, not that fuel
  does not matter. Check identifiability of what the model predicts (per-pixel spread
  probability across the top members) or of sums (total fuel effect).
- Sets within noise of the best objective can give hindcast areas from 0.6 to 1.0.
  Prediction uses whole parameter sets from the top of the population, one per replicate,
  never blended parameters.
- The intercept is flat within noise once covariates are centred; do not read it.
- Known open bias: fits under-burn the 10 largest fires in-sample. The largest observed
  fires are simulated at a few percent of their size from their own ignitions.

## More

- [references/ruled-out.md](references/ruled-out.md): objectives and fixes tried and
  dropped, with the evidence, and retracted results.
- [references/compute.md](references/compute.md): workers, memory, BLAS threads,
  hyperthreading, cluster placement, and compute waste found.
- Validating a fit against observed fire: `firesense-hindcast-validation`.
