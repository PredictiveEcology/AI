# Reproducing a testthat-module failure locally

The `testthat-module` job does three things: install the dependencies, convert the
module to a package, run `testthat::test_local()` on the result. A local replica has to
match on one point that is easy to get wrong.

## The one thing that matters

**Use an *installed* SpaDES.core, not `pkgload::load_all()`.** `load_all()` places a
package's own imports on the search path, so a module with an unresolved import resolves
it anyway and the test passes. A local replica built on a `load_all()`ed SpaDES.core will
disagree with CI for reasons that have nothing to do with the module.

Install SpaDES.core (and any other dependency under development) into a scratch library,
and prepend that library. Never install into a shared library to chase a CI failure.

## The replica

```r
## ci_local.R -- run from inside the module directory
.libPaths(c("~/scratch-rlib-ci", .libPaths()))
library(SpaDES.core)                       # installed, not load_all()ed

m <- basename(getwd())                     # module name == directory name
pkg <- suppressMessages(
  SpaDES.core::convertToPackage(m, path = "..", buildDocuments = TRUE,
                                destinationPath = tempfile("testthat-module"))
)
res <- testthat::test_local(pkg, reporter = "silent", stop_on_failure = FALSE)
print(res)
```

Run it with `Rscript ci_local.R`. `buildDocuments = TRUE` is required: it is what
generates the `NAMESPACE` whose imports are under test.

## Setting up the scratch library

```r
.libPaths(c("~/scratch-rlib-ci", .libPaths()))
Require::Require("PredictiveEcology/SpaDES.core@development", require = FALSE)
```

Add whichever dependency packages the module's `reqdPkgs` floors demand. This library is
disposable; delete it when the investigation ends.

## Checking one test file

An import defect can be masked by an earlier test file that attaches the package
itself. To check a single file against the converted package:

```r
testthat::test_file(file.path(pkg, "tests", "testthat", "test-<name>.R"))
```

## What this replica does not cover

System dependencies, the spatial stack, and download behaviour. If the CI failure is in
an install step rather than in `Run tests`, read the log instead of reproducing it — the
cause is usually a version floor or a transient download.
