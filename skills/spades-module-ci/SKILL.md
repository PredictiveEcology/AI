---
name: spades-module-ci
description: Getting a SpaDES module through continuous integration and into a merged PR — the three shared reusable workflows (testthat-module, render-module-rmd, pkgdown-module) from PredictiveEcology/actions, how convertToPackage() turns a module into an R package for testing, the packaging traps that pass locally and fail in CI (@importFrom suppressing the blanket @import, Collate, helper naming), reqdPkgs version floors that redden a module until its dependency package merges, and how to reproduce a CI failure on your own machine. Use when a module's CI is red, when adding CI to a module, when a module test passes locally but not on GitHub, or when preparing a module PR for review. For writing the tests themselves use testing; for module structure use spades-module-anatomy.
metadata:
  ecosystem: SpaDES
  version: "1.0"
---

# SpaDES module CI

Authoring a module and *landing* a module are different jobs. This skill covers the
second: what runs on a module PR, what breaks, and how to tell a real defect from a
stale dependency.

## The three shared workflows

Module repos do not write their own CI. Each workflow in the module repo is a thin
caller that names the module and delegates to a reusable workflow in
[`PredictiveEcology/actions`](https://github.com/PredictiveEcology/actions), referenced
at `@main`. Copy the caller from `examples/` in that repo.

| Workflow | What it does | Trigger |
|---|---|---|
| `testthat-module` | Converts the module to a package and runs `tests/testthat/`; optional coverage summary | PR + push to `main`/`master`/`development`, and changes to `<Module>.R`, `R/**`, `tests/**` |
| `render-module-rmd` | Renders `<Module>.Rmd` and commits the result back | PR + push, and changes to `<Module>.R`/`.Rmd` |
| `pkgdown-module` | Builds the module's pkgdown site and deploys to `gh-pages` | PR + push to `development` |

Two things about permissions. `render-module-rmd` and `pkgdown-module` need
`permissions: contents: write` **in the caller**, because a called workflow can only
reduce what the caller grants. `testthat-module` deliberately has no commit job and
needs no write scope.

**Never hand-patch a per-repo copy of one of these.** Divergent copies are how a bad
pin survives across a dozen repos. If the shared workflow is wrong, fix it in
`actions`, once.

## The module-as-package model

`testthat-module` does not source the module. It calls:

```r
pkg <- SpaDES.core::convertToPackage(m, path = "..", buildDocuments = TRUE,
                                     destinationPath = tempfile("testthat-module"))
testthat::test_local(pkg)
```

So during testing your module **is an R package**: `R/*.R` become package code with a
real `NAMESPACE`, and `reqdPkgs` become `Imports` in a generated `DESCRIPTION`. Almost
every "passes locally, fails in CI" case traces to that conversion. The traps are in
`references/packaging-traps.md`; the one that costs the most time is first below.

## Read first

1. **An explicit `@importFrom` for a package cancels the blanket `@import` for that
   whole package.** `convertToPackage()` writes `#' @import <pkg>` for each `reqdPkgs`
   entry, then drops any package that already appears in an `@importFrom`
   (`SpaDES.core/R/convertToPackage.R:352-360`). This is documented, intended
   behaviour, and it is sharp: add one `@importFrom data.table set` anywhere in `R/`
   and every *other* data.table function in the module becomes unresolved. The symptom
   is `could not find function "data.table"` in CI only. `:=` keeps working, which
   makes it look impossible — data.table's `cedta()` accepts any `importFrom` from
   your namespace. Fix by naming what you use: `@importFrom data.table data.table`.

2. **`pkgload::load_all()` hides that failure, so a local test run is not a CI run.**
   `load_all()` puts a package's own imports on the search path. If you develop
   against a `load_all()`ed SpaDES.core, unresolved imports resolve anyway. Reproduce
   CI with an *installed* SpaDES.core in a scratch library — recipe in
   `references/reproducing-module-ci.md`.

3. **A new `R/*.R` file must be in `Collate`.** `R CMD INSTALL` refuses a package with
   an R file the `Collate` field does not list. Adding a helper file without updating
   `DESCRIPTION` fails CI and nothing else.

4. **A module helper may not be named with the module's own prefix.** SpaDES rejects
   it. Rename the helper.

5. **`[skip-ci]` in the head commit message skips the whole job**, and a module with
   no `tests/testthat/test*.R` *passes* and says so in the job summary. A green check
   is not evidence that tests ran; read the summary.

6. **Red CI right after a dependency merges is usually a stale run, not a defect.**
   `reqdPkgs` pins like `PredictiveEcology/LandR@development (>= 1.2.0.9024)` are
   version floors. A run that started before that LandR version existed installs the
   older one and fails with "the packages ... are required". Re-run the job before
   investigating anything.

## When a module PR is red

Work in this order; each step is cheap and rules out a whole class.

1. Read the failing step's log for "the packages ... are required". If present, the
   dependency floor is unmet — merge or wait for the dependency package, then re-run.
2. Re-run the job once. Transient download failures are real and common.
3. Check whether the failure is in `Run tests` or earlier. Earlier means packaging
   (imports, `Collate`, documents), not your test.
4. Only then reproduce locally, against an installed SpaDES.core
   (`references/reproducing-module-ci.md`).

A test file that calls `library(data.table)` itself will mask an import defect, and
`testthat` runs files alphabetically — so a module can be broken while its PR is green
because an earlier test file attached the package. Do not treat "other modules' tests
pass" as evidence.

## Version floors and the merge order

A module and the package it depends on almost always change together, and the module
cannot go green until the package side is merged. The working order is: merge the
package PR to `development`, wait for its version to be installable, then re-run the
module PRs. Raising a floor in `reqdPkgs` before the package merges reddens every
module that carries it — expected, not a regression.

## Reference files

| File | Covers |
|---|---|
| `references/packaging-traps.md` | the full `convertToPackage()` trap list with symptoms and fixes |
| `references/reproducing-module-ci.md` | a local replica of the `testthat-module` job |

## Related skills

- `testing` — writing the tests this workflow runs.
- `spades-module-anatomy` — the module file layout these workflows consume.
- `landr-package-maintenance` / `spades-package-development` — the *package* side of a
  paired module+package change.
