---
name: spades-testing
description: Writing and running tests for SpaDES modules and toolkit packages — both unit tests (a single module, event, or helper function) and integration tests (multi-module workflows). Covers the tests/unitTests.R + tests/testthat/ layout, building minimal in-memory rasters and data.tables, calling simInit()/spades(), reaching module-internal functions, and asserting on the returned simList. Use when the user asks to add, fix, or run tests for a module, simulation, or toolkit package.
metadata:
  ecosystem: SpaDES
  version: "1.0"
---

# SpaDES testing

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
and style.

## Building minimal inputs

SpaDES tests construct small, deterministic objects in memory: tiny raster layers and
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

## Toolkit-package tests

The toolkit packages themselves (`SpaDES.core`, `SpaDES.tools`, `reproducible`, `Require`,
etc.) use the standard testthat package layout (`tests/testthat/` + `tests/testthat.R`).
Run them via the devtools workflow — see `spades-package-development` — e.g.
`devtools::test("<Package>")`.

## Running tests

- Module: source `tests/unitTests.R`, or `testthat::test_dir("<Module>/tests/testthat")`.
- Package: `devtools::test("<Package>")`.
- Always run from a context where the module's `reqdPkgs` (or the package's dependencies)
  are installed; use `Require()` to load them.

<!--Note to Ceres: request input from Eliot and Alex.-->