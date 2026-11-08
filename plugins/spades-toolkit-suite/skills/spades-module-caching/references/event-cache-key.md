# What a SpaDES cache key holds

Line numbers are for SpaDES.core `development` at 3.2.1.9058. Read the code when your
version differs: these rules have changed several times in 2026.

## Event key (`.runEvent()`, `R/simulation-spades.R`)

`.runEvent()` builds two lists before calling `Cache()` (`:1559-1572`):

- `moduleSpecificObjects`, the `.objects` that are digested:
  - functions in `sim` whose names carry the module's name;
  - every function in the module's namespace environment (`<module>:<fn>`), i.e. the
    code in `<Module>.R` and `R/`;
  - every object in the module's `mod` environment (`<module>:<name>`);
  - every `expectsInput()` object name.
- `moduleSpecificOutputObjects`, what a hit restores: the module's `createsOutput()`
  objects, its `.mods` and `mod` entries.

The parameters go in through `classOptionsForCache()`, minus `.paramsNotCachedOn()`
(`cacheKey = FALSE` parameters, `omitParams`, and the fixed list `.useCache`,
`.useCacheArgs`, `.useCloud`, `.neverCache`; `R/helpers.R:480`). The metadata slots go in
as `dependsSlots = metadataToDigest` (`R/simulation-simInit.R:2570-2571`):

```r
otherDependsToDig <- c("childModules", "loadOrder", "reqdPkgs", "spatialExtent", "timeframe", "timeunit")
metadataToDigest <- c("inputObjects", "outputObjects", "parameters", otherDependsToDig)
```

A hit restores only the declared outputs that the event changed when the entry was
saved (the `eventObjectsChanged` tag, written since 3.2.1.9051).

### Consequences

- An object the event reads but does not declare is invisible to the key. If the event
  also writes it, a hit replaces the live value with the cached one.
- A package function is not digested, even when the event calls it. A package fix does
  not invalidate events; a `reqdPkgs` floor change does (the strings are digested).
- Editing any module function re-runs every cached event of that module, unless
  `spades.cacheKeyReachable = TRUE`.

## `.inputObjects` key (`R/simulation-simInit.R:1740-1860`)

- Digests the module functions reachable from `.inputObjects` (`.fnsReachableFrom()`,
  `:1763`, since 3.1.2.9007), plus declared inputs that are already in `sim`.
- Parameters and metadata as for events, without the `outputObjects` slot.
- A hit restores declared inputs and declared outputs (`:1751`, since 3.2.1.9020).
  Before that it restored declared inputs only.

## Version history that changes behaviour

| SpaDES.core | Change |
|---|---|
| 3.1.2.9007 | `.inputObjects` key includes the module helpers it reaches |
| 3.2.1.9020 | cached `.inputObjects` restores its declared outputs too |
| 3.2.1.9030 | `options(spades.reqdPkgsAttach = FALSE)` available |
| 3.2.1.9035 | `.globals` sets only universal dot parameters in modules that do not declare them |
| 3.2.1.9043 | module `version` no longer in any cache key; existing entries miss once |
| 3.2.1.9047 | `defineParameter(cacheKey = )`, `.useCacheArgs` `omitParams` |
| 3.2.1.9048 | `options(spades.cacheKeyReachable)`, default `FALSE` |

Why `version` left the key: a code change is already in the key through the function
bodies, so a version bump with no code change only forced re-runs.

Why the key does not digest the source of called package functions: the key is
recomputed on every cache read, and memoised event reads happen many times a second.
Parsing and digesting called functions measured 0.3 to 1.2 s per module, which would
make reads several times slower. Static analysis also misses `get()`, `do.call("f")` and
S3/S4 dispatch, so it would trade false misses for stale hits.

## `.cacheExtra` for callee functions

`reproducible::Cache()` digests the called function and its arguments. It does not
follow the functions that function calls. When a cached result depends on a function in
another package, pass the function object:

```r
## makeLCC() is the function you call; its result depends on otherPkg::classify()
lcc <- makeLCC(rasterToMatch, year) |>
  Cache(.cacheExtra = list(otherPkg::classify))
```

Do not pass `packageVersion()`: development versions bump on every merge, so every
unrelated merge would recompute the step.

Test that pins this, adapted from `fireSense_dataPrepFit`
(`tests/testthat/test-cacheExtraInnerFunction.R`):

```r
test_that("a function in .cacheExtra makes Cache re-run when that function's code changes", {
  withr::local_options(reproducible.cachePath = withr::local_tempdir(),
                       reproducible.verbose = -2)
  inner <- function(x) x + 1
  outer <- function(x) inner(x)
  expect_identical(as.numeric(reproducible::Cache(outer(1))), 2)
  expect_identical(as.numeric(reproducible::Cache(outer(1), .cacheExtra = list(inner))), 2)
  inner <- function(x) x + 100
  expect_identical(as.numeric(reproducible::Cache(outer(1))), 2)      # stale without it
  expect_identical(as.numeric(reproducible::Cache(outer(1), .cacheExtra = list(inner))), 101)
})
```
