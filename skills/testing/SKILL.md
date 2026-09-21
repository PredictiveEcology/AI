---
name: testing
description: Writing and running tests for SpaDES modules, toolkit packages, and simulation model accessory packages (e.g. LandR/LandR.CS/fireSenseUtils) — both unit tests (a single module, event, or helper function) and integration tests (multi-module workflows). Covers the tests/unitTests.R + tests/testthat/ layout, building minimal in-memory rasters and data.tables, calling simInit()/spades(), reaching module-internal functions, and asserting on the returned simList. Use when the user asks to add, fix, or run tests for a module, simulation, or package. For the CI workflows that run module tests on a PR, use spades-module-ci.
metadata:
  ecosystem: SpaDES, LandR
  version: "1.1"
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

- `tests/unitTests.R` — entry point that runs the suite:
  ```r
  # run all tests in the folder:
  test_dir("../<Module>/tests/testthat")
  # or a single file:
  test_file("../<Module>/tests/testthat/test-<name>.R")
  ```
- `tests/testthat/test-<name>.R` — one file per function or event, named after the thing
  tested, e.g. `test-<helperFn>.R`, `test-<Module>Init.R`.

Read an existing test in the target module before writing a new one, to match its fixtures
and style. In LandR, `Biomass_core` is the richest reference (~21 test files).

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
    paths   = list(modulePath = "..", outputPath = tempdir())
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
                   paths = list(modulePath = "..", outputPath = tempdir()))
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
    paths   = list(modulePath = "..", outputPath = tempdir(), inputPath = tempdir())
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
`fireSenseUtils/tests/testthat/test-data.R` is an existing LandR example; `LandR` has no
suite yet.

## Running tests

- Module: source `tests/unitTests.R`, or `testthat::test_dir("<Module>/tests/testthat")`.
- Package: `devtools::test("<Package>")`.
- Run from a context where the module's `reqdPkgs` (or the package's dependencies) are
  installed; use `Require()` to load them.

### Running against unreleased dependencies

Modules and the packages they depend on usually change together, so a module's
`reqdPkgs` often carries a floor — `PredictiveEcology/LandR@development (>= 1.2.0.9024)`
— that the installed library does not meet yet. Do not install the development version
into a shared library to make the tests run. Put it in a scratch library and prepend
that:

```r
.libPaths(c("~/scratch-rlib", .libPaths()))
Require::Require("PredictiveEcology/LandR@development", require = FALSE)
```

Delete the scratch library when the work is done. Two further points when running a
module outside `simInit()`'s normal path:

- **`spades.useRequire = FALSE` does not attach `reqdPkgs`.** It only stops SpaDES from
  installing them. Module code that calls a package unqualified (e.g. `fpCompare`'s
  `%>>%`) then fails. Attach what the module needs explicitly.
- **`pkgload::load_all()` is not equivalent to an installed package.** It puts a
  package's own imports on the search path, so a namespace problem in the code under
  test can resolve anyway and the test passes locally while CI fails.

### What CI runs

A module PR is gated by `testthat-module`, which does not source the module: it
converts it to an R package with `SpaDES.core::convertToPackage()` and runs
`testthat::test_local()` on that. Tests can therefore pass locally and fail on GitHub
for packaging reasons that have nothing to do with the assertions. A module with no
`tests/testthat/test*.R` passes and reports it in the job summary, so a green check is
not by itself evidence that tests ran. See `spades-module-ci`.

Two habits that keep the suite honest under that conversion:

- **Do not rely on another test file having attached a package.** `testthat` runs files
  alphabetically, and a `library(data.table)` at the top of one file silently supplies
  it to every file after. Check a suspect file on its own.
- **Do not add `library()` calls to a test purely to make it pass.** If the module's own
  namespace cannot find a function, that is the defect.

<!--Note to Ceres: request input from Eliot and Alex.-->
