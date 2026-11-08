# Growth curves and competition between species

Findings from reproducing a "spruce grows +1 a year in mixtures" artifact with
Biomass_core's own growth functions, and from refitting species traits. They matter
whenever a cohort rule or a trait change is judged by species coexistence.

## Competition is winner-take-all

- A cohort's share of growth is `bPM = B^0.95 / sum(B^0.95)` within the pixel group,
  and its ANPP scales with `maxANPP x maxB^(1 - growthcurve) x B^growthcurve x bPM`.
  For a minority cohort that is roughly `B^(growthcurve + 0.95)`: whoever starts ahead
  stays ahead.
- Two species with equal `maxB` coexist only if their `growthcurve` values are within
  about 0.005. A difference of 0.02 left the weaker species at 28 % of the other's
  biomass; 0.04 at 10 %. Mortality shape made no difference.
- Removing the +1 floor does not rescue the weaker species (it stalls instead).
  Continuous (non-integer) biomass helps a little but does not change the outcome.
- What balances two species is `maxANPP x maxB^(1 - growthcurve)`, not a common
  `growthcurve`. With a common `growthcurve` the species with the larger `maxB` wins.

## Fitting traits one species at a time

`Biomass_speciesParameters` fits each species alone to its own growth curve. The
objective is flat (a wide range of `growthcurve` is within 2 log-likelihood units),
and the answer is a weighted mean of the top fits, so small differences in the plot
data (for example a species with no plots younger than 30 years) move `growthcurve`
by more than the coexistence window. Fitting pairs jointly is just as flat with
all-plot curves; it only helps with data from plots where the species co-occur.

Check the species definition too: in one case BC interior spruce ("Picea glauca" in
BC plots) was not mapped to Engelmann spruce, which alone moved its `growthcurve` from
0.85 to 0.737.

## Yield tables and the factorial

- `Biomass_yieldTables` starts cohorts at B = 1, age 0; Biomass_core and the factorial
  use `initialB = 10`, age 1. The lower start makes the minority effect worse but does
  not cause it.
- In the `Biomass_speciesFactorial` design (equal `maxB`, pairs only where species 1 is
  at least as large in every trait), 19 % of about 980,000 pairs had species 1 stuck at
  +1 a year to age 61.

None of these led to a code change yet; they are listed so the next person does not
rediscover them.
