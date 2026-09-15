---
name: landr-testing
description: Writing and running tests for LandR/SpaDES modules and functions — both unit tests (single module or single helper function) and integration tests (multi-module workflows). Covers the tests/unitTests.R + tests/testthat/ layout, building minimal in-memory rasters and data.tables, calling simInit()/spades(), accessing module-internal functions, and asserting on the returned simList. Use when the user asks to add, fix, or run tests for a module or an accessory package function.
metadata:
  ecosystem: LandR
  version: "1.0"
---

# LandR / SpaDES testing

Tests use **testthat**. Do not create tests unless asked; when asked, follow the existing
conventions in the target module.

## Layout

- `tests/unitTests.R` — entry point that runs the suite:
  ```r
  # run all tests in the folder:
  test_dir("../<Module>/tests/testthat")
  # or a single file:
  test_file("../<Module>/tests/testthat/test-<name>.R")
  ```
- `tests/testthat/test-<name>.R` — one file per function or event. Name after the thing
  tested, e.g. `test-calculateCompetition.R`, `test-Biomass_coreInit.R`.

`Biomass_core` is the richest reference (~21 test files); read one before writing a new one.

## Building minimal inputs

SpaDES tests construct small, deterministic objects in memory: tiny `raster` layers and
`data.table`s with a handful of `pixelGroup`s. Prefer fixed values and known expected
outputs over random data. Set a seed if randomness is unavoidable (a random integer, not 42).

## Unit test patterns

### (a) Testing a single module helper function

Initialize a minimal `simList` so module functions are available, then call the function
directly. If it is exported it is visible by name; otherwise reach it via
`sim$.mods$<Module>$<fn>`:

```r
test_that("competition is computed correctly", {
  library(SpaDES.core); library(data.table)
  mySim <- simInit(
    times   = list(start = 0, end = 1),
    params  = list(.globals = list(verbose = FALSE),
                   Biomass_core = list(.saveInitialTime = NA)),
    modules = list("Biomass_core"),
    objects = list(),
    paths   = list(modulePath = "..", outputPath = tempdir())
  )
  cohortData <- data.table(pixelGroup = 1L, age = 1:5, B = 1:5, maxB = 40, sumB = 36)

  fn <- if (exists("calculateCompetition")) calculateCompetition else
        mySim$.mods$Biomass_core$calculateCompetition
  out <- fn(cohortData, stage = "spinup")

  expect_equal(round(out$bAP, 4), c(NA, NA, NA, NA, NA))  # replace with known values
})
```

### (b) Testing an event / module init

Run the module (or a couple of events) and assert on the resulting `simList`:

```r
test_that("Biomass_core init produces cohortData", {
  mySim <- simInit(times = list(start = 0, end = 2), params = parameters,
                   modules = list("Biomass_core"), objects = objects,
                   paths = list(modulePath = "..", outputPath = tempdir()))
  out <- spades(mySim, debug = FALSE)
  expect_s4_class(out, "simList")
  expect_true(!is.null(out$cohortData))
})
```

## Integration tests (multi-module workflows)

Integration tests exercise a **chain of modules** communicating through shared `simList`
objects (one module's `createsOutput` feeds another's `expectsInput`). Examples:
`Biomass_*DataPrep -> Biomass_core`; `fireSense_*Fit -> fireSense_*Predict`.

```r
test_that("dataPrep -> core chain runs end to end", {
  mySim <- simInit(
    times   = list(start = 0, end = 2),
    params  = params,
    modules = list("Biomass_borealDataPrep", "Biomass_core"),
    objects = objects,
    paths   = list(modulePath = "..", outputPath = tempdir(), inputPath = tempdir())
  )
  out <- spades(mySim, debug = FALSE)
  expect_s4_class(out, "simList")
  # assert the handoff object exists and is well-formed
  expect_true(nrow(out$cohortData) > 0)
})
```

Guidance:
- Keep the study area tiny (a few pixels) so the chain runs fast and deterministically.
- Use `reproducible::Cache()` and prebuilt fixtures for expensive data prep; cache to a
  `tempdir()` so tests stay hermetic.
- Assert on the **interface objects** passed between modules, plus a coarse end-state check.
- Modules requiring downloads should have those inputs stubbed or supplied via `objects`.

## Accessory-package tests

For `LandR`, `LandR.CS`, `fireSenseUtils`, use standard `testthat` package layout
(`tests/testthat/` + `tests/testthat.R`). See the `landr-package-maintenance` skill for the
devtools workflow (`devtools::test()`). `fireSenseUtils/tests/testthat/test-data.R` is an
existing example; `LandR` has no suite yet.

## Running tests

- Module: source `tests/unitTests.R`, or `testthat::test_dir("<Module>/tests/testthat")`.
- Package: `devtools::test("<Package>")`.
- Always run from a context where `reqdPkgs` are installed; use `Require()` to load them.
