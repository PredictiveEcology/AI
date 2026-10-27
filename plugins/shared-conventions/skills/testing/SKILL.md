---
name: testing
description: Writing and running tests for SpaDES modules, toolkit packages, and simulation model accessory packages (e.g. LandR/LandR.CS/fireSenseUtils) — both unit tests (a single module, event, or helper function) and integration tests (multi-module workflows). Covers the tests/unitTests.R + tests/testthat/ layout, building minimal in-memory rasters and data.tables, calling simInit()/spades(), reaching module-internal functions, and asserting on the returned simList. Use when the user asks to add, fix, or run tests for a module, simulation, or package.
metadata:
  ecosystem: SpaDES, LandR
  version: "1.0"
---

# SpaDES / LandR testing

Tests use **testthat**. Do not create tests unless asked; when asked, follow the existing
conventions in the target module or package rather than imposing new ones.

## Two kinds of test

- **Unit tests** exercise one thing in isolation: a single helper function, a single
  event, or a single module's `init`.
- **Integration tests** exercise a **chain of modules** communicating through shared
  `simList` objects (one module's `createsOutput` feeds another's `expectsInput`).

## Module test layout

- `tests/testthat/setup.R` — sets options and defines `testPaths` (a scratch tree whose
  `modulePath` is the folder *containing* the module). Copy it from
  `examples/module-tests-setup.R` in `PredictiveEcology/actions`. CI (`testthat-module`)
  converts the module to a package with `SpaDES.core::convertToPackage()` and runs
  `testthat::test_local()`, so helpers can be called directly.
- `tests/testthat/test-<name>.R` — one file per function or event, named after the thing
  tested, e.g. `test-<helperFn>.R`, `test-<Module>Init.R`.

Read an existing test in the target module before writing a new one, to match its fixtures
and style. In LandR, `Biomass_core` is a good reference.

## Building minimal inputs

Tests construct small, deterministic objects in memory: tiny raster layers and
`data.table`s with a handful of rows/pixel groups. Prefer fixed values with known expected
outputs over random data. If randomness is unavoidable, set a seed (a random integer, not
a special value like 42), and keep the study area tiny so tests run fast and reproducibly.

## Unit test patterns

### (a) Testing a single module helper function

Initialize a minimal `simList` so the module's functions are available, then call the
function directly. An exported function is visible by name; otherwise reach it via
`sim$.mods$<Module>$<fn>`:

```r
test_that("<helperFn> computes the expected result", {
  library(SpaDES.core); library(data.table)
  mySim <- simInit(
    times   = list(start = 0, end = 1),
    params  = list(.globals = list(verbose = FALSE)),
    modules = list("<Module>"),
    objects = list(),
    paths   = testPaths                               # from setup.R
  )
  input <- data.table(id = 1L, x = 1:5)               # small, fixed fixture

  fn <- if (exists("<helperFn>")) `<helperFn>` else mySim$.mods$`<Module>`$`<helperFn>`
  out <- fn(input)

  expect_equal(out$y, c(2, 4, 6, 8, 10))              # replace with known values
})
```

### (b) Testing an event / module init

Run the module (or a couple of events) and assert on the resulting `simList`:

```r
test_that("<Module> init produces its output object", {
  mySim <- simInit(times = list(start = 0, end = 2), params = parameters,
                   modules = list("<Module>"), objects = objects,
                   paths = testPaths)
  out <- spades(mySim, debug = FALSE)
  expect_s4_class(out, "simList")
  expect_true(!is.null(out$<outputObject>))
})
```

## Integration tests (multi-module workflows)

Examples in LandR: `Biomass_*DataPrep -> Biomass_core`; `fireSense_*Fit -> fireSense_*Predict`.

```r
test_that("<upstream> -> <downstream> chain runs end to end", {
  mySim <- simInit(
    times   = list(start = 0, end = 2),
    params  = params,
    modules = list("<upstream>", "<downstream>"),
    objects = objects,
    paths   = testPaths
  )
  out <- spades(mySim, debug = FALSE)
  expect_s4_class(out, "simList")
  # assert the handoff object exists and is well-formed
  expect_true(nrow(out$<handoffObject>) > 0)
})
```

Guidance:

- Keep the study area tiny (a few pixels) so the chain runs fast and deterministically.
- Use `reproducible::Cache()` and prebuilt fixtures for expensive data prep; cache to a
  `tempdir()` so tests stay hermetic.
- Assert on the **interface objects** passed between modules, plus a coarse end-state check.
- Modules requiring downloads should have those inputs stubbed or supplied via `objects`.

## Package tests

Toolkit packages (`SpaDES.core`, `SpaDES.tools`, `reproducible`, `Require`, etc.) and LandR
accessory packages (`LandR`, `LandR.CS`, `fireSenseUtils`) all use the standard testthat
package layout (`tests/testthat/` + `tests/testthat.R`). Run them via the devtools workflow
— see `spades-package-development` (toolkit) — e.g. `devtools::test("<Package>")`.
`LandR` and `fireSenseUtils` both have substantial suites to copy from.

## Running tests

- Module: source `tests/unitTests.R`, or `testthat::test_dir("<Module>/tests/testthat")`.
- Package: `devtools::test("<Package>")`.
- Always run from a context where the module's `reqdPkgs` (or the package's dependencies)
  are installed; use `Require()` to load them.

<!--Note to Ceres: request input from Eliot and Alex.-->
