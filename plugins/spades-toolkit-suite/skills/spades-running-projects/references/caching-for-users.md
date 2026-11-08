# Caching, as someone who runs SpaDES projects

You do not write the `Cache()` calls, but you live with them: a run that recomputes
for hours when you expected a hit, or one that hits when you expected your fix to
take effect. This file is about reading that behaviour. Fixing a module's cache key
is module work (`spades-module-development`).

## What makes a cached event rerun

What an event cache key holds, and what a hit restores, is in `spades-module-caching`
(`references/event-cache-key.md`). The two things that surprise people running projects:

- **A `reqdPkgs` change alone makes every cached event of that module miss**, and
  downstream modules can miss too when the rebuilt objects differ. Updating all modules
  to their latest commits between two stages of a campaign has silently rebuilt the whole
  first stage before the second could start. Before such an update, list which modules
  changed `reqdPkgs` and expect their events to rerun. (Before SpaDES.core 3.2.1.9043 a
  `version` bump did the same.)
- **A fix inside a function that the cached code calls in another package does not
  invalidate the cached result.** If a package fix "did not take effect", this is the
  first suspect. Clearing that one cache entry is the user-side workaround; the module
  fix is `.cacheExtra`.

## Diagnosing a miss or an unexpected hit

Do not guess from what changed in git: compare the keys, as in
`spades-module-caching/references/diagnosing-cache.md`.

Symptoms that point at the cache, not the model:

- A run uses data older than what it just read or downloaded: a cached event restored
  an older value of an object.
- A run works the first time and fails on the rerun with an object missing: the
  object came from a cache hit that did not restore it.

Both are module declaration defects (recent SpaDES.core fixes the second). Report
them to the module, with the object name.

## Cache file format

`options(reproducible.cacheSaveFormat)` chooses `"rds"` or `"qs2"` for new entries.
Since reproducible 3.2.1.9046 its default is unset, meaning "read each entry in the
format it is in". Setting it to a format that differs from an existing entry's
converts that entry on disk when it is loaded; before 3.2.1.9046 the conversion also
dropped the entry's tags, so `showCache()` could no longer find it by function name.
In diagnostic scripts that read a shared cache, leave it unset.

## terra scratch files

terra writes temporary rasters as `spat_<hash>_<pid>_*.tif` in its temp directory
(`terraOptions(tempdir = )`). The PID says which process wrote the file, not which
process uses it. A raster restored from the cache, or memoised in another job, can
point at a file written by a process that has since exited. Deleting those files
because their PID is dead has broken every running job within minutes, with

```
[readStart] file does not exist: .../spat_..._<deadPID>_...tif
```

or opaque errors from cluster workers. This was still true after reproducible fixes
aimed at it. Clean terra scratch only when no job that can read the shared cache is
running. If the disk is full, decide by hand what to move or which cache entries to
clear.

## Rasters in RAM

terra's default is `todisk = FALSE`: any result that fits within `memmax x memfrac`
stays in RAM, and a cache entry saved that way restores into RAM again. `prepInputs()`
writes to disk only inside its own steps. Workers started by `experiment*()` (recent
SpaDES.project) set `terraOptions(todisk = TRUE)`; a run started any other way needs
it in `global.R`, e.g. in `setupProject(sideEffects = )`. A run holding many GB of
rasters in RAM: check `terraOptions()$todisk` first.

## Keeping results between scripts

Use `Cache()` or `terra::writeRaster()`, never `saveRDS()` of a terra object (details in
`spades-module-caching`).

## Stray `<name>_1.tif` files

A `*_1.tif` beside a raster in an output folder, appearing right after a cache save,
is the signature of a reproducible memoise bug fixed in 3.2.1.9050: the simulation
used a copy, and two jobs sharing the folder overwrote each other's copy. Upgrade
reproducible rather than working around it.
