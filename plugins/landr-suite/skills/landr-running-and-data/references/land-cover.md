# Land cover, forest land and biomass partitioning

## Class 240: forest land that is not treed now

`LandR::prepInputs_SCANFI_LCC_FAO()` (and the NTEMS equivalent) recodes to 240
(`disturbedCode`) every pixel that is forest land but not treed in `year`. Forest land
comes from `forestLandFrom`:

- `"fao"`: the FAO forest layer.
- `"lccYears"`: treed (210, 220, 230) in any of `forestLandYears`.
- `"both"` (default): the union.

`forestLandYears` defaults to about one year per decade plus the most recent. `year`
itself is removed from the list for its own call (it adds nothing). Each extra year is
one more layer to download and project.

Downstream, `Biomass_borealDataPrep` treats 240 as forested
(`forestedLCCClasses`) and replaces it with a nearby forest class
(`LCCClassesToReplaceNN = 240`) before estimating growth parameters, because a
transient class should not get its own parameters.

### The nearest-neighbour fill and Cache

`LCCClassesToReplaceNNMethod = "nearestRandom"` (default) draws from the RNG. `Cache()`
does not key on RNG state, so a cached call replays one draw for every replicate. If
replicates must differ here, put the seed in the cache key; if they must agree, use
`"nearestWeighted"`, which is deterministic and gives the same answer on a grid-aligned
crop as on the full extent.

## Forest-land cost and caching

Measured on one study area (before caching was added): one call cost about 27 minutes:
FAO crop and project about 12 minutes, the other years' land cover about 11, then the
mask. A caller that asked for five data years paid it five times, and four of those
gave an identical answer. No cache setting could help, because there was no `Cache()`
in that path; it was a loop-invariant recomputation.

Now each input (the FAO layer and each year's land cover) is cached on the target
geometry (CRS, extent, dimensions), not on the land-cover values, because the inputs
are aligned but not masked to the land cover. Caching follows
`options("reproducible.useCache")` unless `options(LandR.forestLandUseCache = "always")`
is set. Under `spades.useCache = "eventsOnly"` the inner caches are off, so set the
option when a module prepares several years of one study area.

`useCache = "always"` also overrides the nesting rule in `reproducible`, where an inner
`Cache(useCache = TRUE)` takes the outermost cache's setting. Delete the cache entries
(`reproducible::clearCache()`) to recompute.

## Wetlands

`LandR::prepInputs_CWIM()` reads the Canadian wetland inventory map and
`LandR::wetlandToLCC()` recodes land cover: wet and treed (210, 220, 230, 240) becomes
81, other wet non-water becomes 80. Pass `keepClasses` for any class that must never be
overwritten (water by default; also non-flammable codes such as 0 if you use them).
In one comparison against NTEMS, wet/not-wet agreed on 82-89 % of pixels, but derived
class 80 matched NTEMS 80 on only 13-18 %; treat the 80/81 split as uncertain.

## Deciduous cover weight

`Biomass_borealDataPrep` splits each pixel's total biomass among species by cover,
weighting deciduous cover by `deciduousCoverWeight`. With
`fitDeciduousCoverWeight = TRUE` (default) it is estimated for your study area from
SCANFI canopy height and closure, in seconds. The parameter value (0.93) is only a
fallback for landscapes that cannot identify it. Estimates so far ran from about 0.65
(NTEMS biomass) to 1.01 (a landscape with 5 % deciduous cover), so check the message
saying which value was used.

An earlier estimator without a site-quality control returned 1.74 on the same data:
broadleaf grows on richer ground, and an uncontrolled between-pixel fit credits the
site to the species. Its search interval capped at 1, which hid the problem.

## Land cover is not static

Design anything that reuses land-cover-derived results across simulated years
(flammable maps, non-forest classes, templates) to recompute when the land cover
passed in changes. Prefer making the per-year work cheaper over caching it across
years. Test the reuse with land cover that changes between calls.
