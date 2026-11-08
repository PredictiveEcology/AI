# Cohort rules tested, and what was ruled out

All numbers are from a paired simulator started from one real landscape (nine
species, 240 m pixels), several seeds, common random numbers. "Rows" is cohort rows
kept relative to the current rule. "Change" is the change in landscape biomass against
the current rule (without fire / fire every 500 years / every 150 years); it is context,
not a quality score (see SKILL.md). Run-to-run noise without fire was about 1.3 %.

## Count limits

| Rule | Rows (no fire) | Change | Notes |
|---|---|---|---|
| Hard cap per tolerance class, `cohortEstablishmentLimit = c(Inf, 1, 2, 3, 4, 5)` | 0.46-0.64 | -10 % at year 600, -26 % at year 1000 / ~0 at FRI 150 | the only rule on the cohort target in both fire regimes, by construction |
| Same, counting only suppressed cohorts | | | missed the target (7 and 12 cohorts for the mid and tolerant species) |
| Cap: no new cohort once K = 20 older exist | 0.95 | 7.1 / 2.3 / 0.3 % | |
| Establish only every 20 years once n > 10 | 0.88 | 5.2 / 1.5 / 0.3 % | |
| Same, n > 5 | 0.76 | 10 / 3.3 / 0.7 % | |
| One cohort per species per shade class, tolerance 1-2 only | 0.97 | 0.7 / 1.5 / 2.3 % | fixes the intolerant pine (1 cohort); tolerant stacks untouched |
| Same, all tolerances | 0.31 | 41 / 13 / 2.0 % | |

## Light rule changes

| Rule | Rows | Change | Notes |
|---|---|---|---|
| Tolerance-5 row of `sufficientLight` to 0,0,1,1,1,0.5 | 0.92 | 2.7 / 0.8 / 0.1 % | tolerant fir 36 -> 22 cohorts; no losses |
| Tolerance-5 row to 0,0,1,1,1,0 | 0.83 | 8.1 % | tolerant fir -> 12 |
| `minRelativeB` x 0.5 | 0.69 | 33 / 13 / 2.4 % | 89 species-decades lost; tolerant stack untouched |
| `minRelativeB` x 1.5 | 1.40 | | more rows |
| Older default tables (0.2/0.4/... and 0.15/0.25/0.50/...) | 1.32-1.36 | 51-67 % | |

## Merging and removing

| Rule | Rows | Change | Notes |
|---|---|---|---|
| Remove suppressed cohorts below 1 % of stand B and older than 0.85 x longevity | 0.98 | 0.4 / 0.1 / 0.1 % | barely reduces rows |
| Time-based squash every 100 years, 20-year bands from age 80 | 0.71 | 9.9 / 3.4 / 1.9 % | no extinctions |
| Age-triggered squash (`cohortSquash`, merged rule) | 0.44-0.49 | 24-25 / 8.3 / 4.8 % | 70-93 species-decades lost; merges snowball at every multiple |

Squashes also shifted stand-cycle timing of a tolerant hemlock and raised the
tolerant fir's biomass by 26-49 % at year 1000. The milder squash settings
(interval 200-300, width 10) were not tested.

## Ruled out

| Idea | Why |
|---|---|
| Drop suppressed cohorts at any age (0.1-1 % relative cut) | 10-60 % change, two species extinct |
| Merge all suppressed cohorts, or cap cohorts per species, or stop re-stacking | 10-170 % change |
| Global `successionTimestep` 20 or 30 | biased even with fire (3-14 %), extinctions |
| Raise `minCohortBiomass` | must stay below `initialB` (10) |
| Let suppressed cohorts die (suppression mortality, or remove the cap on competitive mortality) | rows go **up** (gaps refill), 65-206 extinctions; uncapping alone leaves rows unchanged |
| Coarser pixel-group keys or a multiplicity column | under 7 % gain; groups are separated by species x age |
| Round merged ages to the timestep grid | no effect |
| Growth-share threshold relative to open ground, all tolerances | rows 0.13-0.46, 62-77 % change, the whole understory goes |
| Same, calibrated per tolerance | on target with fire, but without fire the mid-tolerant species rose to 11-14 cohorts (U-shape, see why-cohorts-stack.md) |
| Absolute growth threshold (predicted first-year growth above a floor) | intolerant pine stuck at 1; drops species from old fire-free stands |

## Limits of these results

- One landscape, one simulator. The simulator reproduced the real run's stacking at
  FRI 150 but is not the full model.
- No observed regeneration or stand-structure data were used. A rule that is "right"
  needs that comparison; these results only show what each rule does.
- The effect of the establishment limit on a full real run has not been measured
  against a same-code, same-fit baseline.
