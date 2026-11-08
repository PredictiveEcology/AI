# Diagnosing a cache miss or a stale hit

## Unexpected miss (an expensive step re-ran)

1. **Turn on `showSimilar` for the next run.** `options(reproducible.showSimilar = TRUE)`
   (or the module parameter `.showSimilar = TRUE`) makes a miss report the most similar
   entry and which parts of the key differ. `reproducible.showSimilarDepth` only tunes
   that report; it does nothing while `showSimilar` is off.
2. **Compare `preDigest` tags when the run is over.** Each entry stores one `preDigest`
   tag per key component (`<name>:<digest>`). Find the new entry and the one you
   expected it to hit with `showCache(cachePath, userTags = c("module:<Module>", "eventType:<event>"))`,
   then compare their `preDigest` rows **by component name**. The names that differ
   are the cause. Two different comparisons can disagree: `showSimilar` compares a
   stored entry with the live call, while a tag diff compares two stored entries.
3. **Check code before metadata.** The usual cause is a changed module function. Parse
   the module at both commits and compare function bodies. A `reqdPkgs` floor change
   or a parameter change is the next suspect.
4. **Check the event queue and outputs table.** Both are part of later events' keys, so
   one changed early event can make every later event miss.

A diagnostic script that only reads the cache can still change it: on reproducible
before 3.2.1.9046, setting `reproducible.cacheSaveFormat` to a format other than the
entry's converted the entry on disk and dropped its tags. Leave that option unset in
diagnostic scripts.

## Stale hit (the run used an old result)

Ask what the result depends on that the key does not hold:

- An object the event reads but does not declare with `expectsInput()`.
- A function in another package that the cached call reaches (needs `.cacheExtra`).
- A parameter marked `cacheKey = FALSE` or in `omitParams` that really does change the
  result.
- An input that another module changes during the run, while your code assumes it is
  fixed.

## Tests that pin cache behaviour

Cache bugs pass on the first run, because the first run is a miss. A useful test runs
the same thing twice with caching on and changes one thing in between:

```r
test_that("init output is current after a cached rerun", {
  withr::local_options(reproducible.cachePath = withr::local_tempdir())
  run <- function(val) {
    sim <- simInit(times = list(start = 0, end = 1), modules = "<Module>",
                   params = list(`<Module>` = list(.useCache = c(".inputObjects", "<event>"))),
                   objects = list(x = val), paths = list(modulePath = ".."))
    spades(sim)
  }
  a <- run(1)
  b <- run(2)                           # only `x` changed
  expect_false(identical(a$result, b$result))
  c <- run(2)                           # identical call: should be a hit
  expect_identical(b$result, c$result)
})
```

Check that the test fails when the defect is put back (remove the `expectsInput()`, or
the `.cacheExtra`). A test that passes both ways pins nothing.

A static check also helps. `fireSense_dataPrepFit`'s `test-declaredIsUsed.R` checks that
every declared parameter and input is read and every declared output is assigned; the
reverse check (every `sim$x <-` in `.inputObjects` is a declared input) caught two
undeclared objects there.
