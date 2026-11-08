# Why suppressed cohorts stack up

Evidence from one 1000-year, 240 m landscape run (year 3020 state) and a paired
simulator built from Biomass_core's own functions. Line numbers are approximate; find
the code by function name.

## What the stacks look like

- Per (pixel group, species) stack of 3 or more, cohorts are one succession step
  (10 years) apart.
- A shade-intolerant pine: median 5 cohorts spanning 40 years, recruited 20 to 70 years
  after the stand's oldest cohort, mostly under **other** species' canopies (pine was a
  median 3 % of stand biomass in stacked pixel groups).
- A mid-tolerant Douglas-fir: about 7 cohorts over 90 years.
- A very tolerant fir (tolerance 5): about 30 cohorts over 350 years, recruited
  continuously under the canopy.
- 69 % of pixel groups were at shade class 5.

## The light rule

`LandR::calcSiteShade()` (`R/light-shade.R`):

```
bAM      = sum(B of cohorts older than 5 years) / maxMaxB
maxMaxB  = max(maxB) over ALL species in the ecoregion group
siteShade = the class of bAM between the ecoregion's minRelativeB thresholds X1..X5
```

`sufficientLight` (a LANDIS-II input table, one row per shade-tolerance class) then
gives the probability that a species of each tolerance establishes at each shade
class. With the default table:

- tolerance t = 1 to 4 establishes only while shade < t, i.e. while bAM < X_t;
- tolerance 5 establishes only at shade 2 and above, and is never shut off.

Because `maxMaxB` is the largest species' maximum (often 18 to 28 kg/m2), a new stand
starting at `initialB = 10` takes 40 to 50 years to reach X1 = 0.15 of it. The stand
counts as open the whole time, while competition between cohorts already treats it as
closed. Species enter the light rule only through `shadetolerance`; non-integer
tolerances are interpolated between table rows.

`minRelativeB` is per ecoregion group, not per species, and is built by
`Biomass_borealDataPrep` (`minRelativeBFunction`, default
`LandR::minRelativeBDefaults()`). Its default X1..X5 changed twice (0.2/0.4/0.5/0.7/0.9,
then 0.15/0.25/0.50/0.75/0.85, now 0.15/0.25/0.35/0.45/0.55). X4 and X5 give the same
column in the default light table, so X5 never matters.

## The growth floor

In growth and mortality, `aNPPAct` is floored: `pmax(1, aNPPAct - mAge)`. Competitive
mortality is capped at growth. A suppressed recruit therefore gains exactly 1 g/m2 a
year and never dies of competition: its B equals its age until it reaches longevity.

## Growth share is U-shaped in stand biomass

A rule based on a recruit's predicted growth relative to open ground looks natural and
fails. The potential term uses `bPot = maxB - sumB + B0` (Biomass_core `R/helpers.R`),
and the resulting share falls as the stand fills, then rises again close to `maxB`. A
relative threshold therefore admits recruits again in nearly full stands: in one test,
90 % of the Douglas-fir establishments it allowed without fire were in stands above
0.9 of `maxB`. Those recruits stayed on the floor anyway.

## What was not resolved

- Whether an absolute rule (predicted growth must exceed the floor) can work without
  dropping species from old stands. One version did: it removed a common birch from
  almost all fire-free pixels.
- Whether large young-cohort biomass in one older run (B 1,000 to 2,000 at age 1,
  which closes stands at once and prevents stacks) came from a different setup. It
  was seen once and not pursued.
