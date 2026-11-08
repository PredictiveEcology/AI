# Data years in detail

## Which years exist

| Source | Years | Where defined |
|---|---|---|
| SCANFI V1 (land cover, species, biomass, age) | 2000, 2010, 2020 | `LandR:::.scanfi_v1_years` (`R/maps.R`) |
| SCANFI V2 | 1985 to 2025, every 5 years | `LandR:::.scanfi_v2_years` |
| SCANFI V3 | land cover only, read from NRCan's COG server; species, biomass and age still come from V2 | `?prepInputs_SCANFI_LCC_FAO`, `dataVersion` |
| FAO forest layer | 2019, 2022 (static: one layer serves every data year) | `LandR:::.faoForestYears` |

Asking for a year a source does not have is an error ("SCANFI V2 Landcover does not
exist for this year"), not a fallback to the nearest year. If you need a year between
two data years, choose the data year yourself (see "Matching a year to a data year").

Some older code still assumed V1 years. Two examples, both since fixed, show what to
look for when a module behaves as if only 2000/2010/2020 exist:

- `Biomass_borealDataPrep` filled class-240 pixels from SCANFI 2000, 2010 and 2020
  whatever `dataYear` was.
- A `stopifnot(dataYear %in% c(2000, 2010, 2020))` in `Biomass_borealDataPrep` stopped
  every V2-only year.

If you find another hard-coded year list, it is a bug: the years belong in LandR's
year constants, read from there.

## Who reads dataYear

| Module | Parameter | What it uses it for |
|---|---|---|
| `Biomass_speciesData` | `dataYear` | year of the species cover layers |
| `Biomass_borealDataPrep` | `dataYear` | year of land cover, biomass, age and species layers |
| `Biomass_core` | `dataYear` | only when `speciesLayers` are not supplied |
| `fireSense_dataPrepPredict` | `dataYear` | vegetation for prediction |
| `burnSummaries` | `dataYear` | land cover for summaries |

Each calls `SpaDES.core::paramCheckOtherMods(sim, "dataYear", ifSetButDifferent =
"error")` in recent versions. The check runs at `simInit()` time, inside each module's
`.inputObjects` or `init`. It compares with `identical()`. A module whose value is
`NULL` or `"default"` takes the single value the others agree on.

Run several data years by running the vegetation modules several times (a nested
simulation per year, as `fireSense_dataPrepFit` does), not by giving modules different
`dataYear` values in one `simList`.

## Matching a year to a data year

Two rules, used for two different questions. Both live in `fireSenseUtils` so that a
fit and every later prediction read the same vegetation for the same year.

- `dataYearFor(dataYears, years)`: the data year closest to, and **not after**, each
  year. Use it to choose the vegetation a simulation or prediction starts from. It
  stops if a year is before the first data year.
- `dataYearBefore(dataYears, years)`: the latest data year **strictly before** each
  year. Use it whenever vegetation is paired with an event that the vegetation layer
  may already record (fires, harvest). SCANFI of year Y already shows year Y's burns.

```r
fireSenseUtils::dataYearFor(c(1985, 1990, 2000, 2010, 2020), c(1985, 1999, 2015, 2024))
#> [1] 1985 1990 2010 2020
fireSenseUtils::dataYearBefore(c(1985, 1990, 2000, 2010, 2020), c(1986, 1990, 2021))
#> [1] 1985 1985 2020
```

Consequence for climate: a run whose vegetation starts at 1985 needs climate from
1986. A climate module that checks each requested year exists (for example
`climateYear` with a `samplingRange`) stops if you ask it for 1985 and the historical
climate starts in 1986. Older versions dropped the year silently.

## Hindcasting a past year

To simulate year Y as a test of a model: vegetation from data year Y (the state at the
end of Y), climate and observed fires of Y + 1. Make sure any time-since-fire layer
built from fire polygons stops at the year before the one you simulate, or the young
stands mask leaks the answer.
