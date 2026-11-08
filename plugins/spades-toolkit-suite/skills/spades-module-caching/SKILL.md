---
name: spades-module-caching
description: How SpaDES module caching really behaves, for module developers — what an event or .inputObjects cache key digests (declared inputs, mod$ contents, module functions, parameters, reqdPkgs; not package function bodies, not undeclared objects), what a cache hit restores, and the traps that give stale results or needless re-runs. Covers .cacheExtra for callee functions, declaring every object an event reads as expectsInput, defineParameter(cacheKey = FALSE), .useCacheArgs omitParams, .neverCache, spades.cacheKeyReachable, persisting terra objects (Cache or writeRaster, never saveRDS), not assuming inputs stay fixed across simulated years, and how to diagnose a miss or a stale hit. Use when adding Cache() to module code, when a cached run returns old results or re-runs unexpectedly, when changing module metadata or reqdPkgs, or when designing a speed-up that reuses results across years.
metadata:
  ecosystem: SpaDES
  version: "0.1"
---

# SpaDES module caching

`spades-module-development` says to use `Cache()` and not to cache stochastic events.
This skill covers what happens after that: what the key holds, what a hit brings back,
and how a cached module silently returns the wrong answer.

The two failure modes are opposite, and both are silent:

- **Stale hit.** Something the result depends on is not in the key. The run uses an
  old result and nothing says so.
- **Needless miss.** Something irrelevant is in the key. Expensive steps re-run after
  a change that could not affect them.

A stale hit is worse. When in doubt, keep a thing in the key.

## What an event's cache key holds

On current SpaDES.core development (details and line numbers in
`references/event-cache-key.md`):

| In the key | Not in the key |
|---|---|
| Every object the module declares with `expectsInput()` that exists in `sim` | Objects the event reads but does not declare |
| Every `mod$` object that exists when the event is called | Bodies of package functions the module calls |
| The module's own functions (`<Module>.R` and `R/`) | The module `version` (since SpaDES.core 3.2.1.9043) |
| The module's parameters, except `cacheKey = FALSE` ones | `.useCache`, `.useCacheArgs`, `.useCloud`, `.neverCache` |
| Metadata: inputs/outputs tables, parameters, `reqdPkgs`, `childModules`, `timeunit`, ... | |

A hit restores the module's declared outputs that the event changed, plus its `mod`.

## Read first

1. **An object an event reads must be declared with `expectsInput()`.**
   Symptom: a run uses data older than what it just read or computed. Cause: an
   uncached step (e.g. `init`) sets `sim$x`, a later cached event uses `x` and also
   writes it. `x` is `createsOutput` only, so it is not in the later event's key, and
   the hit restores the old `x`. Fix: declare `x` with `expectsInput()` too. Declaring
   it in both lists is normal for an object a module both reads and writes.

2. **`mod$` values need no extra handling.** Everything in `mod` when the event starts
   is in the key, as `<module>:<name>`. Do not move a `mod$` value to `sim$` or add it
   to `.cacheExtra` to make it count.

3. **A `Cache()` call digests the function you call, not the functions it calls.**
   `Cache(outer(x))` stays a hit after `pkg::inner()` changes. When the result depends
   on a callee in another package, pass that function itself:
   `outer(x) |> Cache(.cacheExtra = list(pkg::inner))`. Do not use
   `packageVersion("pkg")`: it changes on every merge, so unrelated changes re-run
   expensive steps. Pin this with a test (a template is in
   `references/event-cache-key.md`).

4. **Raising a `reqdPkgs` floor re-runs every cached event of the module once.** The
   `reqdPkgs` strings are in the key. That is often what you want after a package fix,
   since package bodies are not. But it also re-runs steps the fix did not touch, and
   modules downstream miss when the rebuilt objects differ. Say so in the PR.

5. **Never `saveRDS()` a terra object**, wrapped or not. A plain `SpatRaster` comes back
   with "external pointer is not valid"; `saveRDS(terra::wrap(r))` works but is slower
   and less portable. To keep a result between sessions, call the function through
   `Cache()` (it wraps and unwraps for you) or use `terra::writeRaster()` /
   `writeVector()`. First ask whether saving is needed at all.

6. **Do not assume an input stays the same across simulated years.** Land cover, a
   flammability map or a template raster may be changed by another module, even if no
   module in your project does it today. A speed-up that computes something once per
   run from such an input will serve stale results when such a module is added. Key
   any reuse across years on the inputs actually passed to that call, or make the
   per-call work cheaper. Add a test where the input changes between calls.

## Keeping a parameter out of the key

Every parameter is in every key of its module by default. Two ways to narrow that
(SpaDES.core >= 3.2.1.9047; set that floor in `reqdPkgs` if you use them):

- `defineParameter(..., cacheKey = FALSE)` — for a parameter that changes how the module
  works, not what it returns: core counts, host lists. After a hit it keeps the current
  value, not the cached one.
- `.useCacheArgs = list(<event> = list(omitParams = c(".runName", ".rep")))` — for a
  parameter that labels a run and changes some events' results but not this one's.

`.neverCache = c("<event>")` stops an event from being cached whatever `.useCache`
says. Use it for events that run for their side effects (writing files, uploading).

`options(spades.cacheKeyReachable = TRUE)` narrows each event key to the parameters and
module functions that event's code reaches. It defaults to `FALSE` and is experimental:
the static analysis can miss `get()`, `do.call("f")` and method dispatch, and a wrong
narrowing returns a stale result. Do not turn it on in a module's defaults; if you trial
it, compare against full-key runs.

## `.inputObjects`

- Its key holds the declared inputs that already exist in `sim`, the module's
  parameters and metadata, and the module functions `.inputObjects` reaches.
- **On SpaDES.core < 3.2.1.9020, a cached `.inputObjects` restored only objects
  declared with `expectsInput()`.** An object it set but declared only as
  `createsOutput()` vanished on the second run. Symptom: the first run works, a rerun
  fails in another module with an object that is `NULL`. Fixed in 3.2.1.9020; on older
  versions, declare the object as `expectsInput()` too.
- Test module hand-offs with caching on, and run twice. The first run is a miss and
  proves nothing about what a hit restores.

## Diagnosing

Do not guess why a cache missed or hit. Compare what was digested:
`references/diagnosing-cache.md` has the steps (`showSimilar`, comparing `preDigest`
tags, a hit/miss test). Before blaming metadata for a miss, check whether a module
function body changed; that is the usual cause.

## Reference files

| File | Covers |
|---|---|
| `references/event-cache-key.md` | what the event and `.inputObjects` keys hold, with SpaDES.core source lines and the version history; the `.cacheExtra` test template |
| `references/diagnosing-cache.md` | finding why an entry missed or hit, and tests that pin cache behaviour |

## Related skills

- `spades-module-contract` — metadata rules (`reqdPkgs`, parameters, `.globals`) that
  this skill relies on.
- `spades-module-development` — when to cache at all; stochastic events.
- `testing` — module test layout.
