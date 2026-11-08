---
name: spades-module-contract
description: The rules a SpaDES module's metadata and code must keep so that it works for anyone who runs it, not only in the project where it was written — reqdPkgs lists every package the code uses (never pkg:: as a substitute), version floors on @development, a module reads only parameters it defines (.globals is a user shortcut, never read by a module), modelling settings live in module parameters rather than run scripts, every figure goes through Plots(), verbosity and plotting never cause computation, parent modules and how childModules entries choose a branch or release, data.table subsetting traps in module tests, and when the module version is bumped. Use when writing or reviewing module code or metadata, adding a dependency, adding a parameter or figure, building a parent module, or when a module works in one project and fails in another. For file layout use spades-module-anatomy; for caching use spades-module-caching; for CI use spades-module-ci.
metadata:
  ecosystem: SpaDES
  version: "0.1"
---

# SpaDES module contract

A module is used by people who have not read its code. Its metadata is the whole
contract: the packages it needs, the parameters it reads, the objects it reads and
writes. Code that works only because some other module or the run script happens to
supply something breaks the first time the module runs somewhere else.

## Packages

1. **`reqdPkgs` lists every package the module's code uses**, whether called as
   `pkg::f()` or unqualified. When a gap is found, add the package to `reqdPkgs`. Do not
   rewrite calls as `pkg::f()` to dodge it: `pkg::` still needs the package installed,
   and only `reqdPkgs` makes that happen.
   Symptom of a gap: `could not find function "n"` in one project but not another.
   The module was relying on a package another module attached. With
   `options(spades.reqdPkgsAttach = FALSE)` (SpaDES.core >= 3.2.1.9030) each module
   sees only its own `reqdPkgs`, so running the module's tests under that option finds
   gaps.

2. **A module that needs a newer package states a floor on its development branch:**
   `"PredictiveEcology/reproducible@development (>= 3.2.1.9025)"`. Never name a feature
   branch; it disappears after merge. The floor may only name a version that already
   exists on that branch. A bare `@development` does not upgrade a package that is
   already installed; only the floor does.

3. **Raising a floor re-runs the module's cached events once** (the `reqdPkgs` strings
   are in the key; see `spades-module-caching`). It also makes the next project setup
   resolve packages again, which can take minutes.

## Parameters

4. **A module reads only parameters it defines with `defineParameter()`.** Reading
   `P(sim)$.studyAreaName` without defining it is a bug, even if a run sets it. Every
   parameter needs a working default.

5. **A module never calls `globals()` or reads `.globals`.** `params$.globals` is a user
   shortcut: "set this named parameter, in every module that defines it, to this
   value". There is no global parameter in SpaDES; that would break modularity. In
   docs, say "the user may set it in `.globals`", never "it comes from `.globals`".
   Since SpaDES.core 3.2.1.9035, `.globals` sets a dot parameter in a module that does
   not declare it only for `.plots`, `.seed`, `.showSimilar`, `.useCache` and
   `.useCacheArgs`.

6. **Give shared parameters one name across modules** (`.studyAreaName`, not
   `studyAreaName` in one and `.studyAreaName` in another), so one `.globals` entry can
   set them all.

7. **Modelling choices go into the module, not the run script.** Bounds, link
   functions, likelihood weights, covariate handling: if an experiment needs one the
   module lacks, add it to the module as a parameter (PR) first. A run script only sets
   parameters. Otherwise the experiment tests something the module does not do, and its
   results cannot be carried into production runs.

8. **Analysis that produces reported numbers or figures belongs in a module**, so
   someone without your scripts can rerun it. Only assembling the final document or page
   may live outside.

## Figures and verbosity

9. **Every figure goes through `SpaDES.core::Plots()`**, never a direct `ggsave()`,
   `png()` or `print()`. `Plots()` reads the module's `.plots` parameter, so the user
   chooses screen, PNG, both or nothing, and files land under `figurePath(sim)`. Shape
   the plotting function for it: data first, returns a ggplot. Put it in the package
   or the module's `R/`.

10. **A verbosity or plotting setting never makes code run.** If a block is skipped
    because the result does not need it, it stays skipped at any `verbose` level and
    with plotting on. Do not write `if (needed || verbose > 1)`. Drop the log lines
    that would have used it instead.

## Parent modules

A parent module has `childModules` and no events of its own. Rules for how children are
fetched, nesting, and releases are in `references/parent-modules.md`. In short: a plain
child name follows the parent's GitHub account and branch, `owner/repo@branch` is used
as written, and a user's own top-level module entry wins.

## Module tests

11. **Do not subset data.tables with `DT[0]` or `DT[col %in% x]` in a test's own frame.**
    `[.data.table` uses its special syntax only for callers it considers data.table
    aware (`cedta()`). A test run with `testthat::test_file()` from the global
    environment is aware; the same test inside the converted module package (CI,
    `R CMD check`) is not, so `[.data.frame` runs: `DT[0]` selects zero columns, and
    `DT[col %in% x]` fails with `object 'col' not found`. Use
    `DT[integer(0), , drop = FALSE]` and `DT[DT$col %in% x, , drop = FALSE]`, which
    behave the same both ways. A local pass proves nothing here.

12. **Pin the metadata contract in a test.** A `test-metadata.R` that checks the names
    and classes of inputs, outputs, parameters and defaults makes a rename fail loudly.
    A second check that every declared parameter and input is read, and every declared
    output is written, catches stale metadata (example:
    `fireSense_dataPrepFit/tests/testthat/test-declaredIsUsed.R`).

## Versions (PredictiveEcology convention)

13. **A PR does not change `version`.** NEWS bullets go under one development heading.
    The version is bumped once, on the base branch, right after each merge. A bump
    inside a PR makes every pair of open PRs conflict, and a merge with no bump leaves
    a version that dependent floors cannot tell apart from the last one.

14. **A PR that needs another unmerged PR says so** with a `Depends-on: owner/repo#N`
    line, and is not a draft; the shared CI actions install that PR before testing.

## Reference files

| File | Covers |
|---|---|
| `references/parent-modules.md` | `childModules` entry forms, branch and release resolution, nesting, what a parent cannot do |

## Related skills

- `spades-module-anatomy` — where these things live in the module file.
- `spades-module-caching` — how metadata enters cache keys.
- `spades-module-ci` — `convertToPackage()` and import traps in CI.
- `testing` — module test layout.
