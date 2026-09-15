# Module families

Module folders live directly under `~/GitHub/LandR/<ModuleName>/`. There are ~52.

## Biomass_* (vegetation succession)

LANDIS-II–style biomass succession. Cohort-based; the central data object is
`cohortData` (a `data.table` keyed by `pixelGroup`) alongside `pixelGroupMap`.

- `Biomass_core` — flagship succession model (dispersal, growth/mortality, aging,
  regeneration). Largest module; ~21 testthat files.
- Data prep: `Biomass_borealDataPrep`, `Biomass_speciesData`, `Biomass_sppEcoregDataPrep`,
  `Biomass_yieldTables`.
- Parameterization/fitting: `Biomass_speciesParameters`, `Biomass_speciesFactorial`,
  `Biomass_sppEcoregFit`, `Biomass_sppEcoregPredict`.
- Regeneration/fuels: `Biomass_regeneration`, `Biomass_regenerationPM`, `Biomass_fuels`,
  `Biomass_fuelsPFG`.
- Validation/summary: `Biomass_validationKNN`, `Biomass_summary`.

Typical workflow chain: species/ecoregion data prep -> `Biomass_borealDataPrep`
(builds initial `cohortData`) -> `Biomass_core` (runs succession) -> summary/validation.

## fireSense_* (fire modelling)

Organized as **fit** and **predict** pairs per fire process:

- Ignition: `fireSense_IgnitionFit`, `fireSense_IgnitionPredict`.
- Escape: `fireSense_EscapeFit`, `fireSense_EscapePredict`.
- Spread: `fireSense_SpreadFit`, `fireSense_SpreadPredict`.
- Size: `fireSense_SizeFit`, `fireSense_SizePredict`.
- Data prep / support: `fireSense_dataPrep*`, `fireSense`, `fireSense_summary`,
  `fireSense_NWT*`, `fireSense_hindcast`, `fireSense_ELFs`, `fireSense_Tutorial`,
  `FavierFireSpread`, `fireProperties`, `fireWeather`.

Typical workflow: data prep -> *Fit modules estimate statistical models -> *Predict
modules apply them within a running simulation. Supported by the `fireSenseUtils` package.

## Carbon

- `LandR_CBM`, `LandRCBM`, `LandRCBM_split3pools`, `LandRCBM_partialDisturbance`,
  `LandRCSAM` — carbon budget modelling coupled to LandR vegetation.

## Other

- `canClimateData` — climate data prep.
- `LandR_reforestation`, `LandR_yield`, `LandR_BiomassGMCC`, `LandR_BiomassGMOrig`.

When in doubt about a module's role, read its `defineModule()` `description` and
`keywords`, and its `<Module>.Rmd` manual.
