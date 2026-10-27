# Module families

Each module is its own repo. Where it sits locally depends on the workspace;
`setupProject()` puts modules under `<project>/modules/<ModuleName>/`. Unless noted, repos
are under `PredictiveEcology/`.

## Biomass_* (vegetation succession)

LANDIS-II–style biomass succession. Cohort-based; the central data object is
`cohortData` (a `data.table` keyed by `pixelGroup`) alongside `pixelGroupMap`.

- `Biomass_core` — flagship succession model (dispersal, growth/mortality, aging,
  regeneration). Largest module; has a testthat suite.
- Data prep: `Biomass_borealDataPrep`, `Biomass_speciesData`, `Biomass_yieldTables`.
- Parameterization/fitting: `Biomass_speciesParameters`, `Biomass_speciesFactorial`.
  `Biomass_sppEcoregDataPrep`/`Fit`/`Predict` are in `CeresBarros/` (last changed 2023).
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
- Data prep: `fireSense_dataPrepFit`, `fireSense_dataPrepPredict`.
- Fire-regime units: `fireSense_ELFs` (the fits depend on it).
- Burning: `fireSense` — applies predicted ignitions/escapes and spread to the landscape.
- Summary: `fireSense_summary`. Also `fireSense_hindcast`.
- Archived or dormant: `fireSense_SizeFit`, `fireSense_SizePredict`, `fireSense_Tutorial`
  (archived); `fireSense_NWT`, `fireSense_dataPrep`, `fireProperties` (no changes since
  2019–2022). `FavierFireSpread` and `fireWeather` are in `CeresBarros/`.

Typical workflow: ELFs + dataPrepFit -> *Fit modules estimate statistical models ->
dataPrepPredict -> *Predict modules and `fireSense` apply them within a running
simulation. Supported by the `fireSenseUtils` package.

## Carbon

- CBM stack: `CBM_core`, `CBM_defaults`, `CBM_vol2biomass`, `CBM_dataPrep*`, `spadesCBM`,
  and the `CBMutils` package.
- Linked to LandR vegetation: `LandRCBM`, `LandRCBM_split3pools`;
  `LandRCBM_partialDisturbance` is in `camillegiuliano/`.
- Dormant: `LandR_CBM` (last changed 2023); `LandRCSAM` is in `ianmseddy/` (last changed
  2022).

## Other

- `canClimateData` — climate data prep.
- `LandR_yield`. `LandR_reforestation` and `LandR_BiomassGMCC` are in `ianmseddy/`,
  `LandR_BiomassGMOrig` in `eliotmcintire/`.

When in doubt about a module's role, read its `defineModule()` `description` and
`keywords`, and its `<Module>.Rmd` manual.
