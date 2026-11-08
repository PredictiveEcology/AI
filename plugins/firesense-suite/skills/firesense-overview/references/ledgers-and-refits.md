# Ledgers and refits

## What a ledger is

A ledger is an `sf` object with one row per fitted ELF polygon: the fitted parameters,
the covariate ranges used to rescale them, the link and its settings, the fit years and a
fit date. The spread and ignition models have separate ledgers:

- `fireSenseSpreadParams_<years><modelTag><fitFileSuffix>.rds`
- `fireSenseIgnitionParams_<years><modelTag><fitFileSuffix>.rds`

They live in a shared Google Drive folder (`spreadFitGoogleDriveFolder`,
`ignitionFitGoogleDriveFolder`; `fireSenseUtils::spreadFitLedgerFolder()`), so a fit made
by one person is used by everyone. `spreadFitLedgerFolder(testing = TRUE)` is the folder
for experiment fits. `spreadFitFilename = "latest"` (default) writes to the file named for
the fit's years and model, and reads the newest matching file.

A prediction reads the ledger row and applies exactly what is stored there: the link
(`spreadLink`), `powerLawGamma`, `powerLawShape`, `climateRef` and the covariate ranges.
A row without a field gets the older behaviour (e.g. no `spreadLink` means the logistic
"ceiling" link). So a new fitting option must be written to the ledger row, or
prediction will silently apply the old model.

## How a fit is found

Two steps, both spatial first:

1. `fireSense_dataPrepFit` reads the ledger rows that overlap the study area
   (`reproducible::CacheGeo()`, with a sliver tolerance so a neighbour that the study area
   only grazes is not returned).
2. `fireSense_spreadFit` (`hasPreRunFitForThisPolygon()`) skips the fit if one of those
   rows has `polygonID` equal to this ELF's name.

Consequences:

- A code change in a module or in fireSenseUtils does not refit anything. This is
  deliberate: a minor code change should not throw away a 40-core, multi-hour fit.
- Event caches of the data-preparation steps may still miss after an update (they key on
  module parameters and metadata). That is a recompute of inputs, not a refit.
- Changing the ELF version does not, by itself, refit anything.
- Never select a ledger row by ID before the spatial selection. IDs drift from geometry.

Generic ledger logic (spatial rule, keyed write, "latest") belongs in reproducible's
`CacheGeo` family, so any module can use one, not in fireSenseUtils.

## Refitting

Start a new ledger with a new `fitFileSuffix`, set once for all modules:

```r
params = list(.globals = list(fitFileSuffix = "_newObjective20261107"))
```

`.globals` only sets each module's own parameter of the same name; it is a user shortcut.

Why a new ledger rather than `doFit = TRUE`: the reasons to refit (a new objective, new
land cover, new fire years, a changed cause filter) make every old row stale at once. A
new file makes the change explicit and keeps old rows available for "did we improve"
comparisons by name.

Things that need a new suffix:

- `fireCauses`, fire years, covariates or land cover source
- spread objective (`DEoptimTests`, `crpsWeights`), link (`spreadLink`, `powerLawShape`),
  `wholeLandscapeSpread`
- anything that changes what the ignition or escape model is fitted to

The one suffix is shared by the spread and ignition ledgers, so every new spread suffix
also refits ignition. Plan for it; ignition fits are much cheaper than spread fits.

## Held-out fold fits

A cross-validation fold's fitted parameters are saved in the same row structure as the
`run` event's ledger row, built by the same function, with the fold fields added. Held-out
years are then scored through the real prediction path, which reads ledger rows. A
separate structure would need a parallel code path, and validation would stop testing
what the production run uses.

## The ELF list

`fireSense_ELFs` builds the national ELF polygons once and caches them in the cloud,
keyed only on a hand-set `ELFversion`. Bump `ELFversion` to rebuild; never add code,
parameters or remote checksums to that key, or every module edit rebuilds the ELFs. Its
figures are drawn uncached with `Plots()`.
